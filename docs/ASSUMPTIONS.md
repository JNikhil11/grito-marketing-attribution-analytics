# Comprehensive Methodological & Data Assumptions

**Project:** Multi-Channel Marketing Analytics & Attribution Framework  
**Entity:** Grito Labs  
**Document Version:** 2.0 (Verified Seed 42 Run)  
**Data Provenance Notice:** Synthetic dataset generated to mimic realistic multi-channel marketing behavior (Seed 42), because public attribution datasets (e.g. Criteo 2017) host links have suffered bitrot/404 or require gated enterprise credentials. The synthetic generator guarantees 100% mathematical reproducibility, zero-leakage reconciliation, and realistic EdTech unit economics.

---

The analytical outputs, SQL queries, predictive CLV models, and budget optimization recommendations in this project rest upon the following 16 explicit, documented assumptions:

### 1. Data Integrity & Lookback Horizon
1. **30-Day Conversion Lookback Window:** A prospective student's journey is evaluated within a strict 30-day window preceding their conversion timestamp. Any touchpoint occurring $> 30.0$ days prior to enrollment is considered expired brand equity and excluded from attribution credit.
2. **Fixed 90-Day Telemetry Window:** The dataset spans August 1, 2026 to October 31, 2026 (92 active calendar days), representing a stable operating quarter free of macroeconomic disruptions.
3. **Cookie / Identity Graph Persistence:** We assume `customer_id` correctly resolves cross-device interactions through authenticated logins, syllabus downloads, form captures, and first-party cookies with zero identity fragmentation.

### 2. Funnel Definition & Conversion Events
4. **Primary Conversion Event:** Defined strictly as a paid course enrollment order (`conversion_cycle = 1`), carrying explicit transaction revenue in USD.
5. **Initial vs Repeat Purchases:** Initial acquisition attribution is calculated on `conversion_cycle = 1`. Repeat purchases (`conversion_cycle = 2+`) are captured for Customer Lifetime Value (CLV) and cohort retention modeling, but are not credited to initial media acquisition campaigns.
6. **Non-Converting Paths:** Visitors who interact with 1 or more touchpoints but never convert are retained in the transition dataset to ensure mathematically sound absorbing Markov matrices and Shapley coalition values.

### 3. Financial & Cost Accounting
7. **Currency & Inflation:** All financial values (spend, CPC, CAC, revenue, CLV) are denominated in United States Dollars ($ USD) with zero inflation adjustment over the 90-day period.
8. **Direct Media Cost Allocation:**
   - Paid Search: Paid per click ($9.54 blended CPC across brand and non-brand keywords; $198,410.22 total spend).
   - Paid Social: Paid per click and impressions ($5.51 blended CPC; $142,951.06 total spend).
   - Display Ads: Programmatic CPM and retargeting clicks ($1.93 blended CPC; $51,626.47 total spend).
   - Email Marketing: Infrastructure and nurture distribution expense ($0.78 blended CPC equivalent; $13,700.33 total spend).
   - Referral: Fixed partner commission / referral reward ($2.77 blended cost per click; $19,729.96 total spend).
   - Organic Search & Direct: Zero direct marginal media expense ($0.00). ROAS is formally documented as `N/A` (unpaid) rather than infinity, avoiding division-by-zero distortion.
9. **No Revenue Discounts Without Documentation:** Course list prices are $349 (Foundation), $999 (Bootcamp), and $2,199 (Executive Fellowship). Occasional promotional pricing (10% discount) is captured directly at the order level. Total verified revenue across 2,744 orders is **$2,382,514.60**.

### 4. Attribution Modeling Parameters
10. **Time-Decay Half-Life:** Fixed at $\tau = 7.0$ days. This reflects the empirical 5.2-day average consideration latency observed in the journey data.
11. **Position-Based (U-Shaped) Split:** 40% First Touch, 40% Last Touch, and 20% distributed uniformly across intermediate assists. Single-touch journeys receive 100%; two-touch journeys receive 50% each.
12. **Markov Chain First-Order Memory:** Customer transitions follow a first-order Markov process where the probability of the next interaction depends solely on the current state.
13. **Shapley Game Symmetry:** Channels are assumed to act as cooperative coalitional players without order bias in the characteristic function $v(S)$.

### 5. Diminishing Returns & Budget Optimization
14. **Hill Saturation Response:** Media channels follow an S-shaped Hill saturation curve ($R(S) = \frac{R_{\max} S^\alpha}{S_{50}^\alpha + S^\alpha}$).
15. **Fixed Total Budget Constraint:** Total quarterly paid marketing spend is capped at exactly **$426,418.04** (17.96% of total revenue). All recommended budget changes represent zero-sum capital reallocations across existing channels (net shift = **$0.00**).
16. **Execution Risk Bounds:** Projections incorporate a conservative **-10% Low Case** (creative fatigue, bid auction inflation) and a **+15% High Case** (improved landing page conversion rate).
