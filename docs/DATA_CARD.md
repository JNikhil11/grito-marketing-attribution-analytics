# Dataset Card: Grito Labs Multi-Channel Marketing Telemetry

**Dataset Name:** Grito Labs EdTech Multi-Channel Customer Journeys & Conversions  
**Domain:** EdTech (Data Analytics & Business Decision Science)  
**Version:** 2.0 (Verified Seed 42 Run)  
**Curator:** J Nikhil ([GitHub: JNikhil11](https://github.com/JNikhil11))  
**Date of Release:** November 2026  
**Authenticity Notice:** Synthetic dataset generated to mimic realistic multi-channel marketing behavior (Seed 42), because the legacy public Criteo Attribution Modeling for Bidding dataset (Diemert et al., 2017) host link returned HTTP 404 (dead mirror) and HuggingFace mirrors require restricted authentication tokens. The synthetic generator guarantees 100% deterministic, zero-setup mathematical reproducibility while accurately modeling EdTech unit economics, multi-touch consideration gestation, and channel synergies.

---

## 1. Dataset Summary & Provenance

This dataset captures individual prospective student interactions across digital marketing channels (Paid Search, Paid Social, Email Marketing, Display Ads, Organic Search, Referral, Direct), tracking user trajectories from initial touchpoint through paid course enrollment.

- **Primary Conceptual Reference:** Criteo Attribution Modeling for Bidding Dataset (Diemert et al., 2017).
  - Source Reference: [ResearchGate / Criteo Research](https://www.researchgate.net/publication/322989255_Attribution_Modeling_for_Bidding_in_Display_Advertising)
  - Public License Reference: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).
- **Domain Adaptation:** Calibrated to reflect high-involvement EdTech education economics (3-tier course ladder: Foundation Certificate $349, Analytics Bootcamp $999, Executive Fellowship $2,199).
- **Generation Reproducibility:** Executable via `python src/generate_dataset.py` with fixed random seed `42`.

---

## 2. Dataset Dimensions & Volume

| Entity Table | Storage Path | Row Count | Column Count | Primary Key | Description |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **`dim_channel`** | `data/processed/dim_channel.csv` | 7 | 5 | `channel_id` | Marketing channel dimensions & CPC benchmarks |
| **`dim_campaign`** | `data/processed/dim_campaign.csv` | 14 | 6 | `campaign_id` | Campaign metadata, objectives, target personas |
| **`dim_customer`** | `data/processed/dim_customer.csv` | 16,000 | 6 | `customer_id` | Prospective and enrolled student profiles |
| **`dim_date`** | `data/processed/dim_date.csv` | 92 | 9 | `date` | Calendar dimension (Aug 1 - Oct 31, 2026) |
| **`fact_touchpoints`** | `data/processed/fact_touchpoints.csv` | 40,806 | 11 | `touchpoint_id` | Granular digital interactions (clicks & impressions) |
| **`fact_conversions`** | `data/processed/fact_conversions.csv` | 2,744 | 10 | `conversion_id` | Verified course enrollment transactions |
| **`fact_daily_spend`** | `data/processed/fact_daily_spend.csv` | 1,300 | 6 | `(date, channel_id, campaign_id)` | Daily media spend, impressions, and clicks |

---

## 3. Data Quality & Integrity Validation

All tables underwent automated schema and integrity checks during ingestion:
1. **Uniqueness:** 0 duplicate primary keys across all fact and dimension tables.
2. **Referential Integrity:** 0 orphan foreign keys; 100% of touchpoint and conversion records cleanly resolve to customer, channel, and campaign dimensions.
3. **Financial Constraints:** 0 negative costs, 0 negative spend records, and 0 non-positive revenues. Total paid media spend equals **$426,418.04** (17.96% of total revenue).
4. **Chronological Validity:** 100% of conversion timestamps occur strictly at or after preceding touchpoints within a 30-day sessionization window.
5. **Reconciliation Audit:** Attributed conversion revenue across all 5 SQL models equals the ground truth conversion revenue (**$2,382,514.60**) to the exact penny ($0.00 discrepancy).
6. **Multi-Touch Realism:** Exactly 1,897 of 2,744 orders (69.1%) involve multi-channel journeys ($\ge 2$ touchpoints), satisfying realistic high-involvement education research criteria.

---

## 4. Known Limitations & Analytical Boundaries

1. **Synthetic Nature:** Generated to mimic realistic multi-channel marketing behavior (seed 42). Real-world production deployment would replace this pipeline with raw telemetry from snowplow/segment or Google Analytics 4 BigQuery export streams.
2. **First-Party Identity Assumption:** The dataset assumes deterministic cross-device tracking via unified `customer_id`. Real-world deployments must account for cookie loss (Safari ITP, Chrome Privacy Sandbox) through probabilistic identity stitching.
3. **Ad Viewability & Offline Channels:** Offline touchpoints (word-of-mouth conversations, campus events) and non-viewable ad impressions are outside current digital telemetry boundaries.
