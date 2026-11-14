# Marketing KPI Definitions & Mathematical Formulas

**Project:** Multi-Channel Marketing Analytics & Attribution Framework  
**Entity:** Grito Labs  
**Author:** J Nikhil ([GitHub: JNikhil11](https://github.com/JNikhil11))  
**Document Version:** 2.0  

---

## 1. Customer vs. Order Terminology Standards

To maintain analytical rigor, this framework distinguishes strictly between customer-level and transaction-level entities:

| Metric Entity | Count | Definition | Strategic Scope |
| :--- | :--- | :--- | :--- |
| **Unique Students (Customers)** | **2,450** | Distinct individual students acquired through marketing touchpoints. | Denominator for Headline CAC, Conversion Rate, and Journey Analysis. |
| **New-Customer Orders** | **2,450** | Initial paid course enrollments resulting from acquired students. | Scope of Multi-Touch Attribution Models ($2,382,514.60 revenue). |
| **Repeat Orders** | **294** | Follow-on modular or advanced course purchases by existing alumni. | Scope of Customer Lifetime Value & Retention ($282,306.00 revenue). |
| **Total Orders (Enrollments)** | **2,744** | Sum of all transactions completed across the 90-day observation window. | Denominator for Cost per Order ($2,664,820.60 lifetime order revenue). |

---

## 2. Top-of-Funnel & Engagement Metrics

### 2.1 Click-Through Rate (CTR)
- **Definition:** The percentage of ad impressions that resulted in a user click.
- **Formula:**
  $$\text{CTR} = \frac{\text{Total Clicks}}{\text{Total Impressions}} \times 100\%$$
- **SQL Implementation:**
  ```sql
  ROUND(CAST(clicks AS REAL) / NULLIF(impressions, 0) * 100.0, 2) AS ctr_pct
  ```
- **Business Interpretation:** Measures creative resonance, thumbnail appeal, and targeting precision. Edtech benchmarks: Search (2.0%-5.0%), Social (0.8%-1.5%), Display (0.1%-0.4%).

### 2.2 Cost Per Click (CPC)
- **Definition:** The average advertising cost incurred for each click directed to the course landing page.
- **Formula:**
  $$\text{CPC} = \frac{\text{Total Media Spend}}{\text{Total Clicks}}$$
- **SQL Implementation:**
  ```sql
  ROUND(spend / NULLIF(clicks, 0), 2) AS cpc
  ```
- **Business Interpretation:** Reflects commercial auction competition. Search commands higher CPC ($9.54) due to immediate purchase intent compared to Paid Social ($5.51) and Display ($1.93).

---

## 3. Acquisition Efficiency Metrics

### 3.1 Headline Customer Acquisition Cost (CAC - Unique Students)
- **Definition:** The total advertising expenditure required to acquire one distinct new enrolled student. This is the **primary headline CAC** reported across all executive dashboards and financial reviews.
- **Formula:**
  $$\text{Headline CAC} = \frac{\text{Total Paid Media Spend}}{\text{Unique New Students Acquired}} = \frac{\$426,418.04}{2,450} = \$174.05$$
- **SQL Implementation:**
  ```sql
  ROUND(SUM(spend) / COUNT(DISTINCT customer_id), 2) AS headline_cac
  ```
- **Business Interpretation:** The foundational unit economic hurdle. Evaluated against Customer Lifetime Value (LTV) to determine business viability.

### 3.2 Cost Per Order (CPO / Cost per Enrollment)
- **Definition:** The blended advertising expenditure per transaction across all orders (initial + repeat).
- **Formula:**
  $$\text{Cost Per Order (CPO)} = \frac{\text{Total Paid Media Spend}}{\text{Total Orders Completed}} = \frac{\$426,418.04}{2,744} = \$155.40$$
- **SQL Implementation:**
  ```sql
  ROUND(SUM(spend) / COUNT(order_id), 2) AS cost_per_order
  ```
- **Business Interpretation:** Reflects order-level marketing friction. Lower than headline CAC because repeat orders amortize initial customer acquisition investment without incremental paid media spend.

### 3.3 Conversion Rate (CVR)
- **Definition:** The percentage of website visits/clicks that culminate in a course enrollment.
- **Formula:**
  $$\text{CVR} = \frac{\text{Total Enrolled Students}}{\text{Total Clicks}} \times 100\%$$
- **SQL Implementation:**
  ```sql
  ROUND(CAST(conversions AS REAL) / NULLIF(clicks, 0) * 100.0, 2) AS cvr_pct
  ```

---

## 4. Financial Return & Profitability Metrics

### 4.1 Return on Ad Spend (ROAS)
- **Definition:** Gross course enrollment revenue generated per dollar of paid media spend.
- **Formula:**
  $$\text{ROAS} = \frac{\text{Attributed Revenue}}{\text{Total Media Spend}}$$
- **Channel Benchmark Examples (Position-Based Attribution):**
  - **Paid Social:** $\$571,912.22 / \$142,951.06 = 4.00\text{x}$
  - **Display Ads:** $\$272,976.29 / \$51,626.47 = 5.29\text{x}$
  - **Paid Search:** $\$536,017.28 / \$198,410.22 = 2.70\text{x}$
  - **Email Marketing:** $\$191,562.81 / \$13,700.33 = 13.98\text{x}$
  - **Referral:** $\$117,069.24 / \$19,729.96 = 5.93\text{x}$
  - **Organic Search & Direct:** Spend = $\$0.00$ $\rightarrow$ ROAS reported as **N/A** (Unpaid organic asset).
  - **Blended Paid ROAS (Paid Channels Only):** $\$1,689,537.84 / \$426,418.04 = 3.96\text{x}$
  - **Total Portfolio Multiplier (All Attributed Revenue):** $\$2,382,514.60 / \$426,418.04 = 5.59\text{x}$

### 4.2 Marginal Return on Ad Spend (mROAS)
- **Definition:** The derivative of the channel revenue response curve with respect to spend:
  $$\text{mROAS}_i = \frac{dR_i(S_i)}{dS_i}$$
- **Significance in Allocation:** Under unconstrained optimal conditions, funds shift until $\text{mROAS}_i = \lambda$ across all channels. When bounds are binding, marginal ROAS diverges:
  - Constrained Min Bound (Search): $\text{mROAS} = 1.67\text{x}$
  - Constrained Max Capacity (Email): $\text{mROAS} = 4.91\text{x}$
  - Constrained Max Capacity (Referral): $\text{mROAS} = 2.61\text{x}$
  - Equalized Equilibrium (Social & Display): $\text{mROAS} = 1.82\text{x}$

---

## 5. Multi-Touch Journey & Funnel Role Metrics

### 5.1 Assist-to-Last-Click Ratio
- **Definition:** The ratio of non-converting assist touchpoints to last-click conversion touchpoints.
- **Formula:**
  $$\text{Assist-to-Last Ratio} = \frac{\sum \text{Assist Touches}}{\sum \text{Last Touches}}$$
- **Strategic Thresholds:**
  - $> 1.5$: **Top/Mid-Funnel Feeder / Influencer** (Paid Social: 2.1x, Display: 1.8x).
  - $0.8 - 1.5$: **Balanced Full-Funnel** (Organic Search, Referral).
  - $< 0.8$: **Bottom-Funnel Closer / Harvester** (Paid Search: 0.6x, Direct: 0.4x).

---

## 6. Customer Lifetime Value (CLV) & Unit Economics

### 6.1 Historical CLV
- **Definition:** Cumulative realized revenue across initial enrollment and subsequent repeat purchases:
  $$\text{Historical CLV} = \frac{\text{Total Lifetime Revenue}}{\text{Unique Students}} = \frac{\$2,664,820.60}{2,450} = \$1,087.68$$

### 6.2 Predictive 12-Month CLV (BG/NBD + Gamma-Gamma)
- **Definition:** Forward-looking expected value incorporating probability of being active and future transaction rates:
  $$\text{Predictive CLV} = \text{Realized Revenue} + \left( E[Y(12) \mid x, t_x, T] \times E[M \mid x, \bar{x}] \right)$$

### 6.3 LTV:CAC Ratio
- **Definition:** The ratio of realized or expected lifetime value to the headline customer acquisition cost:
  $$\text{LTV:CAC} = \frac{\text{Historical CLV}}{\text{Headline CAC}} = \frac{\$1,087.68}{\$174.05} = 6.25\text{x}$$
- **Executive Interpretation:**
  - Standard healthy edtech target is $3.0\text{x} - 5.0\text{x}$.
  - At $6.25\text{x}$, Grito Labs possesses substantial headroom to scale customer acquisition while remaining safely profitable.
