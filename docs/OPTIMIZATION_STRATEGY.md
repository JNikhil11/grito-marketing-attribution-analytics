# Executive Optimization Strategy & Capital Reallocation Report

**To:** Leadership Team & Investment Committee, Grito Labs  
**From:** J Nikhil ([GitHub: JNikhil11](https://github.com/JNikhil11))  
**Date:** November 2026  
**Subject:** Multi-Channel Attribution Findings & Quantified Budget Optimization (Q4 2026 / Q1 2027)  
**Data Provenance:** Synthetic benchmark dataset generated to mimic realistic EdTech multi-channel marketing behavior (Seed 42, 16,000 student journeys, 40,806 touchpoints, 2,450 new students, 2,744 total orders).  

---

## 1. Executive Summary & Core Opportunity

Over the analyzed 90-day operating cycle, Grito Labs invested **$426,418.04** in direct digital advertising across five paid channels (Paid Search, Paid Social, Display Ads, Email Marketing, and Referral). This capital generated **2,450 newly enrolled students** and **$2,382,514.60 in initial course enrollment revenue**, representing a blended paid Return on Ad Spend (ROAS) of **3.96x** across paid channels and **5.59x** portfolio multiplier against all initial course revenue. Follow-on modular certifications by alumni generated an additional **294 repeat orders ($282,306.00)**, bringing total realized lifetime revenue to **$2,664,820.60** across **2,744 total orders**.

Unit economics are robust:
- **Headline Customer Acquisition Cost (CAC):** **$174.05** per unique new enrolled student ($426,418.04 / 2,450 students).
- **Cost Per Order (CPO):** **$155.40** across all transactions ($426,418.04 / 2,744 orders).
- **Customer Lifetime Value (Historical CLV):** **$1,087.68** per student, yielding an exceptional **6.25x LTV:CAC ratio**.

However, cross-channel attribution modeling reveals severe capital misallocation driven by legacy reliance on Last-Touch Attribution (LTA):
1. **Paid Social is Severely Undervalued:** Last-Touch attribution credits Paid Social with only \$387,351 in revenue. In reality, our multi-touch Position-Based (U-Shaped) model proves that Paid Social initiates or assists in over **$571,912.22** of initial student revenue (+47.6% credit expansion, +$184,561 lift). Paid Social acquires qualified prospective students at a CAC of **$146.47**—significantly more efficient than Paid Search ($367.33).
2. **Paid Search Sits in Severe Diminishing Returns:** Paid Search absorbs 46.5% of the total marketing budget ($198,410.22) but delivers the lowest paid ROAS (**2.55x** LTA, **2.70x** Position-Based) and highest CAC ($367.33). High non-brand keyword bids ("data analytics bootcamp", "python certification") have pushed Search deep into flat marginal returns (Marginal ROAS = **1.67x**).
3. **Email Marketing & Referral Are Starved for Capital:** Automated email drip campaigns deliver an efficient **13.98x Position-Based ROAS** and \$38.27 CAC, yet received only 3.2% of the budget ($13,700.33). Referral drives a 5.93x ROAS ($132.42 CAC) but received only $19,729.96.

### The Quantified Recommendation
By reallocating capital across channels under a **strictly fixed budget of $426,418.04** ($0.00 net change), Grito Labs can unlock:
- **+$224,908.02 in Net Incremental Revenue (+13.3% paid top-line lift)** in the Base Case (Projected Paid Revenue: **$1,914,445.86**).
- An expansion of blended paid ROAS from **3.96x to 4.49x**.
- Symmetrical scenario outcomes on incremental lift: **Low Case (0.75x lift): +$168,681.01** ($1,858,218.85 projected paid revenue) vs. **High Case (1.25x lift): +$281,135.03** ($1,970,672.87 projected paid revenue).

---

## 2. The Attribution Revelation: Why Last-Touch Misleads

In EdTech, students evaluate course curricula, career placement statistics, and tuition plans over an **average 5.2-day consideration window**. Exactly **69.1% of all enrollments** (1,693 of 2,450 new students) involve two or more distinct marketing touchpoints across multiple channels.

When marketing performance is evaluated through Last-Touch Attribution:
- **Direct Traffic Receives False Credit:** Direct navigation accounts for \$554,397 in Last-Touch revenue. However, multi-touch analysis proves that downstream students convert via direct bookmarks after upstream discovery. In Position-Based attribution, Direct drops to \$368,226 (-33.6%), rightfully transferring credit to top-of-funnel channels.
- **Top-of-Funnel Origination is Penalized:** Display Ads (Assist-to-Last ratio of **2.61**) and Paid Social (Assist-to-Last ratio of **2.14**) act as primary pipeline feeders. Cutting Paid Social spend based on Last-Touch CAC would collapse downstream organic and direct conversions within two to three weeks.

### Attribution Model Comparison Matrix (All Attributed to Initial Students: $2,382,514.60)

| Marketing Channel | Media Spend | First-Touch | Last-Touch | Linear | Time-Decay | Position-Based | Markov Chain | Shapley Value | LTA ROAS | U-Shaped ROAS | Credit Shift vs LTA |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Paid Search** | \$198,410.22 | \$577,728 | \$506,125 | \$530,926 | \$527,672 | \$536,017 | \$499,497 | \$528,489 | 2.55x | 2.70x | +5.9% |
| **Paid Social** | \$142,951.06 | \$792,931 | \$387,351 | \$544,134 | \$522,162 | **\$571,912** | **\$483,974** | **\$542,994** | 2.71x | **4.00x** | **+47.6%** |
| **Display Ads** | \$51,626.47 | \$364,869 | \$198,153 | \$259,603 | \$250,867 | \$272,976 | \$256,108 | \$268,434 | 3.84x | 5.29x | +37.8% |
| **Email Marketing** | \$13,700.33 | \$0 | \$333,974 | \$220,760 | \$237,497 | \$191,563 | \$315,430 | \$229,022 | 24.38x | 13.98x | -42.6% |
| **Referral** | \$19,729.96 | \$137,754 | \$100,379 | \$114,991 | \$113,800 | \$117,069 | \$122,710 | \$123,029 | 5.09x | 5.93x | +16.6% |
| **Organic Search** | \$0.00 | \$351,110 | \$302,134 | \$321,479 | \$319,038 | \$324,750 | \$319,226 | \$329,585 | N/A | N/A | +7.5% |
| **Direct** | \$0.00 | \$158,122 | \$554,397 | \$390,621 | \$411,480 | \$368,226 | \$385,570 | \$360,962 | N/A | N/A | -33.6% |
| **TOTAL** | **\$426,418.04** | **\$2,382,515** | **\$2,382,515** | **\$2,382,515** | **\$2,382,515** | **\$2,382,515** | **\$2,382,515** | **\$2,382,515** | **3.96x** | **3.96x** | **Reconciled ($0.00)** |

*Note: Blended Paid ROAS is 3.96x on current paid channel revenue ($1,689,537.84 / $426,418.04). Unattributed revenue is $0.00 across all models (100% of converting journeys have touchpoints within the 30-day lookback window).*

---

## 3. Diminishing Returns, Hill Saturation & Constraint Status

Every additional dollar spent in an advertising channel produces less incremental revenue than the prior dollar. Using econometrically calibrated **Hill Saturation Curves**:
$$R_i(S_i) = \frac{R_{\max, i} \cdot S_i^{\alpha_i}}{S_{50, i}^{\alpha_i} + S_i^{\alpha_i}}$$

### Calibration Methodology:
1. **$R_{\max}$ (Channel Revenue Capacity):** Estimated from market addressable audience size and historical conversion ceilings per channel.
2. **$S_{50}$ (Half-Saturation Spend):** Spend level where 50% of maximum potential revenue is attained, derived from historical acquisition velocity and auction saturation points.
3. **$\alpha$ (Hill Shape Exponent):** Sets curvature steepness ($\alpha = 1.05 - 1.25$), calibrated to empirical response elasticity in EdTech auctions.
4. **Baseline Alignment:** Curve outputs are normalized such that $R(S_{\text{current}})$ reproduces current baseline multi-touch attributed revenue exactly.

### Marginal ROAS and Boundary Constraints:
The optimization maximizes total portfolio revenue subject to a fixed total budget ($\sum S_i = \$426,418.04$) and managerial operational boundaries:
- **Paid Search:** Pinned at lower operational limit ($S_{\min} = \$140,000.00$). Marginal ROAS at boundary = **1.67x**. Further cuts are prohibited to protect core brand keyword defense.
- **Email Marketing:** Pinned at list capacity limit ($S_{\max} = \$35,000.00$). Marginal ROAS at boundary = **4.91x**. Further expansion is restricted to avoid email fatigue and subscriber churn.
- **Referral:** Pinned at organic community capacity limit ($S_{\max} = \$40,000.00$). Marginal ROAS at boundary = **2.61x**.
- **Paid Social & Display Ads (Unconstrained Equilibrium):** Both unconstrained channels freely adjust until their marginal returns reach exact equilibrium at **1.82x**.

**Summary Finding:** "Constrained reallocation (marginal ROAS spread: 1.67x to 4.91x; unconstrained channels equalized at 1.82x)."

---

## 4. The Recommended Capital Reallocation

We propose the following zero-sum reallocation of the **$426,418.04** quarterly budget:

| Marketing Channel | Current Spend | Recommended Spend | Dollar Shift ($\Delta \$) | Percent Shift ($\Delta \%$) | Current ROAS | Projected ROAS | Marginal ROAS | Constraint Status | Projected Base Revenue |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Paid Search** | \$198,410.22 | \$140,010.22 | **-\$58,400.00** | **-29.4%** | 2.70x | 2.96x | 1.67x | Lower Bound Constrained (Min Cap) | \$413,974.76 |
| **Paid Social** | \$142,951.06 | \$147,551.06 | **+\$4,600.00** | **+3.2%** | 4.00x | 3.96x | 1.82x | Unconstrained Equilibrium | \$583,690.26 |
| **Email Marketing** | \$13,700.33 | \$34,950.33 | **+\$21,250.00** | **+155.1%** | 13.98x | 11.58x | 4.91x | Upper Bound Constrained (Capacity Cap) | \$404,773.49 |
| **Display Ads** | \$51,626.47 | \$63,926.47 | **+\$12,300.00** | **+23.8%** | 5.29x | 4.87x | 1.82x | Unconstrained Equilibrium | \$311,334.44 |
| **Referral** | \$19,729.96 | \$39,979.96 | **+\$20,250.00** | **+102.6%** | 5.93x | 5.02x | 2.61x | Upper Bound Constrained (Capacity Cap) | \$200,672.91 |
| **TOTAL** | **\$426,418.04** | **\$426,418.04** | **\$0.00** | **0.0%** | **3.96x** | **4.49x** | **Spread: 1.67x–4.91x** | **Zero-Sum Balanced Reallocation** | **\$1,914,445.86** |

### Projected Financial Outcomes Across Scenarios (Symmetrical Bounds on Incremental Lift)
- **Base Case (1.00x Expected Lift):** Total paid channel revenue expands from \$1,689,537.84 to **\$1,914,445.86**, delivering a **net incremental revenue gain of +$224,908.02 (+13.3% lift)**.
- **Low Case (0.75x Base Lift):** Accounting for -25% market friction, reallocation delivers **+$168,681.01** in net incremental gain (**$1,858,218.85** total paid revenue; 4.36x ROAS).
- **High Case (1.25x Base Lift):** With +25% creative upside and list expansion, reallocation delivers **+$281,135.03** in net incremental gain (**$1,970,672.87** total paid revenue; 4.62x ROAS).

---

## 5. Campaign Winners & Cut Candidates (Quadrant Matrix)

Our multi-touch campaign scoring establishes four distinct operational categories:

1. **Portfolio Stars (Scale & Protect +20%):**
   - `SOC_Meta_Prospecting` (\$188.5K Rev, 7.50x ROAS): Top-of-funnel engine. Protect budget and refresh video testimonials bi-weekly.
   - `PS_Brand_Core` (\$182.5K Rev, 7.06x ROAS): Defend 100% impression share against competitor bidding.
   - `DIS_Retargeting_Dynamic` (\$137.1K Rev, 7.32x ROAS): Highly profitable bottom-funnel nudge.
2. **Scalable Hidden Gems (Budget Infusion):**
   - `EM_Alumni_Upsell` (\$60.5K Rev, 16.04x ROAS): Drip campaigns for advanced second certifications.
   - `EM_Webinar_Nurture` (\$65.0K Rev, 13.84x ROAS): High conversion from webinar attendee workflows.
   - `REF_Student_Advocate` (\$117.1K Rev, 5.93x ROAS): Scale referral incentives and student ambassador perks.
3. **Question Marks (Creative & Targeting Optimization):**
   - `PS_NonBrand_Analytics` (\$173.3K Rev, 2.43x ROAS): Prune negative keywords for broad informational queries.
   - `SOC_LinkedIn_Prof` (\$206.9K Rev, 2.31x ROAS): High B2B CPC ($9+); refocus on targeted job-title segments.
4. **Cut Candidates (Immediate Defunding):**
   - `PS_Competitor_Intercept` (\$101.2K Spend, 1.78x ROAS, \$550.21 CAC): Inefficient keyword auction bidding; reduce budget by 50% to fund high-ROAS email and referral initiatives.

---

## 6. Execution Roadmap & Incrementality Test Design

To de-risk the $58.4K budget shift from Search to Email/Referral, we recommend a **4-Week Matched-Market Geo-Holdout Test**:
- **Test Group (Shift Applied):** Dallas-Fort Worth, San Francisco, Chicago, Atlanta.
- **Control Group (Status Quo Spend):** Austin, Seattle, Minneapolis, Charlotte.
- **Evaluation Metric:** Difference-in-Differences (DiD) estimation on paid enrollments and incremental ROAS.
- **Guardrail Stop-Loss:** If CAC exceeds +20% for two consecutive weeks in any market, pause reallocation immediately.
