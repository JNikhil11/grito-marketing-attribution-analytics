-- ============================================================================
-- SCRIPT: 06_clv_cohort.sql
-- PROJECT: Grito Labs Multi-Channel Marketing Analytics & Attribution Framework
-- PURPOSE: Calculate Historical Customer Lifetime Value (CLV), Repeat Rates,
--          Monthly Cohort Retention Curves, and LTV:CAC ratios by channel.
-- ENGINE: ANSI SQL (DuckDB / SQLite / PostgreSQL / MySQL compatible)
--
-- BUSINESS QUESTION ANSWERED:
-- Which acquisition channels bring customers with the highest long-term
-- retention and repeat enrollment value, and what is our LTV:CAC health?
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: Customer-Level CLV & Repeat Purchase Summary by Acquisition Channel
-- Purpose: Aggregate initial vs repeat enrollments and calculate LTV:CAC.
-- ----------------------------------------------------------------------------
WITH customer_order_aggregates AS (
    SELECT 
        c.customer_id,
        c.acquisition_channel,
        c.segment,
        c.country,
        c.first_touch_date,
        COUNT(cv.conversion_id) AS total_orders,
        SUM(cv.revenue) AS lifetime_revenue,
        MIN(cv.timestamp) AS first_order_date,
        MAX(cv.timestamp) AS last_order_date,
        CASE WHEN COUNT(cv.conversion_id) > 1 THEN 1 ELSE 0 END AS is_repeat_customer
    FROM dim_customer c
    JOIN fact_conversions cv ON c.customer_id = cv.customer_id
    GROUP BY c.customer_id, c.acquisition_channel, c.segment, c.country, c.first_touch_date
),
channel_acquisition_costs AS (
    SELECT 
        c.channel_name,
        SUM(s.spend) AS total_spend
    FROM fact_daily_spend s
    JOIN dim_channel c ON s.channel_id = c.channel_id
    GROUP BY c.channel_name
)
SELECT 
    coa.acquisition_channel,
    COUNT(DISTINCT coa.customer_id) AS acquired_customers,
    SUM(coa.is_repeat_customer) AS repeat_customers,
    ROUND(CAST(SUM(coa.is_repeat_customer) AS REAL) / COUNT(DISTINCT coa.customer_id) * 100.0, 2) AS repeat_rate_pct,
    ROUND(SUM(coa.lifetime_revenue), 2) AS total_lifetime_revenue,
    ROUND(AVG(coa.lifetime_revenue), 2) AS avg_historical_clv,
    ROUND(SUM(coa.total_orders) * 1.0 / COUNT(DISTINCT coa.customer_id), 2) AS avg_orders_per_customer,
    
    -- Blended CAC by First-Touch Acquisition Channel
    ROUND(COALESCE(cac.total_spend, 0.0) / COUNT(DISTINCT coa.customer_id), 2) AS blended_cac,
    
    -- LTV:CAC Ratio (Healthy SaaS/Edtech benchmark is 3.0x - 5.0x)
    ROUND(AVG(coa.lifetime_revenue) / NULLIF(COALESCE(cac.total_spend, 0.0) / COUNT(DISTINCT coa.customer_id), 0), 2) AS ltv_cac_ratio,
    
    -- LTV:CAC Health Evaluation
    CASE 
        WHEN AVG(coa.lifetime_revenue) / NULLIF(COALESCE(cac.total_spend, 0.0) / COUNT(DISTINCT coa.customer_id), 0) >= 4.0 THEN 'Elite Unit Economics (Scale Heavily)'
        WHEN AVG(coa.lifetime_revenue) / NULLIF(COALESCE(cac.total_spend, 0.0) / COUNT(DISTINCT coa.customer_id), 0) >= 2.5 THEN 'Healthy Economics (Scale Carefully)'
        WHEN AVG(coa.lifetime_revenue) / NULLIF(COALESCE(cac.total_spend, 0.0) / COUNT(DISTINCT coa.customer_id), 0) >= 1.0 THEN 'Marginal / Near Breakeven'
        ELSE 'Value-Destructive (CAC Exceeds LTV)'
    END AS economic_health
FROM customer_order_aggregates coa
LEFT JOIN channel_acquisition_costs cac ON coa.acquisition_channel = cac.channel_name
GROUP BY coa.acquisition_channel, cac.total_spend
ORDER BY total_lifetime_revenue DESC;

-- ----------------------------------------------------------------------------
-- QUERY 2: Monthly Acquisition Cohort Retention & Cumulative Revenue
-- Purpose: Track how monthly cohorts of newly acquired students generate
--          follow-on repeat revenue over subsequent months (Month 0, Month 1, Month 2).
-- ----------------------------------------------------------------------------
WITH first_purchase AS (
    SELECT 
        customer_id,
        MIN(SUBSTR(timestamp, 1, 7)) AS cohort_month
    FROM fact_conversions
    GROUP BY customer_id
),
cohort_size AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_initial_users
    FROM first_purchase
    GROUP BY cohort_month
),
monthly_orders AS (
    SELECT 
        fp.cohort_month,
        SUBSTR(cv.timestamp, 1, 7) AS order_month,
        -- Month index: (Year diff * 12) + Month diff
        (CAST(SUBSTR(cv.timestamp, 1, 4) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 1, 4) AS INTEGER)) * 12 +
        (CAST(SUBSTR(cv.timestamp, 6, 2) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 6, 2) AS INTEGER)) AS month_number,
        COUNT(DISTINCT cv.customer_id) AS active_students,
        COUNT(cv.conversion_id) AS total_orders,
        SUM(cv.revenue) AS monthly_revenue
    FROM fact_conversions cv
    JOIN first_purchase fp ON cv.customer_id = fp.customer_id
    GROUP BY fp.cohort_month, SUBSTR(cv.timestamp, 1, 7), cv.timestamp
)
SELECT 
    mo.cohort_month,
    cs.cohort_initial_users,
    mo.month_number,
    SUM(mo.active_students) AS active_students,
    ROUND(SUM(mo.active_students) * 100.0 / cs.cohort_initial_users, 2) AS retention_rate_pct,
    ROUND(SUM(mo.monthly_revenue), 2) AS cohort_revenue_period,
    -- Cumulative Revenue per Cohort via SUM OVER window function
    ROUND(SUM(SUM(mo.monthly_revenue)) OVER (
        PARTITION BY mo.cohort_month 
        ORDER BY mo.month_number 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS cumulative_cohort_revenue,
    -- Cumulative Revenue per Initial Customer (Cumulative CLV progression)
    ROUND(SUM(SUM(mo.monthly_revenue)) OVER (
        PARTITION BY mo.cohort_month 
        ORDER BY mo.month_number 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) / cs.cohort_initial_users, 2) AS cumulative_clv_per_student
FROM monthly_orders mo
JOIN cohort_size cs ON mo.cohort_month = cs.cohort_month
GROUP BY mo.cohort_month, cs.cohort_initial_users, mo.month_number
ORDER BY mo.cohort_month, mo.month_number;
