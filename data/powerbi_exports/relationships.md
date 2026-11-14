# Power BI Star Schema Data Model & Entity Relationships

This document outlines the table relationships, primary/foreign keys, and cardinalities for importing `data/powerbi_exports/` into Microsoft Power BI Desktop.

## Star Schema Architecture

```
        +-------------------+           +-------------------+
        |    dim_channel    |           |    dim_campaign   |
        +-------------------+           +-------------------+
        | channel_id (PK)   |           | campaign_id (PK)  |
        +---------+---------+           +---------+---------+
                  |                               |
                  | 1                             | 1
                  |                               |
                  | *                             | *
        +---------+-------------------------------+---------+
        |                    fact_touchpoints               |
        +---------------------------------------------------+
        | touchpoint_id (PK)                                |
        | customer_id (FK) >-----------+                    |
        | session_id                   |                    |
        | timestamp                    |                    |
        | channel_id (FK)              |                    |
        | campaign_id (FK)             |                    |
        | touch_type                   |                    |
        | cost                         |                    |
        | position                     |                    |
        | is_conversion_touch          |                    |
        +------------------------------+--------------------+
                                       |
                                       | *
                                       |
        +-------------------+          | 1
        |    dim_customer   | <--------+
        +-------------------+
        | customer_id (PK)  | <--------+
        +-------------------+          | 1
                                       |
                                       | *
        +------------------------------+--------------------+
        |                    fact_conversions               |
        +---------------------------------------------------+
        | conversion_id (PK)                                |
        | customer_id (FK)                                  |
        | conversion_timestamp                              |
        | order_value                                       |
        | course_tier                                       |
        +---------------------------------------------------+

        +-------------------+           +-------------------+
        |    dim_channel    |           |     dim_date      |
        +-------------------+           +-------------------+
        | channel_id (PK)   |           | date (PK)         |
        +---------+---------+           +---------+---------+
                  |                               |
                  | 1                             | 1
                  | *                             | *
        +---------+-------------------------------+---------+
        |                    fact_daily_spend               |
        +---------------------------------------------------+
        | spend_id (PK)                                     |
        | date (FK)                                         |
        | channel_id (FK)                                   |
        | campaign_id (FK)                                  |
        | spend                                             |
        | impressions                                       |
        | clicks                                            |
        +---------------------------------------------------+
```

---

## Detailed Relationship Specifications

| From Table (Many / Fact) | Foreign Key | To Table (One / Dimension) | Primary Key | Cardinality | Cross Filter Direction | Active |
|---|---|---|---|---|---|---|
| `fact_touchpoints` | `channel_id` | `dim_channel` | `channel_id` | Many-to-One (*:1) | Single (`dim_channel` filters `fact_touchpoints`) | Yes |
| `fact_touchpoints` | `campaign_id` | `dim_campaign` | `campaign_id` | Many-to-One (*:1) | Single (`dim_campaign` filters `fact_touchpoints`) | Yes |
| `fact_touchpoints` | `customer_id` | `dim_customer` | `customer_id` | Many-to-One (*:1) | Single (`dim_customer` filters `fact_touchpoints`) | Yes |
| `fact_conversions` | `customer_id` | `dim_customer` | `customer_id` | Many-to-One (*:1) | Both (Bidirectional for cohort analysis) | Yes |
| `fact_daily_spend` | `channel_id` | `dim_channel` | `channel_id` | Many-to-One (*:1) | Single (`dim_channel` filters `fact_daily_spend`) | Yes |
| `fact_daily_spend` | `campaign_id` | `dim_campaign` | `campaign_id` | Many-to-One (*:1) | Single (`dim_campaign` filters `fact_daily_spend`) | Yes |
| `fact_daily_spend` | `date` | `dim_date` | `date` | Many-to-One (*:1) | Single (`dim_date` filters `fact_daily_spend`) | Yes |

---

## Pre-Aggregated Analysis Tables (Disconnected or Linked by Channel)

The following tables are exported for high-speed executive dashboards and require no many-to-many resolution:

1. **`kpi_channel_summary.csv`**:
   - Primary Key: `channel_id`
   - Linked to `dim_channel.channel_id` (1:1)
   - Contains impressions, clicks, spend, CTR, CPC, CVR, CPA/CAC, ROAS, and ROI.

2. **`attribution_master_comparison.csv`**:
   - Primary Key: `channel_name`
   - Contains attributed conversion counts and attributed revenue across all 7 models (First-Touch, Last-Touch, Linear, Time-Decay, Position-Based/U-Shaped, Markov Chain, Shapley Value).

3. **`budget_hill_optimization.csv`**:
   - Primary Key: `channel_name`
   - Contains current spend, recommended spend, dollar shift, percentage shift, current ROAS, projected ROAS, marginal ROAS, and low/base/high revenue projections under Hill saturation curves.

4. **`kpi_campaign_ranking.csv`**:
   - Primary Key: `campaign_id`
   - Linked to `dim_campaign.campaign_id` (1:1)
   - Contains spend, attributed conversions, attributed revenue, CAC, ROAS, quadrant classification (`1. Stars`, `2. Scalable Gems`, `3. Question Marks`, `4. Cut Candidates`), and tactical recommendations.

5. **`clv_predictive_summary.csv`**:
   - Primary Key: `channel_name`
   - Contains acquired customers, repeat count, repeat rate %, spend, blended CAC, average historical CLV, 12-month BG/NBD predictive CLV, historical LTV:CAC, and predictive LTV:CAC.
