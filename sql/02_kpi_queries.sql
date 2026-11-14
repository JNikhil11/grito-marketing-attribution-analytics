-- ============================================================================
-- SCRIPT: 02_kpi_queries.sql
-- PROJECT: Grito Labs Multi-Channel Marketing Analytics & Attribution Framework
-- PURPOSE: Compute channel, campaign, and monthly marketing performance KPIs.
-- ENGINE: ANSI SQL (DuckDB / SQLite / PostgreSQL / MySQL compatible)
--
-- FORMULAS & DEFINITIONS:
-- 1. CTR (Click-Through Rate) = Total Clicks / Total Impressions * 100
-- 2. CPC (Cost Per Click)     = Total Spend / Total Clicks
-- 3. CVR (Conversion Rate)   = Total Conversions / Total Clicks * 100
-- 4. CAC / CPA (Cost Per Acq) = Total Spend / Total Conversions
-- 5. ROAS (Return on Ad Spend)= Attributed Revenue / Total Spend
-- 6. ROI (Net Return on Inv)  = (Attributed Revenue - Total Spend) / Total Spend
-- 7. Revenue Share (%)        = Channel Revenue / Total Revenue * 100
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Channel-Level Macro Performance & Efficiency Summary
-- Purpose: Evaluate aggregate ROI, ROAS, CAC, CTR, and CPC across marketing channels.
-- Business Question: Which marketing channels generate the highest returns and efficiency?
-- ----------------------------------------------------------------------------
WITH channel_media_metrics AS (
    SELECT 
        s.channel_id,
        c.channel_name,
        c.channel_group,
        c.is_paid,
        SUM(s.impressions) AS total_impressions,
        SUM(s.clicks) AS total_clicks,
        SUM(s.spend) AS total_spend
    FROM fact_daily_spend s
    JOIN dim_channel c ON s.channel_id = c.channel_id
    GROUP BY s.channel_id, c.channel_name, c.channel_group, c.is_paid
),
channel_last_touch_conversions AS (
    -- Baseline Last-Touch conversions from the touchpoint directly triggering order
    SELECT 
        tp.channel_id,
        COUNT(DISTINCT cv.conversion_id) AS total_conversions,
        SUM(cv.revenue) AS total_revenue
    FROM fact_conversions cv
    JOIN fact_touchpoints tp ON cv.touchpoint_id = tp.touchpoint_id
    WHERE cv.conversion_cycle = 1
    GROUP BY tp.channel_id
)
SELECT 
    m.channel_id,
    m.channel_name,
    m.channel_group,
    m.is_paid,
    m.total_impressions,
    m.total_clicks,
    ROUND(m.total_spend, 2) AS total_spend,
    COALESCE(c.total_conversions, 0) AS last_touch_conversions,
    ROUND(COALESCE(c.total_revenue, 0.0), 2) AS last_touch_revenue,
    -- CTR (%)
    ROUND(CAST(m.total_clicks AS REAL) / NULLIF(m.total_impressions, 0) * 100.0, 2) AS ctr_pct,
    -- CPC ($)
    ROUND(m.total_spend / NULLIF(m.total_clicks, 0), 2) AS cpc,
    -- CVR (%)
    ROUND(CAST(COALESCE(c.total_conversions, 0) AS REAL) / NULLIF(m.total_clicks, 0) * 100.0, 2) AS cvr_pct,
    -- CPA / CAC ($)
    CASE 
        WHEN m.is_paid = 1 THEN CAST(ROUND(m.total_spend / NULLIF(c.total_conversions, 0), 2) AS TEXT)
        ELSE 'n/a (unpaid)'
    END AS cpa_cac,
    -- ROAS ($ Revenue per $1 Spend)
    CASE 
        WHEN m.is_paid = 1 THEN CAST(ROUND(COALESCE(c.total_revenue, 0.0) / NULLIF(m.total_spend, 0), 2) AS TEXT)
        ELSE 'n/a'
    END AS last_touch_roas,
    -- ROI (%)
    CASE 
        WHEN m.is_paid = 1 THEN CAST(ROUND((COALESCE(c.total_revenue, 0.0) - m.total_spend) / NULLIF(m.total_spend, 0) * 100.0, 2) AS TEXT)
        ELSE 'n/a'
    END AS roi_pct,
    -- Revenue Share (%)
    ROUND(COALESCE(c.total_revenue, 0.0) / SUM(COALESCE(c.total_revenue, 0.0)) OVER () * 100.0, 2) AS rev_share_pct
FROM channel_media_metrics m
LEFT JOIN channel_last_touch_conversions c ON m.channel_id = c.channel_id
ORDER BY total_spend DESC;

-- ----------------------------------------------------------------------------
-- QUERY 2: Campaign-Level Granular Performance Matrix
-- Purpose: Drill down into individual campaign efficiency, volume, and unit economics.
-- Business Question: Which specific campaigns drive positive unit economics vs drain budget?
-- ----------------------------------------------------------------------------
WITH campaign_spend AS (
    SELECT 
        s.campaign_id,
        cmp.campaign_name,
        ch.channel_name,
        cmp.objective,
        SUM(s.impressions) AS total_impressions,
        SUM(s.clicks) AS total_clicks,
        SUM(s.spend) AS total_spend
    FROM fact_daily_spend s
    JOIN dim_campaign cmp ON s.campaign_id = cmp.campaign_id
    JOIN dim_channel ch ON s.channel_id = ch.channel_id
    GROUP BY s.campaign_id, cmp.campaign_name, ch.channel_name, cmp.objective
),
campaign_conversions AS (
    SELECT 
        tp.campaign_id,
        COUNT(DISTINCT cv.conversion_id) AS conversions,
        SUM(cv.revenue) AS revenue
    FROM fact_conversions cv
    JOIN fact_touchpoints tp ON cv.touchpoint_id = tp.touchpoint_id
    WHERE cv.conversion_cycle = 1
    GROUP BY tp.campaign_id
)
SELECT 
    cs.campaign_id,
    cs.campaign_name,
    cs.channel_name,
    cs.objective,
    cs.total_impressions,
    cs.total_clicks,
    ROUND(cs.total_spend, 2) AS total_spend,
    COALESCE(cc.conversions, 0) AS conversions,
    ROUND(COALESCE(cc.revenue, 0.0), 2) AS revenue,
    -- Unit Economics
    ROUND(CAST(cs.total_clicks AS REAL) / NULLIF(cs.total_impressions, 0) * 100.0, 2) AS ctr_pct,
    ROUND(cs.total_spend / NULLIF(cs.total_clicks, 0), 2) AS cpc,
    ROUND(CAST(COALESCE(cc.conversions, 0) AS REAL) / NULLIF(cs.total_clicks, 0) * 100.0, 2) AS cvr_pct,
    ROUND(cs.total_spend / NULLIF(cc.conversions, 0), 2) AS cac,
    ROUND(COALESCE(cc.revenue, 0.0) / NULLIF(cs.total_spend, 0), 2) AS roas,
    -- Efficiency Tiering using NTILE window function
    NTILE(4) OVER (ORDER BY COALESCE(cc.revenue, 0.0) / NULLIF(cs.total_spend, 0.001) DESC) AS roas_quartile
FROM campaign_spend cs
LEFT JOIN campaign_conversions cc ON cs.campaign_id = cc.campaign_id
ORDER BY total_spend DESC;

-- ----------------------------------------------------------------------------
-- QUERY 3: Monthly Time-Series Trend & Velocity
-- Purpose: Monitor monthly marketing pacing, conversion momentum, and ROAS trajectory.
-- Business Question: Are acquisition costs improving or degrading over consecutive months?
-- ----------------------------------------------------------------------------
WITH monthly_spend AS (
    SELECT 
        d.year,
        d.month,
        d.month_name,
        SUM(s.spend) AS monthly_spend,
        SUM(s.clicks) AS monthly_clicks
    FROM fact_daily_spend s
    JOIN dim_date d ON s.date = d.date
    GROUP BY d.year, d.month, d.month_name
),
monthly_conversions AS (
    SELECT 
        d.year,
        d.month,
        COUNT(DISTINCT cv.conversion_id) AS monthly_conversions,
        SUM(cv.revenue) AS monthly_revenue
    FROM fact_conversions cv
    JOIN dim_date d ON SUBSTR(cv.timestamp, 1, 10) = d.date
    WHERE cv.conversion_cycle = 1
    GROUP BY d.year, d.month
)
SELECT 
    ms.year,
    ms.month,
    ms.month_name,
    ROUND(ms.monthly_spend, 2) AS spend,
    ms.monthly_clicks,
    COALESCE(mc.monthly_conversions, 0) AS conversions,
    ROUND(COALESCE(mc.monthly_revenue, 0.0), 2) AS revenue,
    ROUND(ms.monthly_spend / NULLIF(mc.monthly_conversions, 0), 2) AS cac,
    ROUND(COALESCE(mc.monthly_revenue, 0.0) / NULLIF(ms.monthly_spend, 0), 2) AS roas,
    -- Month-over-Month Revenue Growth via LAG window function
    ROUND((COALESCE(mc.monthly_revenue, 0.0) - LAG(COALESCE(mc.monthly_revenue, 0.0)) OVER (ORDER BY ms.year, ms.month)) 
          / NULLIF(LAG(COALESCE(mc.monthly_revenue, 0.0)) OVER (ORDER BY ms.year, ms.month), 0) * 100.0, 2) AS mom_revenue_growth_pct
FROM monthly_spend ms
LEFT JOIN monthly_conversions mc ON ms.year = mc.year AND ms.month = mc.month
ORDER BY ms.year, ms.month;
