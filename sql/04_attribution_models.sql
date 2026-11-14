-- ============================================================================
-- SCRIPT: 04_attribution_models.sql
-- PROJECT: Grito Labs Multi-Channel Marketing Analytics & Attribution Framework
-- PURPOSE: Implement the 5 Rule-Based Multi-Touch Attribution Models in pure SQL:
--          1. First-Touch Attribution (FTA)
--          2. Last-Touch Attribution (LTA)
--          3. Linear Attribution
--          4. Time-Decay Attribution (7-Day Half-Life: weight = 2^(-days/7))
--          5. Position-Based / U-Shaped Attribution (40% First, 40% Last, 20% Middle)
-- ENGINE: ANSI SQL (DuckDB / SQLite / PostgreSQL / MySQL compatible)
--
-- BUSINESS QUESTION ANSWERED:
-- How does channel credit, attributed revenue, and ROAS change when moving
-- from myopic single-touch models to multi-touch and decay models?
-- ============================================================================

-- ----------------------------------------------------------------------------
-- STEP 1: Compute Weights per Touchpoint for All 5 Rule-Based Models
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS v_touchpoint_attribution_weights;

CREATE VIEW v_touchpoint_attribution_weights AS
WITH touchpoint_base AS (
    SELECT 
        touchpoint_id,
        customer_id,
        conversion_id,
        touchpoint_time,
        conversion_time,
        channel_id,
        channel_name,
        campaign_id,
        conversion_revenue,
        days_before_conversion,
        touch_rank_asc,
        touch_rank_desc,
        total_journey_touches,
        
        -- Time-decay raw weight: 2^(-days / 7.0) = exp(-ln(2) * days / 7.0)
        -- Since SQLite supports EXP, LN, or POWER:
        -- POWER(2.0, - (days_before_conversion / 7.0))
        POWER(0.5, (days_before_conversion / 7.0)) AS time_decay_raw_weight
    FROM v_valid_customer_journeys
),
journey_decay_totals AS (
    SELECT 
        touchpoint_base.*,
        SUM(time_decay_raw_weight) OVER (PARTITION BY conversion_id) AS total_decay_weight_per_journey
    FROM touchpoint_base
)
SELECT 
    touchpoint_id,
    customer_id,
    conversion_id,
    touchpoint_time,
    conversion_time,
    channel_id,
    channel_name,
    campaign_id,
    conversion_revenue,
    total_journey_touches,
    touch_rank_asc,
    touch_rank_desc,
    
    -- 1. First-Touch Weight
    CASE WHEN touch_rank_asc = 1 THEN 1.0 ELSE 0.0 END AS weight_first_touch,
    
    -- 2. Last-Touch Weight
    CASE WHEN touch_rank_desc = 1 THEN 1.0 ELSE 0.0 END AS weight_last_touch,
    
    -- 3. Linear Weight: 1.0 / N
    1.0 / CAST(total_journey_touches AS REAL) AS weight_linear,
    
    -- 4. Time-Decay Weight: Normalized
    time_decay_raw_weight / total_decay_weight_per_journey AS weight_time_decay,
    
    -- 5. Position-Based (U-Shaped) Weight:
    -- If 1 touch: 100%
    -- If 2 touches: 50% / 50%
    -- If 3+ touches: 40% first, 40% last, 20% split across (N - 2) middle touches
    CASE 
        WHEN total_journey_touches = 1 THEN 1.0
        WHEN total_journey_touches = 2 THEN 0.50
        ELSE 
            CASE 
                WHEN touch_rank_asc = 1 THEN 0.40
                WHEN touch_rank_desc = 1 THEN 0.40
                ELSE 0.20 / CAST(total_journey_touches - 2 AS REAL)
            END
    END AS weight_position_based
FROM journey_decay_totals;

-- ----------------------------------------------------------------------------
-- STEP 2: Channel-Level Comparison Matrix Across All Models
-- ----------------------------------------------------------------------------
WITH channel_spend AS (
    SELECT 
        s.channel_id,
        c.channel_name,
        SUM(s.spend) AS total_spend
    FROM fact_daily_spend s
    JOIN dim_channel c ON s.channel_id = c.channel_id
    GROUP BY s.channel_id, c.channel_name
),
channel_attributed_metrics AS (
    SELECT 
        w.channel_id,
        w.channel_name,
        
        -- Attributed Conversions
        ROUND(SUM(w.weight_first_touch), 2) AS conv_first_touch,
        ROUND(SUM(w.weight_last_touch), 2) AS conv_last_touch,
        ROUND(SUM(w.weight_linear), 2) AS conv_linear,
        ROUND(SUM(w.weight_time_decay), 2) AS conv_time_decay,
        ROUND(SUM(w.weight_position_based), 2) AS conv_position_based,
        
        -- Attributed Revenue
        ROUND(SUM(w.weight_first_touch * w.conversion_revenue), 2) AS rev_first_touch,
        ROUND(SUM(w.weight_last_touch * w.conversion_revenue), 2) AS rev_last_touch,
        ROUND(SUM(w.weight_linear * w.conversion_revenue), 2) AS rev_linear,
        ROUND(SUM(w.weight_time_decay * w.conversion_revenue), 2) AS rev_time_decay,
        ROUND(SUM(w.weight_position_based * w.conversion_revenue), 2) AS rev_position_based
    FROM v_touchpoint_attribution_weights w
    GROUP BY w.channel_id, w.channel_name
)
SELECT 
    m.channel_id,
    m.channel_name,
    ROUND(s.total_spend, 2) AS spend,
    
    -- Conversions by Model
    m.conv_first_touch,
    m.conv_last_touch,
    m.conv_linear,
    m.conv_time_decay,
    m.conv_position_based,
    
    -- Revenue by Model
    m.rev_first_touch,
    m.rev_last_touch,
    m.rev_linear,
    m.rev_time_decay,
    m.rev_position_based,
    
    -- ROAS Comparisons (Revenue / Spend)
    ROUND(m.rev_first_touch / NULLIF(s.total_spend, 0), 2) AS roas_first_touch,
    ROUND(m.rev_last_touch / NULLIF(s.total_spend, 0), 2) AS roas_last_touch,
    ROUND(m.rev_linear / NULLIF(s.total_spend, 0), 2) AS roas_linear,
    ROUND(m.rev_time_decay / NULLIF(s.total_spend, 0), 2) AS roas_time_decay,
    ROUND(m.rev_position_based / NULLIF(s.total_spend, 0), 2) AS roas_position_based,
    
    -- ROAS Delta: Position-Based vs Last-Touch (%)
    -- Shows how much Last-Touch overvalues or undervalues each channel
    ROUND((m.rev_position_based - m.rev_last_touch) / NULLIF(m.rev_last_touch, 0) * 100.0, 1) AS roas_shift_pct
FROM channel_attributed_metrics m
JOIN channel_spend s ON m.channel_id = s.channel_id
ORDER BY s.total_spend DESC;

-- ----------------------------------------------------------------------------
-- STEP 3: Automated Sanity & Integrity Validation Check
-- Purpose: Verify that the sum of attributed conversions and revenue for EACH
--          attribution model exactly reconciles to the ground truth total revenue.
-- ----------------------------------------------------------------------------
SELECT 
    'Ground Truth Conversions & Revenue' AS metric_type,
    COUNT(DISTINCT conversion_id) AS total_conversions,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM fact_conversions
WHERE conversion_cycle = 1

UNION ALL

SELECT 
    'First-Touch Model Sum' AS metric_type,
    ROUND(SUM(weight_first_touch), 2) AS total_conversions,
    ROUND(SUM(weight_first_touch * conversion_revenue), 2) AS total_revenue
FROM v_touchpoint_attribution_weights

UNION ALL

SELECT 
    'Last-Touch Model Sum' AS metric_type,
    ROUND(SUM(weight_last_touch), 2) AS total_conversions,
    ROUND(SUM(weight_last_touch * conversion_revenue), 2) AS total_revenue
FROM v_touchpoint_attribution_weights

UNION ALL

SELECT 
    'Linear Model Sum' AS metric_type,
    ROUND(SUM(weight_linear), 2) AS total_conversions,
    ROUND(SUM(weight_linear * conversion_revenue), 2) AS total_revenue
FROM v_touchpoint_attribution_weights

UNION ALL

SELECT 
    'Time-Decay Model Sum' AS metric_type,
    ROUND(SUM(weight_time_decay), 2) AS total_conversions,
    ROUND(SUM(weight_time_decay * conversion_revenue), 2) AS total_revenue
FROM v_touchpoint_attribution_weights

UNION ALL

SELECT 
    'Position-Based Model Sum' AS metric_type,
    ROUND(SUM(weight_position_based), 2) AS total_conversions,
    ROUND(SUM(weight_position_based * conversion_revenue), 2) AS total_revenue
FROM v_touchpoint_attribution_weights;
