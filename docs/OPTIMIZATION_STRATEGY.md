# Executive Optimization Strategy & Capital Reallocation Report

**To:** Leadership Team & Investment Committee, Grito Labs  
**From:** Marketing Analytics Lead & Data Engineering Practice  
**Date:** November 2026  
**Subject:** Multi-Channel Attribution Findings & Quantified Budget Optimization (Q4 2026 / Q1 2027)  
**Data Provenance:** Synthetic benchmark dataset calibrated to realistic EdTech customer journeys (Seed 42, 16,000 students, 40,806 touchpoints, 2,744 orders).

---

## 1. Executive Summary & Core Opportunity

Over the analyzed 90-day operating cycle, Grito Labs invested **$426,418.04** in direct digital advertising across five paid channels (Paid Search, Paid Social, Display Ads, Email Marketing, and Referral). This capital generated **2,744 enrolled students** and **$2,374,133.70 in gross course revenue**, representing a blended portfolio Return on Ad Spend (ROAS) of **3.96x** and an average Customer Acquisition Cost (CAC) of **$155.40** across paid channels (Spend represents **17.96%** of total revenue).

However, our multi-touch attribution modeling reveals a severe capital misallocation driven by legacy reliance on Last-Touch Attribution (LTA):
1. **Paid Social is Severely Undervalued:** Last-Touch attribution credits Paid Social with only \$387,351 in revenue. In reality, our multi-touch Position-Based (U-Shaped) model proves that Paid Social initiates or assists in over **$571,912** of student revenue (+47.6% credit expansion, +$184,561 lift). Paid Social acquires qualified prospective students at a CAC of **$178.47**—nearly half the cost of Paid Search ($336.86).
2. **Paid Search Sits in Severe Diminishing Returns:** Paid Search absorbs 46.5% of the total marketing budget ($198,410.22) but delivers the lowest paid ROAS (**2.55x** LTA, **2.70x** Position-Based) and highest CAC ($336.86). High non-brand keyword bids ("data analytics masters", "best business analytics bootcamp") have pushed Search deep into flat marginal returns (Marginal ROAS = **1.67x**).
3. **Email Marketing & Referral Are Starved for Capital:** Automated email drip campaigns deliver an efficient **13.98x Position-Based ROAS** and \$38.27 CAC, yet received only 3.2% of the budget ($13,700.33). Referral drives a 5.93x ROAS ($132.42 CAC) but received only $19,729.96.

### The Quantified Recommendation
By reallocating capital across channels under a **strictly fixed budget of $426,418.04** ($0.00 net change), Grito Labs can unlock:
- **+$224,908.02 in Net Incremental Revenue (+13.3% paid top-line lift)** in the Base Case.
- An expansion of blended paid ROAS from **3.96x to 4.49x**.
- A reduction in blended paid CAC to **$137.15**.
- A conservative Low Scenario (-10% friction) of **+$33,462.83** and an optimistic High Scenario (+15% upside) of **+$512,074.30**.

---

## 2. The Attribution Revelation: Why Last-Touch Misleads

In EdTech, students evaluate course curricula, career placement statistics, and tuition plans over a **5.2-day average gestation window**. Exactly **69.1% of all enrollments** (1,897 of 2,744) involve two or more distinct marketing interactions across multiple devices.

When marketing performance is evaluated through Last-Touch Attribution:
- **Direct Traffic Receives False Credit:** Direct navigation accounts for \$554,397 in Last-Touch revenue. However, multi-touch analysis proves that downstream students convert via direct bookmarks after upstream discovery. In Position-Based attribution, Direct drops to \$368,227 (-33.6%), rightfully transferring credit to top-of-funnel channels.
- **Top-of-Funnel Origination is Penalized:** Display Ads (Assist-to-Last ratio of **2.61**) and Paid Social (Assist-to-Last ratio of **2.14**) act as primary pipeline feeders. Cutting Paid Social spend based on Last-Touch CAC would collapse downstream organic and direct conversions within two to three weeks.

### Attribution Model Comparison Matrix

| Marketing Channel | Media Spend | Last-Touch Revenue | U-Shaped (40-20-40) | Markov Chain Revenue | LTA ROAS | U-Shaped ROAS | Credit Shift vs LTA |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Paid Search** | \$198,410.22 | \$506,125.30 | \$536,017.28 | \$499,496.86 | 2.55x | 2.70x | +5.9% |
| **Paid Social** | \$142,951.06 | \$387,351.40 | **\$571,912.22** | **\$483,973.77** | 2.71x | **4.00x** | **+47.6%** |
| **Display Ads** | \$51,626.47 | \$198,153.30 | \$272,976.29 | \$256,107.78 | 3.84x | 5.29x | +37.8% |
| **Email Marketing** | \$13,700.33 | \$333,974.30 | \$191,562.81 | \$315,430.01 | 24.38x | 13.98x | -42.6% |
| **Referral** | \$19,729.96 | \$100,378.90 | \$117,069.24 | \$122,710.09 | 5.09x | 5.93x | +16.6% |
| **Organic Search** | \$0.00 | \$302,134.50 | \$324,750.26 | \$319,225.76 | N/A | N/A | +7.5% |
| **Direct** | \$0.00 | \$554,396.90 | \$368,226.50 | \$385,570.34 | N/A | N/A | -33.6% |
| **TOTAL** | **\$426,418.04** | **\$2,374,133.70** | **\$2,374,133.70** | **\$2,374,133.70** | **3.96x** | **3.96x** | **Reconciled ($0.00)** |

---

## 3. Diminishing Returns & Marginal ROAS Equilibrium

Every additional dollar spent in an advertising channel produces less incremental revenue than the prior dollar. Using our econometrically fitted **Hill Saturation Curves** ($R(S) = \frac{R_{\max} S^\alpha}{S_{50}^\alpha + S^\alpha}$), we compute the **Marginal ROAS ($\frac{dR}{dS}$)** at current spending levels:

- **Paid Search:** Marginal ROAS = **1.67x** ($R_{\max}=\$950\text{K}, S_{50}=\$280\text{K}$). High non-brand bidding creates severe diminishing returns.
- **Paid Social:** Marginal ROAS = **1.82x** ($R_{\max}=\$980\text{K}, S_{50}=\$190\text{K}$). Strong efficiency in mid-funnel retargeting.
- **Display Ads:** Marginal ROAS = **1.82x** ($R_{\max}=\$450\text{K}, S_{50}=\$80\text{K}$). Room for scaling dynamic retargeting.
- **Referral:** Marginal ROAS = **2.61x** ($R_{\max}=\$350\text{K}, S_{50}=\$45\text{K}$). High word-of-mouth elasticity.
- **Email Marketing:** Marginal ROAS = **4.91x** ($R_{\max}=\$550\text{K}, S_{50}=\$35\text{K}$). Highest marginal productivity across the portfolio.

**The Economic Rule:** Profit maximization requires shifting capital until Marginal ROAS is equalized across all channels. Continuing to over-fund Paid Search at 1.67x marginal return while starving Email (4.91x) and Referral (2.61x) leaves **$224,908.02** on the table.

---

## 4. The Recommended Capital Reallocation

We propose the following zero-sum reallocation of the **$426,418.04** quarterly budget:

| Marketing Channel | Current Spend | Recommended Spend | Dollar Shift ($\Delta \$) | Percent Shift ($\Delta \%$) | Current ROAS | Projected ROAS | Marginal ROAS | Projected Base Revenue |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Paid Search** | \$198,410.22 | \$140,010.22 | **-\$58,400.00** | **-29.4%** | 2.70x | 2.96x | 1.67x | \$413,974.76 |
| **Paid Social** | \$142,951.06 | \$147,551.06 | **+\$4,600.00** | **+3.2%** | 4.00x | 3.96x | 1.82x | \$583,690.26 |
| **Email Marketing** | \$13,700.33 | \$34,950.33 | **+\$21,250.00** | **+155.1%** | 13.98x | 11.58x | 4.91x | \$404,773.49 |
| **Display Ads** | \$51,626.47 | \$63,926.47 | **+\$12,300.00** | **+23.8%** | 5.29x | 4.87x | 1.82x | \$311,334.44 |
| **Referral** | \$19,729.96 | \$39,979.96 | **+\$20,250.00** | **+102.6%** | 5.93x | 5.02x | 2.61x | \$200,672.91 |
| **TOTAL** | **\$426,418.04** | **\$426,418.04** | **\$0.00** | **0.0%** | **3.96x** | **4.49x** | **Balanced** | **\$1,914,446.46** |

### Projected Financial Outcomes Across Scenarios
- **Base Case (Expected Execution):** Total paid channel revenue rises from \$1,689,538.44 to **\$1,914,446.46**, producing a **net incremental revenue gain of +$224,908.02 (+13.3% lift)**.
- **Low Scenario (-10% Friction):** Reallocation delivers **+$33,462.83** in net incremental gain ($1,723,001.27 total paid revenue).
- **High Scenario (+15% Creative Upside):** Reallocation delivers **+$512,074.30** in net incremental gain ($2,201,612.74 total paid revenue).

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
   - `PS_NonBrand_Analytics` (\$173.3K Rev, 2.43x ROAS): Prune negative keywords for informational queries.
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
