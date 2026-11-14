# End-to-End Analytical Methodology & Attribution Framework

**Project:** Multi-Channel Marketing Analytics & Attribution Framework  
**Author:** J Nikhil ([GitHub: JNikhil11](https://github.com/JNikhil11))  
**Client / Evaluator:** Grito Labs (EdTech Analytics & Decision Science)  
**Version:** 1.0 (Production Release)  

---

## 1. Executive Problem Statement & Analytical Objectives

In multi-channel marketing, investments are distributed across top-of-funnel brand awareness (Paid Social, Display Ads), mid-funnel lead nurturing (Email Marketing, Webinars), and bottom-of-funnel intent capture (Paid Search, Direct navigation). 

Traditional analytics relies predominantly on **Last-Touch Attribution (LTA)** because of its simplistic implementation in standard web analytics packages. However, in higher-ticket EdTech programs ($349 to $2,199 per student), customer journeys average 5.4 days and 3.1 touchpoints. Last-Touch attribution creates severe structural distortions:
1. It credits 100% of the sale to the closing click (often Direct or Brand Search).
2. It systematically undervalues upstream channels that introduce prospective students to the brand.
3. It misallocates capital by encouraging overbidding on brand search terms while starving top-of-funnel discovery campaigns.

This framework replaces myopic heuristics with a multi-touch attribution engine combining:
- **Five ANSI SQL Rule-Based Models** (First-Touch, Last-Touch, Linear, Time-Decay, Position-Based U-Shaped).
- **Two Algorithmic Data-Driven Models** (Markov Chain Removal Effects and Cooperative Game-Theoretic Shapley Values).
- **Closed-Form Customer Lifetime Value Modeling** (BG/NBD frequency/recency + Gamma-Gamma monetary value).
- **Econometric Budget Optimization** (Hill saturation response curves with equalized marginal ROAS).
- **A Matched-Market Geo-Holdout Test Plan** to de-risk capital reallocation.

---

## 2. Research & Data Engineering Architecture

```
+---------------------------------------------------------------------------------+
|                                DATA INGESTION                                  |
|   raw_touchpoints.csv  |  raw_conversions.csv  |  raw_daily_spend.csv          |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                       STAR-SCHEMA DATA WAREHOUSE (SQL)                          |
|   Dimensions: dim_channel, dim_campaign, dim_customer, dim_date                 |
|   Facts:      fact_touchpoints, fact_conversions, fact_daily_spend              |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                       CLEANING & JOURNEY SESSIONIZATION                         |
|   - 30-Day Pre-Conversion Lookback Window Filter                                |
|   - Deduplication, Temporal Integrity & Primary Key Uniqueness Audits           |
|   - Window Function Sessionization (ROW_NUMBER, LAG, LEAD, SUM OVER)            |
+---------------------------------------------------------------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
+-------------------------------------+ +-------------------------------------+
|      SQL ATTRIBUTION ENGINE         | |     PYTHON ALGORITHMIC ENGINE       |
|  - First-Touch (100% Originator)    | |  - Markov Chain Removal Effects     |
|  - Last-Touch (100% Closer)         | |  - Shapley Value (Game Theory)      |
|  - Linear (1/N Equal Weight)        | |  - BG/NBD + Gamma-Gamma CLV Model   |
|  - Time-Decay (7-Day Half-Life)     | |  - Hill Saturation Optimization     |
|  - Position-Based (40-20-40)        | |  - Sensitivity Analysis (Half-Life) |
+-------------------------------------+ +-------------------------------------+
                   |                                       |
                   +-------------------+-------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                         RECONCILIATION & AUDIT PASS                             |
|   Assert: Sum(Attributed Revenue) == Ground Truth Total Revenue ($2,382,514.60)  |
|   Assert: SQL Revenue Metrics == Python Revenue Metrics (Zero Discrepancy)      |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
|                         DECISION ARTIFACTS & OUTPUTS                            |
|   - Power BI CSV Exports (data/powerbi_exports/) & Power BI Spec                |
|   - Interactive Web Dashboard (dashboard/index.html & dashboard/app.py)         |
|   - Executive Presentation (PPTX & PDF in presentation/)                        |
|   - Quantified Optimization Memo (docs/OPTIMIZATION_STRATEGY.md)                |
+---------------------------------------------------------------------------------+
```

---

## 3. Mathematical Foundations of Implemented Attribution Models

### 3.1 First-Touch Attribution (FTA)
Credits 100% of conversion value to the initial touchpoint in the journey:
$$w_{i} = \begin{cases} 1.0 & \text{if } i = 1 \\ 0.0 & \text{otherwise} \end{cases}$$
- **Role:** Identifies pure top-of-funnel customer originators.

### 3.2 Last-Touch Attribution (LTA)
Credits 100% of conversion value to the final touchpoint preceding conversion:
$$w_{i} = \begin{cases} 1.0 & \text{if } i = N \\ 0.0 & \text{otherwise} \end{cases}$$
- **Role:** Identifies closing / conversion-harvesting channels.

### 3.3 Linear Attribution
Distributes credit evenly across all interactions in the journey:
$$w_{i} = \frac{1}{N}$$
- **Role:** Democratic baseline; prevents single-touch monopolization.

### 3.4 Time-Decay Attribution
Applies exponential weighting prioritizing touchpoints closer to the conversion moment:
$$\tilde{w}_i = 2^{-\frac{\Delta t_i}{\tau}} = \exp\left( -\frac{\ln(2) \cdot \Delta t_i}{\tau} \right), \quad w_i = \frac{\tilde{w}_i}{\sum_{j=1}^N \tilde{w}_j}$$
where $\Delta t_i$ is the days before conversion, and $\tau = 7.0$ days is the calibrated half-life.
- **Justification for 7-Day Half-Life:** In EdTech, consideration spans an average of 5.4 days. Touchpoints occurring within 7 days carry more than double the weight of touchpoints occurring 14+ days prior.

### 3.5 Position-Based (U-Shaped) Attribution
Allocates 40% to first touch, 40% to last touch, and distributes the remaining 20% evenly across middle assist interactions:
$$w_i = \begin{cases} 1.0 & \text{if } N = 1 \\ 0.50 & \text{if } N = 2 \\ 0.40 & \text{if } i \in \{1, N\} \text{ and } N \ge 3 \\ \frac{0.20}{N - 2} & \text{if } 1 < i < N \text{ and } N \ge 3 \end{cases}$$
- **Role:** Recommended primary operational model; rewards both origination and conversion while sustaining mid-funnel nurture.

### 3.6 Data-Driven Markov Chain Model (Removal Effects)
Models customer journeys as a stochastic transition graph across states $S = \{\text{START}, C_1, \dots, C_K, \text{CONVERSION}, \text{NULL}\}$.
1. Transition probabilities are estimated from empirical journey paths:
   $$P_{ij} = \frac{n_{ij}}{\sum_k n_{ik}}$$
2. The overall baseline conversion probability $P(\text{Conv})$ is computed via absorbing Markov matrix algebra.
3. For channel $C_k$, the transition matrix is modified by removing $C_k$ (diverting all incoming edges to `NULL`), yielding $P(\text{Conv} \mid \setminus C_k)$.
4. The Removal Effect is calculated:
   $$\text{Removal Effect}(C_k) = \frac{P(\text{Conv}) - P(\text{Conv} \mid \setminus C_k)}{P(\text{Conv})}$$
5. Removal effects are normalized to attribute conversions and revenue:
   $$w(C_k) = \frac{\text{Removal Effect}(C_k)}{\sum_j \text{Removal Effect}(C_j)}$$

### 3.7 Data-Driven Shapley Value (Cooperative Game Theory)
Treats channels as players in a cooperative game where characteristic function $v(S)$ represents the conversion rate of journeys involving subset $S$.
The marginal contribution is averaged over all possible permutations:
$$\phi_i(v) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(|N| - |S| - 1)!}{|N|!} \left[ v(S \cup \{i\}) - v(S) \right]$$

---

## 4. Diminishing Returns & Response Curve Optimization

Channel spend does not produce linear returns; ad fatigue and audience saturation cause diminishing marginal returns.
We model each channel's revenue response using the **Hill Saturation Equation**:
$$R_i(S_i) = \frac{R_{\max, i} \cdot S_i^\alpha}{S_{50, i}^\alpha + S_i^\alpha}$$
where:
- $R_{\max, i}$ is the maximum addressable revenue ceiling for channel $i$.
- $S_{50, i}$ is the half-saturation spend level (spend required to generate $50\%$ of maximum revenue).
- $\alpha \approx 1.1 - 1.2$ represents curve steepness / initial scale efficiency.

The portfolio budget allocation problem is formulated as:
$$\max_{\{S_i\}} \sum_{i=1}^K R_i(S_i) \quad \text{subject to} \quad \sum_{i=1}^K S_i = B_{\text{total}}, \quad S_{i,\min} \le S_i \le S_{i,\max}$$

At optimality (by KKT conditions), marginal ROAS is equalized across all unconstrained channels:
$$\frac{dR_1}{dS_1} = \frac{dR_2}{dS_2} = \dots = \frac{dR_K}{dS_K} = \lambda$$

Any channel with $\frac{dR_i}{dS_i} > \lambda$ is receiving too little capital; any channel with $\frac{dR_i}{dS_i} < \lambda$ is receiving too much capital.
