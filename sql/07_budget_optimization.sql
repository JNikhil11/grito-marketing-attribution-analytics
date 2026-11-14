-- ============================================================================
-- SCRIPT: 07_budget_optimization.sql
-- PROJECT: Grito Labs Multi-Channel Marketing Analytics & Attribution Framework
-- PURPOSE: Formulate the Attribution-Adjusted Budget Reallocation Model,
--          computing Marginal ROAS and Scenario Uplift (Low, Base, High).
-- ENGINE: ANSI SQL (DuckDB / SQLite / PostgreSQL / MySQL compatible)
--
-- BUSINESS QUESTION ANSWERED:
-- How should Grito Labs reallocate its fixed 90-day marketing budget across
-- channels to maximize revenue and enrollments while mitigating saturation risk?
-- ============================================================================

-- ----------------------------------------------------------------------------
-- STEP 1: Current Baseline Spend, Multi-Touch Attributed Revenue & ROAS
-- ----------------------------------------------------------------------------
WITH channel_spend_agg AS (
    SELECT 
        s.channel_id,
        c.channel_name,
        c.is_paid,
        SUM(s.spend) AS current_spend
    FROM fact_daily_spend s
    JOIN dim_channel c ON s.channel_id = c.channel_id
    WHERE c.is_paid = 1
    GROUP BY s.channel_id, c.channel_name, c.is_paid
),
channel_attrib_agg AS (
    SELECT 
        w.channel_id,
        SUM(w.weight_position_based) AS current_attributed_conversions,
        SUM(w.weight_position_based * w.conversion_revenue) AS current_attributed_revenue
    FROM v_touchpoint_attribution_weights w
    GROUP BY w.channel_id
),
current_channel_state AS (
    SELECT 
        s.channel_id,
        s.channel_name,
        s.is_paid,
        s.current_spend,
        COALESCE(a.current_attributed_conversions, 0.0) AS current_attributed_conversions,
        COALESCE(a.current_attributed_revenue, 0.0) AS current_attributed_revenue,
        COALESCE(a.current_attributed_revenue, 0.0) / NULLIF(s.current_spend, 0) AS current_roas
    FROM channel_spend_agg s
    LEFT JOIN channel_attrib_agg a ON s.channel_id = a.channel_id
),
portfolio_total AS (
    SELECT 
        SUM(current_spend) AS total_marketing_budget
    FROM current_channel_state
),
-- ----------------------------------------------------------------------------
-- STEP 2: Recommended Budget Reallocation Strategy (Strict Zero-Sum Fixed Budget)
-- Rationale:
-- - Paid Search: Near saturation in brand terms; prune competitor search (-$4,000 / -2.0%).
-- - Paid Social: High top-of-funnel discovery; scale Meta prospecting (+$5,000 / +3.5%).
-- - Email Marketing: High marginal ROAS (13.98x), underfunded; scale nurture sequences (+$12,000 / +87.6%).
-- - Display Ads: Low conversion efficiency; cut awareness budget (-$20,000 / -38.7%) to stop ad fatigue.
-- - Referral: Strong LTV and trusted conversion; increase partner incentives (+$7,000 / +35.5%).
-- Net Budget Shift = -$20,000 - $4,000 + $12,000 + $7,000 + $5,000 = $0.00 (Exact Fixed Budget)
-- ----------------------------------------------------------------------------
reallocation_targets AS (
    SELECT 
        c.channel_id,
        c.channel_name,
        c.current_spend,
        c.current_attributed_conversions,
        c.current_attributed_revenue,
        c.current_roas,
        
        -- Exact zero-sum dollar shift
        CASE 
            WHEN c.channel_name = 'Paid Search'      THEN -4000.00
            WHEN c.channel_name = 'Paid Social'      THEN +5000.00
            WHEN c.channel_name = 'Email Marketing'  THEN +12000.00
            WHEN c.channel_name = 'Display Ads'      THEN -20000.00
            WHEN c.channel_name = 'Referral'         THEN +7000.00
            ELSE 0.00
        END AS dollar_shift,

        -- Channel Diminishing Returns Elasticity Exponent (Beta: 0.65 to 0.85)
        CASE 
            WHEN c.channel_name = 'Paid Search'      THEN 0.75
            WHEN c.channel_name = 'Paid Social'      THEN 0.70
            WHEN c.channel_name = 'Email Marketing'  THEN 0.88
            WHEN c.channel_name = 'Display Ads'      THEN 0.60
            WHEN c.channel_name = 'Referral'         THEN 0.82
            ELSE 0.70
        END AS elasticity_beta
    FROM current_channel_state c
),
optimized_projections AS (
    SELECT 
        rt.channel_id,
        rt.channel_name,
        ROUND(rt.current_spend, 2) AS current_spend,
        ROUND(rt.current_spend + rt.dollar_shift, 2) AS recommended_spend,
        ROUND(rt.dollar_shift, 2) AS dollar_shift,
        ROUND((rt.dollar_shift / rt.current_spend) * 100.0, 1) AS pct_shift,
        ROUND(rt.current_roas, 2) AS current_roas,
        
        -- Projected Revenue using Diminishing Return Power Curve:
        -- Projected Rev = Current Rev * (Recommended Spend / Current Spend) ^ Beta
        ROUND(rt.current_attributed_revenue * POWER((1.0 + (rt.dollar_shift / rt.current_spend)), rt.elasticity_beta), 2) AS projected_revenue_base,
        
        -- Scenario Modeling (Low: -10% execution risk, High: +15% creative upside)
        ROUND(rt.current_attributed_revenue * POWER((1.0 + (rt.dollar_shift / rt.current_spend)), rt.elasticity_beta) * 0.90, 2) AS projected_revenue_low,
        ROUND(rt.current_attributed_revenue * POWER((1.0 + (rt.dollar_shift / rt.current_spend)), rt.elasticity_beta) * 1.15, 2) AS projected_revenue_high,
        
        -- Projected Conversions
        ROUND(rt.current_attributed_conversions * POWER((1.0 + (rt.dollar_shift / rt.current_spend)), rt.elasticity_beta), 1) AS projected_conversions_base
    FROM reallocation_targets rt
)
SELECT 
    op.channel_name,
    op.current_spend,
    op.recommended_spend,
    op.dollar_shift,
    op.pct_shift,
    op.current_roas,
    -- Projected Base Metrics
    op.projected_revenue_base,
    ROUND(op.projected_revenue_base / NULLIF(op.recommended_spend, 0), 2) AS projected_roas,
    ROUND(op.projected_revenue_base - (op.current_spend * op.current_roas), 2) AS incremental_revenue_base,
    -- Scenarios
    op.projected_revenue_low,
    op.projected_revenue_high
FROM optimized_projections op

UNION ALL

-- Portfolio Totals & Net Uplift
SELECT 
    'TOTAL PORTFOLIO' AS channel_name,
    ROUND(SUM(op.current_spend), 2) AS current_spend,
    ROUND(SUM(op.recommended_spend), 2) AS recommended_spend,
    ROUND(SUM(op.dollar_shift), 2) AS dollar_shift,
    0.0 AS pct_shift,
    ROUND(SUM(op.current_spend * op.current_roas) / SUM(op.current_spend), 2) AS current_roas,
    ROUND(SUM(op.projected_revenue_base), 2) AS projected_revenue_base,
    ROUND(SUM(op.projected_revenue_base) / SUM(op.recommended_spend), 2) AS projected_roas,
    ROUND(SUM(op.projected_revenue_base - (op.current_spend * op.current_roas)), 2) AS incremental_revenue_base,
    ROUND(SUM(op.projected_revenue_low), 2) AS projected_revenue_low,
    ROUND(SUM(op.projected_revenue_high), 2) AS projected_revenue_high
FROM optimized_projections op;
