-- ============================================================================
-- SCRIPT: 05_campaign_ranking.sql
-- PROJECT: Grito Labs Multi-Channel Marketing Analytics & Attribution Framework
-- PURPOSE: Score marketing campaigns on Efficiency (ROAS, CAC) vs Scale (Revenue, Conversions)
--          and classify them into strategic performance quadrants.
-- ENGINE: ANSI SQL (DuckDB / SQLite / PostgreSQL / MySQL compatible)
--
-- BUSINESS QUESTION ANSWERED:
-- Which campaigns deserve aggressive budget scaling, which need creative
-- optimization, and which should be cut immediately to eliminate budget waste?
-- ============================================================================

WITH campaign_spend_agg AS (
    SELECT 
        campaign_id, 
        ROUND(SUM(spend), 2) AS total_spend 
    FROM fact_daily_spend 
    GROUP BY campaign_id
),
campaign_attrib_agg AS (
    SELECT 
        campaign_id,
        ROUND(SUM(weight_position_based), 2) AS attributed_conversions,
        ROUND(SUM(weight_position_based * conversion_revenue), 2) AS attributed_revenue
    FROM v_touchpoint_attribution_weights
    GROUP BY campaign_id
),
campaign_performance AS (
    SELECT 
        cmp.campaign_id,
        cmp.campaign_name,
        ch.channel_name,
        cmp.objective,
        cmp.target_audience,
        COALESCE(s.total_spend, 0.0) AS total_spend,
        COALESCE(a.attributed_conversions, 0.0) AS attributed_conversions,
        COALESCE(a.attributed_revenue, 0.0) AS attributed_revenue,
        ROUND(COALESCE(s.total_spend, 0.0) / NULLIF(a.attributed_conversions, 0), 2) AS cac,
        ROUND(COALESCE(a.attributed_revenue, 0.0) / NULLIF(s.total_spend, 0), 2) AS roas
    FROM dim_campaign cmp
    JOIN dim_channel ch ON cmp.channel_id = ch.channel_id
    LEFT JOIN campaign_spend_agg s ON cmp.campaign_id = s.campaign_id
    LEFT JOIN campaign_attrib_agg a ON cmp.campaign_id = a.campaign_id
),
portfolio_benchmarks AS (
    -- Compute portfolio medians and averages for thresholding
    SELECT 
        AVG(roas) AS avg_roas,
        AVG(attributed_revenue) AS avg_revenue
    FROM campaign_performance
    WHERE total_spend > 0
)
SELECT 
    cp.campaign_id,
    cp.campaign_name,
    cp.channel_name,
    cp.objective,
    cp.target_audience,
    cp.total_spend,
    cp.attributed_conversions,
    cp.attributed_revenue,
    cp.cac,
    cp.roas,
    
    -- Quadrant Classification:
    -- Stars: High ROAS (>= 2.5), High Revenue (>= $10,000)
    -- Scalable: High ROAS (>= 2.5), Moderate/Low Revenue (< $10,000)
    -- Question Marks: Low ROAS (< 2.5), High Revenue (>= $10,000)
    -- Cut Candidates: Low ROAS (< 2.5), Low Revenue (< $10,000)
    CASE 
        WHEN cp.roas >= 2.50 AND cp.attributed_revenue >= 10000.0 THEN '1. Stars (Scale & Protect)'
        WHEN cp.roas >= 2.50 AND cp.attributed_revenue < 10000.0  THEN '2. Scalable (Budget Infusion)'
        WHEN cp.roas < 2.50  AND cp.attributed_revenue >= 10000.0 THEN '3. Question Marks (Optimize Creatives)'
        ELSE '4. Cut Candidates (Reduce / Terminate)'
    END AS strategic_quadrant,
    
    -- Specific Actionable Directive
    CASE 
        WHEN cp.roas >= 2.50 AND cp.attributed_revenue >= 10000.0 THEN 'Increase budget by +20% with close bid monitoring'
        WHEN cp.roas >= 2.50 AND cp.attributed_revenue < 10000.0  THEN 'Double daily budget to test diminishing return ceiling'
        WHEN cp.roas < 2.50  AND cp.attributed_revenue >= 10000.0 THEN 'Refine negative keywords / refresh creative assets'
        ELSE 'Pause or slash budget by 50% to fund high-ROAS channels'
    END AS tactical_action,

    -- Rank by Efficiency and Scale
    RANK() OVER (ORDER BY cp.roas DESC) AS efficiency_rank,
    RANK() OVER (ORDER BY cp.attributed_revenue DESC) AS scale_rank
FROM campaign_performance cp
CROSS JOIN portfolio_benchmarks pb
ORDER BY cp.attributed_revenue DESC;
