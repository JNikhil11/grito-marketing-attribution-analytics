-- ============================================================================
-- SCRIPT: 01_data_cleaning.sql
-- PROJECT: Grito Labs Multi-Channel Marketing Analytics & Attribution Framework
-- PURPOSE: Execute data quality validation, sanity checks, and data hygiene.
-- ENGINE: ANSI SQL (DuckDB / SQLite / PostgreSQL / MySQL compatible)
--
-- BUSINESS QUESTION ANSWERED:
-- Is our marketing telemetry data clean, consistent, and audit-ready before
-- we calculate financial KPIs and train attribution models?
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Row Count & Entity Audit
-- Purpose: Verify total volume of records across all core dimensional entities.
-- ----------------------------------------------------------------------------
SELECT 
    'dim_channel' AS entity_name, COUNT(*) AS total_records FROM dim_channel
UNION ALL
SELECT 
    'dim_campaign' AS entity_name, COUNT(*) AS total_records FROM dim_campaign
UNION ALL
SELECT 
    'dim_customer' AS entity_name, COUNT(*) AS total_records FROM dim_customer
UNION ALL
SELECT 
    'fact_touchpoints' AS entity_name, COUNT(*) AS total_records FROM fact_touchpoints
UNION ALL
SELECT 
    'fact_conversions' AS entity_name, COUNT(*) AS total_records FROM fact_conversions
UNION ALL
SELECT 
    'fact_daily_spend' AS entity_name, COUNT(*) AS total_records FROM fact_daily_spend;

-- ----------------------------------------------------------------------------
-- QUERY 2: Primary Key Uniqueness & Duplicate Audit
-- Purpose: Confirm zero duplicate primary keys across fact and dimension tables.
-- Logic: Group by primary key and filter HAVING count > 1.
-- ----------------------------------------------------------------------------
SELECT 'Duplicate Customers' AS check_type, COUNT(*) AS violation_count
FROM (
    SELECT customer_id, COUNT(*) AS cnt 
    FROM dim_customer 
    GROUP BY customer_id 
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'Duplicate Touchpoints' AS check_type, COUNT(*) AS violation_count
FROM (
    SELECT touchpoint_id, COUNT(*) AS cnt 
    FROM fact_touchpoints 
    GROUP BY touchpoint_id 
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'Duplicate Conversions' AS check_type, COUNT(*) AS violation_count
FROM (
    SELECT conversion_id, COUNT(*) AS cnt 
    FROM fact_conversions 
    GROUP BY conversion_id 
    HAVING COUNT(*) > 1
);

-- ----------------------------------------------------------------------------
-- QUERY 3: Referential Integrity & Orphan Record Check
-- Purpose: Verify all foreign keys in fact tables cleanly map to dimensions.
-- Logic: Left join facts to dimensions and filter where dimension key IS NULL.
-- ----------------------------------------------------------------------------
SELECT 
    'Orphan Touchpoint Customers' AS audit_rule,
    COUNT(t.touchpoint_id) AS orphan_count
FROM fact_touchpoints t
LEFT JOIN dim_customer c ON t.customer_id = c.customer_id
WHERE c.customer_id IS NULL
UNION ALL
SELECT 
    'Orphan Touchpoint Channels' AS audit_rule,
    COUNT(t.touchpoint_id) AS orphan_count
FROM fact_touchpoints t
LEFT JOIN dim_channel ch ON t.channel_id = ch.channel_id
WHERE ch.channel_id IS NULL
UNION ALL
SELECT 
    'Orphan Conversion Customers' AS audit_rule,
    COUNT(cv.conversion_id) AS orphan_count
FROM fact_conversions cv
LEFT JOIN dim_customer c ON cv.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- ----------------------------------------------------------------------------
-- QUERY 4: Financial & Operational Sanity Checks
-- Purpose: Ensure no negative spend, zero or negative order values, or invalid dates.
-- Logic: Conditional counts of anomalous records.
-- ----------------------------------------------------------------------------
SELECT
    SUM(CASE WHEN cost < 0 THEN 1 ELSE 0 END) AS negative_touchpoint_costs,
    SUM(CASE WHEN revenue <= 0 THEN 1 ELSE 0 END) AS invalid_conversion_revenue,
    SUM(CASE WHEN spend < 0 THEN 1 ELSE 0 END) AS negative_daily_spend,
    SUM(CASE WHEN impressions < clicks THEN 1 ELSE 0 END) AS impossible_ctr_records
FROM (
    SELECT cost, NULL AS revenue, NULL AS spend, NULL AS impressions, NULL AS clicks FROM fact_touchpoints
    UNION ALL
    SELECT NULL AS cost, revenue, NULL AS spend, NULL AS impressions, NULL AS clicks FROM fact_conversions
    UNION ALL
    SELECT NULL AS cost, NULL AS revenue, spend, impressions, clicks FROM fact_daily_spend
);

-- ----------------------------------------------------------------------------
-- QUERY 5: Temporal Logic Validation
-- Purpose: Validate that conversion timestamps occur AT OR AFTER the preceding touchpoint.
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(*) AS temporal_anomaly_count
FROM fact_conversions cv
JOIN fact_touchpoints tp ON cv.touchpoint_id = tp.touchpoint_id
WHERE cv.timestamp < tp.timestamp;

-- ----------------------------------------------------------------------------
-- QUERY 6: Cleaned Analytical View with 30-Day Lookback Window
-- Purpose: Pre-filter journeys where touchpoints fall strictly within a 30-day
--          lookback window before conversion, sessionizing touchpoint ranks.
-- ----------------------------------------------------------------------------
DROP VIEW IF EXISTS v_valid_customer_journeys;

CREATE VIEW v_valid_customer_journeys AS
WITH journey_window AS (
    SELECT 
        tp.touchpoint_id,
        tp.customer_id,
        tp.session_id,
        tp.timestamp AS touchpoint_time,
        tp.channel_id,
        tp.channel_name,
        tp.campaign_id,
        tp.touch_type,
        tp.cost,
        cv.conversion_id,
        cv.timestamp AS conversion_time,
        cv.revenue AS conversion_revenue,
        -- Julian day / day difference calculation for lookback
        -- Touchpoints occurring within 30 days prior to conversion
        ROUND((JULIANDAY(cv.timestamp) - JULIANDAY(tp.timestamp)), 2) AS days_before_conversion
    FROM fact_touchpoints tp
    INNER JOIN fact_conversions cv 
        ON tp.customer_id = cv.customer_id 
        AND cv.conversion_cycle = 1 -- Focus attribution on initial customer acquisition
    WHERE tp.timestamp <= cv.timestamp
      AND JULIANDAY(cv.timestamp) - JULIANDAY(tp.timestamp) <= 30.0
)
SELECT 
    touchpoint_id,
    customer_id,
    session_id,
    touchpoint_time,
    channel_id,
    channel_name,
    campaign_id,
    touch_type,
    cost,
    conversion_id,
    conversion_time,
    conversion_revenue,
    days_before_conversion,
    ROW_NUMBER() OVER (
        PARTITION BY conversion_id 
        ORDER BY touchpoint_time ASC
    ) AS touch_rank_asc,
    ROW_NUMBER() OVER (
        PARTITION BY conversion_id 
        ORDER BY touchpoint_time DESC
    ) AS touch_rank_desc,
    COUNT(*) OVER (
        PARTITION BY conversion_id
    ) AS total_journey_touches
FROM journey_window;
