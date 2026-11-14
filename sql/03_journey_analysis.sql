-- ============================================================================
-- SCRIPT: 03_journey_analysis.sql
-- PROJECT: Grito Labs Multi-Channel Marketing Analytics & Attribution Framework
-- PURPOSE: Analyze multi-touch customer journeys, paths, latency, and assists.
-- ENGINE: ANSI SQL (DuckDB / SQLite / PostgreSQL / MySQL compatible)
--
-- BUSINESS QUESTIONS ANSWERED:
-- 1. How many interactions does a prospective student need before enrolling?
-- 2. What is the typical gestation latency (time-to-convert) across different channels?
-- 3. Which multi-channel sequences produce the highest conversion volume?
-- 4. Which channels act as top-of-funnel "feeders", mid-funnel "assisters", or "closers"?
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Path Length Distribution
-- Purpose: Distribution of total touchpoints in customer conversion journeys.
-- Logic: Group by total_journey_touches on the cleaned journey view.
-- ----------------------------------------------------------------------------
WITH journey_lengths AS (
    SELECT 
        conversion_id,
        MAX(touch_rank_asc) AS path_length,
        MAX(conversion_revenue) AS revenue
    FROM v_valid_customer_journeys
    GROUP BY conversion_id
)
SELECT 
    path_length,
    COUNT(*) AS total_conversions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS conversion_share_pct,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS avg_order_value
FROM journey_lengths
GROUP BY path_length
ORDER BY path_length ASC;

-- ----------------------------------------------------------------------------
-- QUERY 2: Time-to-Convert (Journey Latency) Distribution
-- Purpose: Measure time elapsed (in days and hours) from the very first touchpoint
--          to the moment of conversion.
-- Logic: Min touchpoint_time subtracted from conversion_time.
-- ----------------------------------------------------------------------------
WITH journey_latency AS (
    SELECT 
        conversion_id,
        MIN(touchpoint_time) AS first_touch_time,
        MAX(conversion_time) AS conversion_time,
        ROUND((JULIANDAY(MAX(conversion_time)) - JULIANDAY(MIN(touchpoint_time))), 2) AS days_to_convert,
        ROUND((JULIANDAY(MAX(conversion_time)) - JULIANDAY(MIN(touchpoint_time))) * 24.0, 1) AS hours_to_convert
    FROM v_valid_customer_journeys
    GROUP BY conversion_id
)
SELECT 
    CASE 
        WHEN days_to_convert < 1.0 THEN 'Same Day (< 24 hrs)'
        WHEN days_to_convert <= 3.0 THEN '1 to 3 Days'
        WHEN days_to_convert <= 7.0 THEN '4 to 7 Days (1 Week)'
        WHEN days_to_convert <= 14.0 THEN '8 to 14 Days (2 Weeks)'
        WHEN days_to_convert <= 21.0 THEN '15 to 21 Days (3 Weeks)'
        ELSE '22 to 30 Days'
    END AS latency_bucket,
    COUNT(*) AS total_conversions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS share_pct,
    ROUND(AVG(days_to_convert), 2) AS avg_days_to_convert
FROM journey_latency
GROUP BY 
    CASE 
        WHEN days_to_convert < 1.0 THEN 'Same Day (< 24 hrs)'
        WHEN days_to_convert <= 3.0 THEN '1 to 3 Days'
        WHEN days_to_convert <= 7.0 THEN '4 to 7 Days (1 Week)'
        WHEN days_to_convert <= 14.0 THEN '8 to 14 Days (2 Weeks)'
        WHEN days_to_convert <= 21.0 THEN '15 to 21 Days (3 Weeks)'
        ELSE '22 to 30 Days'
    END
ORDER BY avg_days_to_convert ASC;

-- ----------------------------------------------------------------------------
-- QUERY 3A: Top Converting Channel Paths Overall
-- Purpose: Aggregate customer journey touchpoint sequences into path strings.
-- ----------------------------------------------------------------------------
WITH ordered_journey AS (
    SELECT 
        conversion_id,
        channel_name,
        touch_rank_asc
    FROM v_valid_customer_journeys
    ORDER BY conversion_id, touch_rank_asc
),
aggregated_paths AS (
    SELECT 
        conversion_id,
        GROUP_CONCAT(channel_name, ' > ') AS full_path,
        COUNT(*) AS journey_len
    FROM ordered_journey
    GROUP BY conversion_id
)
SELECT 
    full_path,
    COUNT(*) AS conversions,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS share_of_total_conversions,
    DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS path_rank
FROM aggregated_paths
GROUP BY full_path
ORDER BY conversions DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 3B: Top Multi-Touch Channel Paths Only (2+ Touches)
-- Purpose: Isolate multi-channel conversion sequences excluding single-touch paths.
-- ----------------------------------------------------------------------------
WITH ordered_journey AS (
    SELECT 
        conversion_id,
        channel_name,
        touch_rank_asc
    FROM v_valid_customer_journeys
    ORDER BY conversion_id, touch_rank_asc
),
aggregated_paths AS (
    SELECT 
        conversion_id,
        GROUP_CONCAT(channel_name, ' > ') AS full_path,
        COUNT(*) AS journey_len
    FROM ordered_journey
    GROUP BY conversion_id
)
SELECT 
    full_path,
    COUNT(*) AS conversions,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM aggregated_paths), 2) AS share_of_all_conversions_pct,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS share_of_multitouch_conversions_pct,
    DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS multitouch_rank
FROM aggregated_paths
WHERE journey_len >= 2
GROUP BY full_path
ORDER BY conversions DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 4: Channel Role Analysis (First-Touch vs Assist vs Last-Touch)
-- Purpose: Quantify the strategic role of each channel across the customer funnel:
--          - Introducer / Originator (First Touch)
--          - Assister / Nurturer (Middle Touch)
--          - Closer / Converter (Last Touch)
--          - Assist-to-Last-Touch Ratio (> 1 indicates pure assisting channel)
-- ----------------------------------------------------------------------------
WITH channel_positions AS (
    SELECT 
        conversion_id,
        channel_name,
        total_journey_touches,
        touch_rank_asc,
        touch_rank_desc,
        CASE WHEN touch_rank_asc = 1 THEN 1 ELSE 0 END AS is_first_touch,
        CASE WHEN touch_rank_desc = 1 THEN 1 ELSE 0 END AS is_last_touch,
        CASE WHEN touch_rank_asc > 1 AND touch_rank_desc > 1 THEN 1 ELSE 0 END AS is_assist_touch
    FROM v_valid_customer_journeys
)
SELECT 
    channel_name,
    COUNT(*) AS total_interactions,
    SUM(is_first_touch) AS first_touch_count,
    SUM(is_assist_touch) AS assist_touch_count,
    SUM(is_last_touch) AS last_touch_count,
    -- Assist-to-Last-Click Ratio: Assisting Touches / Last Clicks
    -- Benchmarks: > 1.5 = Feeder/Influencer; ~ 1.0 = Balanced; < 0.8 = Closer
    ROUND(CAST(SUM(is_assist_touch) AS REAL) / NULLIF(SUM(is_last_touch), 0), 2) AS assist_to_last_click_ratio,
    -- Strategic Funnel Classification
    CASE 
        WHEN CAST(SUM(is_assist_touch) AS REAL) / NULLIF(SUM(is_last_touch), 0) > 1.3 THEN 'Top/Mid-Funnel Feeder'
        WHEN CAST(SUM(is_assist_touch) AS REAL) / NULLIF(SUM(is_last_touch), 0) < 0.8 THEN 'Bottom-Funnel Closer'
        ELSE 'Balanced Full-Funnel'
    END AS strategic_role
FROM channel_positions
GROUP BY channel_name
ORDER BY assist_to_last_click_ratio DESC;

-- ----------------------------------------------------------------------------
-- QUERY 5: Channel-to-Channel Handoff Transition Matrix (Sankey Flow Input)
-- Purpose: Calculate step-by-step channel transitions (Source Channel -> Target Channel)
--          using the LEAD window function.
-- ----------------------------------------------------------------------------
WITH channel_steps AS (
    SELECT 
        conversion_id,
        channel_name AS source_channel,
        LEAD(channel_name) OVER (
            PARTITION BY conversion_id 
            ORDER BY touch_rank_asc
        ) AS target_channel
    FROM v_valid_customer_journeys
)
SELECT 
    source_channel,
    target_channel,
    COUNT(*) AS transition_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY source_channel), 2) AS transition_probability_pct
FROM channel_steps
WHERE target_channel IS NOT NULL
GROUP BY source_channel, target_channel
ORDER BY source_channel, transition_count DESC;
