# Grito Labs Marketing Analytics Data Model & ER Architecture

**Document Version:** 1.0  
**Storage Engine:** SQLite 3.35+ / DuckDB 0.9+ (Zero-Setup Portable ANSI SQL)  
**Target Schema:** Star-Schema Relational Warehouse  

---

## 1. Entity-Relationship (ER) Diagram

```
                             +-----------------------+
                             |       dim_date        |
                             +-----------------------+
                             | PK  date              |
                             |     year              |
                             |     quarter           |
                             |     month             |
                             |     month_name        |
                             |     day_of_month      |
                             |     day_of_week       |
                             |     day_name          |
                             |     is_weekend        |
                             +-----------------------+
                                         |
                                         | 1:N
                                         v
+-----------------------+ 1:N +-----------------------+ N:1 +-----------------------+
|      dim_channel      |<----|   fact_daily_spend    |---->|     dim_campaign      |
+-----------------------+     +-----------------------+     +-----------------------+
| PK  channel_id        |     | PK,FK date            |     | PK  campaign_id       |
|     channel_name      |     | PK,FK channel_id      |     |     campaign_name     |
|     channel_group     |     | PK,FK campaign_id     |     | FK  channel_id        |
|     cpc_base          |     |       impressions     |     |     objective         |
|     is_paid           |     |       clicks          |     |     target_audience   |
+-----------------------+     |       spend           |     |     daily_budget      |
        |                     +-----------------------+     +-----------------------+
        |                                                               |
        | 1:N                                                           | 1:N
        v                                                               v
+-------------------------------------------------------------------------------+
|                               fact_touchpoints                                |
+-------------------------------------------------------------------------------+
| PK  touchpoint_id                                                             |
| FK  customer_id                                                               |
|     session_id                                                                |
|     timestamp                                                                 |
| FK  channel_id                                                                |
|     channel_name                                                              |
| FK  campaign_id                                                               |
|     touch_type ('click' | 'impression')                                       |
|     cost                                                                      |
|     position                                                                  |
|     is_conversion_touch                                                       |
+-------------------------------------------------------------------------------+
        |                                                               ^
        | N:1                                                           |
        v                                                               |
+-----------------------+                                               |
|     dim_customer      |                                               |
+-----------------------+                                               |
| PK  customer_id       |                                               |
|     first_touch_date  |                                               |
|     acquisition_ch    |                                               |
|     segment           |                                               |
|     country           |                                               |
|     has_converted     |                                               |
+-----------------------+                                               |
        |                                                               |
        | 1:N                                                           |
        v                                                               |
+-------------------------------------------------------------------------------+
|                               fact_conversions                                |
+-------------------------------------------------------------------------------+
| PK  conversion_id                                                             |
| FK  customer_id                                                               |
| FK  touchpoint_id ------------------------------------------------------------+
|     order_id                                                                  |
|     product_id                                                                |
|     product_name                                                              |
|     timestamp                                                                 |
|     revenue                                                                   |
|     conversion_type                                                           |
|     conversion_cycle (1 = Initial Acquisition, 2 = Repeat)                    |
+-------------------------------------------------------------------------------+
```

---

## 2. Table Specifications & Grain Analysis

### Table: `dim_channel`
- **Grain:** One row per acquisition marketing channel.
- **Record Count:** 7 rows.
- **Attributes:**
  - `channel_id` (INTEGER, PK): Unique numeric surrogate key.
  - `channel_name` (VARCHAR, UNIQUE): Channel taxonomy name.
  - `channel_group` (VARCHAR): High-level grouping (Paid Search, Social, Owned, Display, Organic, Referral, Direct).
  - `cpc_base` (DECIMAL): Baseline cost-per-click benchmark.
  - `is_paid` (INTEGER): Binary indicator (1 = Paid advertising media, 0 = Organic/Owned).

### Table: `dim_campaign`
- **Grain:** One row per distinct marketing campaign.
- **Record Count:** 14 rows.
- **Attributes:**
  - `campaign_id` (VARCHAR, PK): Natural campaign identifier (`CMP-PS-01`, etc.).
  - `campaign_name` (VARCHAR): Descriptive campaign title.
  - `channel_id` (INTEGER, FK): Mapped channel in `dim_channel`.
  - `objective` (VARCHAR): Strategic intent (Capture Intent, Acquisition, Awareness, Cart Recovery, etc.).
  - `target_audience` (VARCHAR): Target persona description.
  - `daily_budget` (DECIMAL): Baseline allocated daily budget limit.

### Table: `dim_customer`
- **Grain:** One row per individual prospective or enrolled student.
- **Record Count:** 15,000 rows.
- **Attributes:**
  - `customer_id` (VARCHAR, PK): Unique persistent identifier (`CUST-000001`).
  - `first_touch_date` (DATE): Timestamp of first recorded brand touchpoint.
  - `acquisition_channel` (VARCHAR): Channel responsible for initial brand origination.
  - `segment` (VARCHAR): Student demographic persona (Career Switcher, Upskilling Analyst, etc.).
  - `country` (VARCHAR): Geographic market.
  - `has_converted` (INTEGER): Flag (1 = Customer placed an order, 0 = Non-converting visitor).

### Table: `dim_date`
- **Grain:** One row per calendar day.
- **Record Count:** 93 rows (2026-08-01 through 2026-11-01).
- **Attributes:** `date` (PK), `year`, `quarter`, `month`, `month_name`, `day_of_month`, `day_of_week`, `day_name`, `is_weekend`.

### Table: `fact_touchpoints`
- **Grain:** One row per individual digital interaction (click or view-through impression).
- **Record Count:** 48,818 rows.
- **Attributes:**
  - `touchpoint_id` (VARCHAR, PK): Unique touchpoint identifier.
  - `customer_id` (VARCHAR, FK): Lead or student receiving the interaction.
  - `session_id` (VARCHAR): Unique browsing session identifier.
  - `timestamp` (TIMESTAMP): Exact interaction timestamp.
  - `channel_id` (INTEGER, FK): Channel associated with the touchpoint.
  - `campaign_id` (VARCHAR, FK): Campaign associated with the ad/touchpoint.
  - `touch_type` (VARCHAR): 'click' or 'impression'.
  - `cost` (DECIMAL): Precise dollar expense incurred for this specific touchpoint.
  - `position` (INTEGER): Ordinal index of touchpoint within customer trajectory.
  - `is_conversion_touch` (INTEGER): 1 if conversion event directly occurred after this touchpoint.

### Table: `fact_conversions`
- **Grain:** One row per course enrollment transaction.
- **Record Count:** 2,894 rows (2,534 Initial Acquisitions + 360 Repeat Purchases).
- **Attributes:**
  - `conversion_id` (VARCHAR, PK): Unique conversion record.
  - `customer_id` (VARCHAR, FK): Enrolling student.
  - `touchpoint_id` (VARCHAR, FK): Last-click touchpoint preceding conversion.
  - `order_id` (VARCHAR): Financial order reference.
  - `product_id` (VARCHAR): Course package purchased (`PRD-01`, `PRD-02`, `PRD-03`).
  - `product_name` (VARCHAR): Course package title.
  - `timestamp` (TIMESTAMP): Order completion timestamp.
  - `revenue` (DECIMAL): Order transaction value in USD ($).
  - `conversion_type` (VARCHAR): 'Course Enrollment' or 'Repeat Enrollment'.
  - `conversion_cycle` (INTEGER): 1 for first order, 2 for repeat enrollment.

### Table: `fact_daily_spend`
- **Grain:** Daily aggregated media spend, impressions, and clicks per campaign.
- **Record Count:** 1,325 rows.
- **Attributes:**
  - `date` (DATE, Composite PK): Calendar day of media flight.
  - `channel_id` (INTEGER, Composite PK): Channel identifier.
  - `campaign_id` (VARCHAR, Composite PK): Campaign identifier.
  - `impressions` (INTEGER): Total impressions served.
  - `clicks` (INTEGER): Total clicks received.
  - `spend` (DECIMAL): Total verified media expenditure.

---

## 3. Indexing & Query Optimization Strategy

Analytical queries heavily join `fact_touchpoints`, `fact_conversions`, and `fact_daily_spend`. To ensure sub-second latency across 50,000+ records in DuckDB and SQLite, the following b-tree indexes are deployed:
1. `idx_tp_cust_time`: Compound index on `(customer_id, timestamp)` for rapid journey sessionization and window filtering.
2. `idx_tp_channel`: Index on `(channel_id)` for aggregated channel attribution rollups.
3. `idx_tp_campaign`: Index on `(campaign_id)` for campaign quadrant scoring.
4. `idx_conv_cust_time`: Index on `(customer_id, timestamp)` for conversion lookback joins.
5. `idx_spend_date_chan`: Compound index on `(date, channel_id)` for daily KPI aggregation.
