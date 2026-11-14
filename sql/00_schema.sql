-- ============================================================================
-- SCRIPT: 00_schema.sql
-- PROJECT: Grito Labs Multi-Channel Marketing Analytics & Attribution Framework
-- PURPOSE: Define the DDL for the Star-Schema Data Warehouse.
-- ENGINE: ANSI SQL (DuckDB / SQLite / PostgreSQL / MySQL compatible)
--
-- BUSINESS QUESTION ANSWERED:
-- How should our marketing touchpoints, spend, customer dimensions, and
-- conversion events be structured to support multi-touch attribution,
-- cohort analysis, and executive KPI reporting with referential integrity?
-- ============================================================================

-- Drop existing tables if recreating schema
DROP TABLE IF EXISTS fact_conversions;
DROP TABLE IF EXISTS fact_touchpoints;
DROP TABLE IF EXISTS fact_daily_spend;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_campaign;
DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_date;

-- ----------------------------------------------------------------------------
-- 1. DIMENSION: dim_channel
-- Grain: One record per marketing channel.
-- ----------------------------------------------------------------------------
CREATE TABLE dim_channel (
    channel_id INTEGER PRIMARY KEY,
    channel_name VARCHAR(50) NOT NULL UNIQUE,
    channel_group VARCHAR(50) NOT NULL,
    cpc_base DECIMAL(10, 2),
    is_paid INTEGER NOT NULL -- 1 = Paid Media, 0 = Organic/Owned/Earned
);

-- ----------------------------------------------------------------------------
-- 2. DIMENSION: dim_campaign
-- Grain: One record per marketing campaign.
-- ----------------------------------------------------------------------------
CREATE TABLE dim_campaign (
    campaign_id VARCHAR(50) PRIMARY KEY,
    campaign_name VARCHAR(100) NOT NULL,
    channel_id INTEGER NOT NULL,
    objective VARCHAR(50),
    target_audience VARCHAR(100),
    daily_budget DECIMAL(12, 2),
    FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id)
);

-- ----------------------------------------------------------------------------
-- 3. DIMENSION: dim_customer
-- Grain: One record per unique customer (lead/user).
-- ----------------------------------------------------------------------------
CREATE TABLE dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    first_touch_date DATE NOT NULL,
    acquisition_channel VARCHAR(50) NOT NULL,
    segment VARCHAR(50),
    country VARCHAR(50),
    has_converted INTEGER NOT NULL -- 1 if customer ever converted, else 0
);

-- ----------------------------------------------------------------------------
-- 4. DIMENSION: dim_date
-- Grain: One record per calendar day.
-- ----------------------------------------------------------------------------
CREATE TABLE dim_date (
    date DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter VARCHAR(10) NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend INTEGER NOT NULL -- 1 = Weekend, 0 = Weekday
);

-- ----------------------------------------------------------------------------
-- 5. FACT: fact_touchpoints
-- Grain: One record per customer interaction (click or view-through impression).
-- ----------------------------------------------------------------------------
CREATE TABLE fact_touchpoints (
    touchpoint_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    session_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    channel_id INTEGER NOT NULL,
    channel_name VARCHAR(50) NOT NULL,
    campaign_id VARCHAR(50) NOT NULL,
    touch_type VARCHAR(20) NOT NULL, -- 'click' or 'impression'
    cost DECIMAL(10, 4) NOT NULL,
    position INTEGER NOT NULL,
    is_conversion_touch INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id),
    FOREIGN KEY (campaign_id) REFERENCES dim_campaign(campaign_id)
);

-- ----------------------------------------------------------------------------
-- 6. FACT: fact_conversions
-- Grain: One record per conversion / enrollment order.
-- ----------------------------------------------------------------------------
CREATE TABLE fact_conversions (
    conversion_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    touchpoint_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    revenue DECIMAL(12, 2) NOT NULL,
    conversion_type VARCHAR(50) NOT NULL,
    conversion_cycle INTEGER NOT NULL, -- 1 = Initial Acquisition, 2+ = Repeat
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
);

-- ----------------------------------------------------------------------------
-- 7. FACT: fact_daily_spend
-- Grain: Daily aggregated media spend, impressions, and clicks per campaign.
-- ----------------------------------------------------------------------------
CREATE TABLE fact_daily_spend (
    date DATE NOT NULL,
    channel_id INTEGER NOT NULL,
    campaign_id VARCHAR(50) NOT NULL,
    impressions INTEGER NOT NULL,
    clicks INTEGER NOT NULL,
    spend DECIMAL(12, 2) NOT NULL,
    PRIMARY KEY (date, channel_id, campaign_id),
    FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id),
    FOREIGN KEY (campaign_id) REFERENCES dim_campaign(campaign_id)
);

-- ----------------------------------------------------------------------------
-- PERFORMANCE INDEXES
-- ----------------------------------------------------------------------------
CREATE INDEX idx_tp_cust_time ON fact_touchpoints (customer_id, timestamp);
CREATE INDEX idx_tp_channel ON fact_touchpoints (channel_id);
CREATE INDEX idx_tp_campaign ON fact_touchpoints (campaign_id);
CREATE INDEX idx_conv_cust_time ON fact_conversions (customer_id, timestamp);
CREATE INDEX idx_spend_date_chan ON fact_daily_spend (date, channel_id);
