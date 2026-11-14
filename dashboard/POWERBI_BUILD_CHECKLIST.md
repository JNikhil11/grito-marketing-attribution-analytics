# Power BI Build & Verification Checklist

This document is a comprehensive, tick-box quality assurance and verification checklist for building or auditing the **Grito Labs Multi-Channel Marketing Analytics & Attribution Engine** dashboard in Microsoft Power BI Desktop.

---

## 1. Data Ingestion & Model Configuration

- [ ] **Import Star Schema Tables from `data/powerbi_exports/`**:
  - [ ] `dim_channel.csv` (7 rows: Paid Search, Paid Social, Email Marketing, Display Ads, Organic Search, Referral, Direct)
  - [ ] `dim_campaign.csv` (14 campaigns)
  - [ ] `dim_customer.csv` (16,000 customers)
  - [ ] `dim_date.csv` (92 calendar dates: 2026-08-01 to 2026-10-31)
  - [ ] `fact_touchpoints.csv` (40,806 interaction records)
  - [ ] `fact_conversions.csv` (2,744 order records)
  - [ ] `fact_daily_spend.csv` (1,300 daily spend rows)
- [ ] **Import Pre-Aggregated Modeling Tables**:
  - [ ] `attribution_master_comparison.csv` (All 7 attribution models: FTA, LTA, Linear, Time-Decay, Position-Based, Markov, Shapley)
  - [ ] `budget_hill_optimization.csv` (Current vs recommended spend, dollar/pct shifts, marginal ROAS, scenario revenue)
  - [ ] `kpi_campaign_ranking.csv` (Efficiency vs scale quadrants, CAC, ROAS)
  - [ ] `clv_predictive_summary.csv` (Historical vs 12-month BG/NBD predictive CLV, LTV:CAC)
- [ ] **Verify Relationships & Cardinality**:
  - [ ] `fact_touchpoints[channel_id]` $\to$ `dim_channel[channel_id]` (*:1, Single)
  - [ ] `fact_touchpoints[campaign_id]` $\to$ `dim_campaign[campaign_id]` (*:1, Single)
  - [ ] `fact_touchpoints[customer_id]` $\to$ `dim_customer[customer_id]` (*:1, Single)
  - [ ] `fact_conversions[customer_id]` $\to$ `dim_customer[customer_id]` (*:1, Both)
  - [ ] `fact_daily_spend[channel_id]` $\to$ `dim_channel[channel_id]` (*:1, Single)
  - [ ] `fact_daily_spend[date]` $\to$ `dim_date[date]` (*:1, Single)
- [ ] **Format Columns**:
  - [ ] Set `date` columns to Data Type: `Date` (Format: `YYYY-MM-DD`).
  - [ ] Set currency fields (`spend`, `order_value`, `revenue`, `cost`, `cac`) to Data Type: `Decimal Number`, Format: `Currency ($)`, 2 decimal places.
  - [ ] Set percentage fields (`ctr_pct`, `cvr_pct`, `repeat_rate_pct`, `shift_pct`) to Data Type: `Percentage`, 1 or 2 decimal places.

---

## 2. Core DAX Measures Verification

Create a Dedicated Measures Table `_Measures` and verify each metric against the benchmark numbers:

- [ ] **Total Spend**:
  ```dax
  Total Spend = SUM(fact_daily_spend[spend])
  ```
  - *Expected Value*: **$426,418.04** ($\pm \$0.01$)
- [ ] **Total Conversions**:
  ```dax
  Total Conversions = COUNTROWS(fact_conversions)
  ```
  - *Expected Value*: **2,744**
- [ ] **Total Converted Revenue**:
  ```dax
  Total Revenue = SUM(fact_conversions[order_value])
  ```
  - *Expected Value*: **$2,374,133.70** ($\pm \$0.01$)
- [ ] **Blended Paid ROAS**:
  ```dax
  Blended Paid ROAS = 
  DIVIDE(
      CALCULATE([Total Revenue], dim_channel[is_paid] = 1),
      [Total Spend],
      BLANK()
  )
  ```
  - *Expected Value*: **3.96x**
- [ ] **Blended Paid CAC**:
  ```dax
  Blended Paid CAC = 
  DIVIDE(
      [Total Spend],
      CALCULATE([Total Conversions], dim_channel[is_paid] = 1),
      BLANK()
  )
  ```
  - *Expected Value*: **$155.40**
- [ ] **Multi-Touch Order Share**:
  ```dax
  MultiTouch Share = 
  VAR ConvertedCustomers = VALUES(fact_conversions[customer_id])
  VAR MultiTouchCust = 
      CALCULATE(
          DISTINCTCOUNT(fact_touchpoints[customer_id]),
          fact_touchpoints[customer_id] IN ConvertedCustomers,
          fact_touchpoints[position] >= 2
      )
  RETURN DIVIDE(MultiTouchCust, [Total Conversions], 0)
  ```
  - *Expected Value*: **69.1%** (1,897 / 2,744)

---

## 3. Visualizations & Canvas Verification

### Page 1: Executive Overview & Channel Attribution
- [ ] **Header Banner**: Navy background (`#0B2545`), white text, subtext noting 90-day period and Synthetic Dataset label (Seed 42).
- [ ] **Top 5 KPI Metric Cards**:
  - [ ] Card 1: `Total Paid Spend` $\to$ **$426.4K** (Subtext: "17.96% of Total Revenue")
  - [ ] Card 2: `Attributed Revenue` $\to$ **$2.37M** (Subtext: "Position-Based Model")
  - [ ] Card 3: `Blended Paid ROAS` $\to$ **3.96x** (Subtext: "Projected: 4.49x")
  - [ ] Card 4: `Paid Blended CAC` $\to$ **$155.40** (Subtext: "2,744 Enrolled Students")
  - [ ] Card 5: `Multi-Touch Share` $\to$ **69.1%** (Subtext: "Journeys $\ge$ 2 Touches")
- [ ] **Chart 1: Clustered Column Chart** (`Attributed Revenue vs Media Spend`):
  - [ ] X-axis: Channel Name
  - [ ] Column 1: Position-Based Revenue (Blue: `#007BFF`)
  - [ ] Column 2: Media Spend (Red: `#E63946`)
  - [ ] Verify Search ($536K rev, $198.4K spend) and Social ($571.9K rev, $143.0K spend) dominate.
- [ ] **Chart 2: 100% Stacked Bar Chart** (`Funnel Role Distribution`):
  - [ ] X-axis: Percentage of Touchpoints
  - [ ] Y-axis: Channel Name
  - [ ] Segments: First Touch (`#2A9D8F`), Assist Touch (`#E76F51`), Last Touch (`#134074`)
  - [ ] Verify Display and Social lead in First Touch; Email and Direct lead in Last/Assist.
- [ ] **Matrix Visual: Attribution Model Discrepancy Table**:
  - [ ] Rows: `channel_name`
  - [ ] Columns / Values: `Spend`, `Last-Touch Rev`, `Position-Based Rev`, `Markov Rev`, `Model ROAS`, `% Delta vs Last Touch`
  - [ ] Conditional Formatting: Delta $>0$ (Green), Delta $<0$ (Red).
  - [ ] Total Row check: Last-Touch ($2,374,133.70) = Position-Based ($2,374,133.70) = Markov ($2,374,133.70). Zero pennies leaked.

### Page 2: Customer Journey & Campaign Performance
- [ ] **Top Paths Table**:
  - [ ] Columns: Path Sequence, Orders, Share of Total Conversions
  - [ ] Top 3 sequences: Paid Social (10.4%), Paid Search (8.0%), Display Ads (5.2%).
- [ ] **Scatter Plot: Campaign Quadrant Matrix**:
  - [ ] X-axis: `Attributed Revenue ($)`
  - [ ] Y-axis: `ROAS (Return on Ad Spend)`
  - [ ] Quadrant Reference Lines: X-Median = $160,000, Y-Threshold = 4.0x ROAS
  - [ ] Color by Strategic Quadrant:
    - Stars: `PS_Brand_Core`, `SOC_Meta_Prospecting`, `SOC_Meta_Retargeting`, `DIS_Retargeting_Dynamic`, `REF_Student_Advocate`
    - Scalable Gems: `EM_Alumni_Upsell`, `EM_Webinar_Nurture`, `EM_Abandoned_Application`
    - Question Marks: `SOC_LinkedIn_Prof`, `PS_NonBrand_Analytics`, `PS_Competitor_Intercept`
- [ ] **Budget Reallocation Slicer / Table**:
  - [ ] Shows current spend, recommended shift (-$58.4K Search, +$21.3K Email, +$20.3K Referral, +$12.3K Display, +$4.6K Social).
  - [ ] Net Spend Shift: **$0.00** (Strict Fixed-Budget constraint).
  - [ ] Base Incremental Revenue Callout: **+$224,908.02**.

---

## 4. Final Audit & Publishing Sanity Checks

- [ ] Slicers dynamically filter visuals without circular dependency errors.
- [ ] All visual headers use sentence casing and executive action titles.
- [ ] Colors conform strictly to the Grito Labs enterprise brand palette (`#0B2545`, `#134074`, `#007BFF`, `#2A9D8F`, `#E76F51`, `#E63946`).
- [ ] All sensitive credentials, internal IPs, and file tokens are excluded.
- [ ] Total canvas resolution is standard 16:9 widescreen (1280x720 or 1920x1080).
