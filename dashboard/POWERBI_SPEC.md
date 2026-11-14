# Grito Labs Marketing Analytics & Attribution Framework
## Comprehensive Power BI Specification & Implementation Guide

**Document Version:** 2.0 (Verified Seed 42 Data Run)  
**Prepared For:** Grito Labs Analytics Leadership & Evaluation Committee  
**Build Time Benchmark:** ~2 Hours  
**Preferred Tooling:** Power BI Desktop (May 2024 or newer)  
**Data Sources:** CSV files located in `data/powerbi_exports/`  
**Dataset Nature:** Synthetic benchmark dataset generated to mimic realistic EdTech multi-channel behavior (Seed 42, 16,000 customers, 40,806 touchpoints, 2,744 enrollments).

---

## 1. Executive Overview & Design System

The Grito Labs Marketing Attribution Dashboard is an enterprise-grade reporting application designed to transform complex multi-touch customer journey telemetry into actionable budget decisions. It allows executive leaders to compare single-touch vs multi-touch attribution models dynamically, isolate campaign inefficiencies, and simulate budget reallocations under diminishing marginal returns.

### Color Palette & Theme Tokens
- **Primary Navy (Canvas Headers & Cards):** `#0B2545`
- **Secondary Slate Blue (Filters & Accents):** `#134074`
- **Accent Cyan / Brand Blue (Data Series & Primary Bars):** `#007BFF`
- **Success / High-ROAS Green (Stars & Growth):** `#2A9D8F`
- **Warning / Medium Amber (Question Marks & Attention):** `#E76F51`
- **Alert / Cut Candidate Crimson (High CAC / Negative Delta):** `#E63946`
- **Neutral Light Grey (Canvas Background):** `#F8F9FA`
- **Card Background White:** `#FFFFFF`
- **Typography:** Segoe UI (Titles: 16pt Bold, Metric Values: 24pt Bold, Data Labels: 10pt Regular)

---

## 2. Data Model & Relationship Architecture

Import all CSVs from `data/powerbi_exports/` using Power Query (Transform Data).

```
                      +-------------------+
                      |     dim_date      |
                      +-------------------+
                                | (1)
                                |
                                | (*)
+-------------------+ (1)   (*) +-------------------+ (*)   (1) +-------------------+
|    dim_channel    |-----------| fact_daily_spend  |-----------|   dim_campaign    |
+-------------------+           +-------------------+           +-------------------+
        | (1)                                                           | (1)
        |                                                               |
        | (*)                                                           | (*)
+-------------------+ (*)   (1) +-------------------+ (*)   (1) +-------------------+
| fact_touchpoints  |-----------|   dim_customer    |-----------| fact_conversions  |
+-------------------+           +-------------------+           +-------------------+
```

### Table Relationships in Power BI Model View:
1. `dim_date[date]` `1` $\longrightarrow$ `*` `fact_daily_spend[date]` (Single direction)
2. `dim_channel[channel_id]` `1` $\longrightarrow$ `*` `fact_daily_spend[channel_id]` (Single direction)
3. `dim_campaign[campaign_id]` `1` $\longrightarrow$ `*` `fact_daily_spend[campaign_id]` (Single direction)
4. `dim_customer[customer_id]` `1` $\longrightarrow$ `*` `fact_touchpoints[customer_id]` (Single direction)
5. `dim_channel[channel_id]` `1` $\longrightarrow$ `*` `fact_touchpoints[channel_id]` (Single direction)
6. `dim_campaign[campaign_id]` `1` $\longrightarrow$ `*` `fact_touchpoints[campaign_id]` (Single direction)
7. `dim_customer[customer_id]` `1` $\longrightarrow$ `*` `fact_conversions[customer_id]` (Both directions)
8. Disconnected Dimension for Dynamic Model Selection: `dim_attribution_model` (Created via DAX table).

---

## 3. Complete DAX Measure Library

Create a dedicated measure table named `_Measures`.

### Core Telemetry & Media Spend Measures
```dax
Total Spend = 
SUM(fact_daily_spend[spend])

Total Impressions = 
SUM(fact_daily_spend[impressions])

Total Clicks = 
SUM(fact_daily_spend[clicks])

CTR = 
DIVIDE([Total Clicks], [Total Impressions], 0)

CPC = 
DIVIDE([Total Spend], [Total Clicks], 0)

Total Conversions = 
COUNTROWS(fact_conversions)

Total Revenue = 
SUM(fact_conversions[order_value])

Blended Paid CAC = 
DIVIDE([Total Spend], [Total Conversions], 0)

Blended Paid ROAS = 
DIVIDE(
    CALCULATE([Total Revenue], dim_channel[is_paid] = 1),
    [Total Spend],
    BLANK()
)
```

### Multi-Touch Attribution Measures (from `attribution_master_comparison`)
```dax
FTA Revenue = 
SUM(attribution_master_comparison[revenue_first_touch])

LTA Revenue = 
SUM(attribution_master_comparison[revenue_last_touch])

Linear Revenue = 
SUM(attribution_master_comparison[revenue_linear])

Time Decay Revenue = 
SUM(attribution_master_comparison[revenue_time_decay])

Position Based Revenue = 
SUM(attribution_master_comparison[revenue_position_based])

Markov Revenue = 
SUM(attribution_master_comparison[revenue_markov])

Shapley Revenue = 
SUM(attribution_master_comparison[revenue_shapley])
```

### Dynamic Attribution Slicer & Measure Switcher
Create a disconnected parameter table:
```dax
dim_attribution_model = 
DATATABLE(
    "ModelID", INTEGER,
    "ModelName", STRING,
    "ModelType", STRING,
    {
        {1, "First-Touch Attribution", "Rule-Based"},
        {2, "Last-Touch Attribution", "Rule-Based"},
        {3, "Linear Attribution", "Rule-Based"},
        {4, "Time-Decay (7d Half-Life)", "Rule-Based"},
        {5, "Position-Based (U-Shaped 40-20-40)", "Rule-Based"},
        {6, "Data-Driven Markov Chain", "Algorithmic"},
        {7, "Data-Driven Shapley Value", "Game Theory"}
    }
)
```

Create the dynamic switching measure:
```dax
Selected Attribution Model = 
SELECTEDVALUE(dim_attribution_model[ModelName], "Position-Based (U-Shaped 40-20-40)")

Dynamic Attributed Revenue = 
SWITCH(
    [Selected Attribution Model],
    "First-Touch Attribution", [FTA Revenue],
    "Last-Touch Attribution", [LTA Revenue],
    "Linear Attribution", [Linear Revenue],
    "Time-Decay (7d Half-Life)", [Time Decay Revenue],
    "Position-Based (U-Shaped 40-20-40)", [Position Based Revenue],
    "Data-Driven Markov Chain", [Markov Revenue],
    "Data-Driven Shapley Value", [Shapley Revenue],
    [Position Based Revenue]
)

Dynamic ROAS = 
DIVIDE([Dynamic Attributed Revenue], [Total Spend], BLANK())

ROAS Shift vs Last Touch % = 
DIVIDE([Dynamic Attributed Revenue] - [LTA Revenue], [LTA Revenue], 0)
```

### Customer Lifetime Value & Repeat Purchase Measures
```dax
Historical CLV = 
AVERAGE(clv_predictive_summary[avg_historical_clv])

Predictive 12M CLV = 
AVERAGE(clv_predictive_summary[avg_predictive_12m_clv])

Repeat Purchase Rate = 
DIVIDE(SUM(clv_predictive_summary[repeat_customers]), SUM(clv_predictive_summary[acquired_customers]), 0)

LTV to CAC Ratio = 
DIVIDE([Historical CLV], [Blended Paid CAC], BLANK())
```

---

## 4. Page-by-Page Report Canvas Specification

### Page 1: Executive KPI & Channel Performance Overview
- **Header:** Title: "Grito Labs Marketing Analytics | Macro Channel Performance & Unit Economics" + Date Slicer (Aug 1 - Oct 31, 2026).
- **Row 1 (KPI Cards):**
  1. Total Paid Spend: `$426,418` (17.96% of Total Revenue)
  2. Total Attributed Revenue: `$2,374,134` (100% Reconciled)
  3. Blended Paid ROAS: `3.96x` (Base Optimized: `4.49x`)
  4. Blended Paid CAC: `$155.40`
  5. Multi-Touch Share: `69.1%` (1,897 / 2,744 Journeys)
- **Row 2 (Visuals):**
  - **Left (Clustered Bar Chart):** Channel Spend vs Attributed Revenue (Sort by Spend DESC).
  - **Right (Scatter Plot):** CAC vs ROAS by Channel (X-axis: CAC, Y-axis: ROAS, Bubble Size: Total Conversions).
- **Row 3 (Matrix Table):**
  - Columns: Channel Name, Impressions, Clicks, CTR %, CPC, Spend, Conversions, Revenue, CAC, ROAS, ROI %.

### Page 2: Multi-Touch Customer Journey & Path Velocity
- **Header:** Title: "Customer Journey Dynamics, Path Lengths & Funnel Assisted Conversions"
- **Row 1 (KPI Cards):**
  1. Multi-Touch Journey Share: `69.1%` (Percent of orders with $\ge 2$ touches)
  2. Average Days to Convert: `5.2 Days`
  3. Median Touchpoints per Enrolled Student: `2.8 Touches`
- **Row 2 (Visuals):**
  - **Left (Column Chart):** Path Length Distribution (1 Touch: 30.9%, 2-3 Touches: 48.4%, 4+ Touches: 20.7%).
  - **Right (Donut Chart):** Time-to-Convert Latency Buckets (<3 Days: 43.1%, 4-14 Days: 37.5%, 15-30 Days: 19.4%).
- **Row 3 (Visuals):**
  - **Left (Top 8 Horizontal Bar Chart):** Most Frequent Converting Paths (`Paid Social`: 286, `Paid Search`: 219, `Display Ads`: 142, etc.).
  - **Right (Stacked Bar Chart):** Channel Funnel Roles (First Touch vs Assist Touch vs Last Touch) with Assist-to-Last Ratio.

### Page 3: Multi-Touch Attribution Model Comparison
- **Header:** Title: "Multi-Touch Attribution Modeling Comparison & Sensitivity Analysis"
- **Top Control Banner:** Single-Select Slicer bound to `dim_attribution_model[ModelName]` + Lookback parameter.
- **Row 1 (Dynamic Metric Cards):**
  1. Selected Model Name
  2. Dynamically Attributed Revenue
  3. Dynamically Attributed ROAS
  4. Delta vs Last-Touch (%)
- **Row 2 (Visuals):**
  - **Clustered Column Chart:** Attributed Revenue Across All 7 Models by Channel (First-Touch, Last-Touch, Linear, Time-Decay, U-Shaped, Markov, Shapley).
  - **Waterfall Chart:** Net Revenue Shift When Moving from Last-Touch to Position-Based/Markov.
- **Row 3 (Detailed Comparison Matrix):**
  - Shows side-by-side revenue and ROAS shifts across models with conditional formatting (Green = credit gain, Red = credit loss).

### Page 4: Campaign Portfolio Quadrant Matrix
- **Header:** Title: "Campaign Ranking: Efficiency vs Scale Quadrant Classification"
- **Row 1 (Visuals):**
  - **Full-Width Scatter Chart (The Quadrant Matrix):**
    - X-Axis: Attributed Revenue (Scale, linear with \$160,000 reference line).
    - Y-Axis: ROAS (Efficiency, Reference line at 4.0x ROAS).
    - Quadrant 1 (Top-Right): **Stars** (Scale & Protect) — Green.
    - Quadrant 2 (Top-Left): **Scalable Gems** (Budget Infusion) — Blue.
    - Quadrant 3 (Bottom-Right): **Question Marks** (Creative Refresh) — Amber.
    - Quadrant 4 (Bottom-Left): **Cut Candidates** (Slash Budget) — Crimson.
- **Row 2 (Action Table):**
  - Campaign Name, Channel, Objective, Spend, Revenue, CAC, ROAS, Quadrant, Tactical Directive.

### Page 5: Budget Optimization & Diminishing Returns Simulator
- **Header:** Title: "Attribution-Adjusted Budget Reallocation & Incremental Revenue Projection"
- **Row 1 (KPI Impact Cards):**
  1. Current Total Budget: `$426,418`
  2. Recommended Reallocated Budget: `$426,418` (Zero Net Budget Increase)
  3. Base Projected Incremental Revenue: `+$224,908` (+13.3% Paid Lift)
  4. Projected Portfolio ROAS: `4.49x` (vs `3.96x` baseline)
- **Row 2 (Visuals):**
  - **Tornado / Bi-Directional Bar Chart:** Budget Shift ($ and %) by Channel (Search -$58.4K vs Email +$21.3K, Referral +$20.3K, Display +$12.3K, Social +$4.6K).
  - **Response Curves Visual:** Modeled Diminishing Return Curves (Hill saturation fit) showing current spend point vs optimal allocation point.
- **Row 3 (Scenario Table):**
  - Channel, Current Spend, Proposed Spend, Delta $, Delta %, Base Revenue, Low Scenario (-10%), High Scenario (+15%), Incrementality Test Market pairings.

---

## 5. Manual steps (about 2 hours)

Follow these exact steps to assemble the `.pbix` file from scratch:

1. **Phase 1: Ingest CSV Data (15 minutes)**
   - Open Power BI Desktop $\to$ Home $\to$ Get Data $\to$ Text/CSV.
   - Import each table from `data/powerbi_exports/`: `dim_channel`, `dim_campaign`, `dim_customer`, `dim_date`, `fact_touchpoints`, `fact_conversions`, `fact_daily_spend`, `attribution_master_comparison`, `budget_hill_optimization`, `kpi_campaign_ranking`, and `clv_predictive_summary`.
   - Verify column types match `data/powerbi_exports/relationships.md`.
2. **Phase 2: Build Relationships (15 minutes)**
   - Switch to **Model View**.
   - Connect the star-schema foreign keys listed in Section 2.
   - Verify all active relationships show `1:*` cardinality.
3. **Phase 3: Write DAX Measures (30 minutes)**
   - Create table `_Measures` and create all measures from Section 3.
   - Create disconnected parameter table `dim_attribution_model` using DAX `DATATABLE`.
4. **Phase 4: Construct Canvas Pages (45 minutes)**
   - Page 1: Executive KPI Cards, Clustered Bar Chart, Channel Matrix.
   - Page 2: Journey Latency Donut, Path Length Histogram, Top 8 Paths Table.
   - Page 3: Model Slicer dropdown, Model Comparison Clustered Bar, Revenue Shift Waterfall.
   - Page 4: Campaign Scatter Quadrant (Revenue vs ROAS), Tactical Action Matrix.
   - Page 5: Budget Shift Waterfall, Marginal ROAS Table, Scenario Uplift Cards.
5. **Phase 5: Quality Assurance & Cross-Check (15 minutes)**
   - Follow `dashboard/POWERBI_BUILD_CHECKLIST.md`.
   - Verify Total Paid Spend = **$426,418.04**, Total Revenue = **$2,374,133.70**, Blended ROAS = **3.96x**.
   - Save file as `dashboard/Grito_Marketing_Attribution.pbix`.
