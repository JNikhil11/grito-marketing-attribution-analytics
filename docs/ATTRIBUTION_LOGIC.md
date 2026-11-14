# Grito Labs Multi-Touch Attribution Logic & Mathematical Reference

**Document Version:** 2.0  
**Author:** J Nikhil ([GitHub: JNikhil11](https://github.com/JNikhil11))  
**Target Audience:** Marketing Analytics Leads, Data Engineers, and Financial Controllers  

---

## 1. Overview of Attribution Paradigms

Marketing attribution is the science of assigning credit for a business conversion to touchpoints encountered along a prospective customer's path to purchase.

Models are classified into two broad families:
1. **Rule-Based (Heuristic) Models:** Pre-determined mathematical rules applied uniformly across all journeys (First-Touch, Last-Touch, Linear, Time-Decay, Position-Based).
2. **Data-Driven (Algorithmic) Models:** Credit derived probabilistically from observed behavioral path sequences, removal effects, and cooperative game theory (Markov Chains, Shapley Values).

---

## 2. Worked Example on a Sample Student Journey

To demonstrate the mathematical divergence across models, consider a prospective Grito Labs student who enrolls in the **Marketing Analytics Bootcamp ($999.00)** through the following 4-touchpoint journey:

| Step | Interaction Timestamp | Days Before Conversion ($\Delta t_i$) | Channel Encountered | Interaction Type | Media Cost |
| :---: | :--- | :---: | :--- | :---: | :---: |
| **$t_1$** | Oct 10, 2026 10:00 AM | **14.0 days** | **Paid Social** (Instagram ad) | Click | \$1.45 |
| **$t_2$** | Oct 16, 2026 03:00 PM | **8.0 days**  | **Display Ads** (Retargeting banner) | Impression | \$0.02 |
| **$t_3$** | Oct 21, 2026 07:00 PM | **3.0 days**  | **Email Marketing** (Free webinar invite) | Click | \$0.05 |
| **$t_4$** | Oct 24, 2026 02:30 PM | **0.0 days**  | **Paid Search** (Google brand search) | Click | \$2.85 |
| **CONV** | Oct 24, 2026 03:00 PM | **0.0 days** | **ENROLLMENT COMPLETED** | Transaction | **Revenue: $999.00** |

---

### Step-by-Step Weight & Credit Calculation

#### 1. First-Touch Attribution (FTA)
- **Rule:** 100% to touchpoint 1.
- **Weights:** $w_1 = 1.0, \quad w_2 = 0.0, \quad w_3 = 0.0, \quad w_4 = 0.0$
- **Attributed Revenue:** Paid Social: **$999.00**, Display: $0.00, Email: $0.00, Search: $0.00.

#### 2. Last-Touch Attribution (LTA)
- **Rule:** 100% to touchpoint 4.
- **Weights:** $w_1 = 0.0, \quad w_2 = 0.0, \quad w_3 = 0.0, \quad w_4 = 1.0$
- **Attributed Revenue:** Paid Social: $0.00, Display: $0.00, Email: $0.00, Search: **$999.00**.

#### 3. Linear Attribution
- **Rule:** Equal distribution: $w_i = 1 / N = 1 / 4 = 0.25$.
- **Weights:** $w_1 = 0.25, \quad w_2 = 0.25, \quad w_3 = 0.25, \quad w_4 = 0.25$
- **Attributed Revenue:** All four channels receive **$249.75** (25.0%).

#### 4. Time-Decay Attribution (7-Day Half-Life: $\tau = 7.0$)
- **Formula:** $\tilde{w}_i = 2^{-\frac{\Delta t_i}{7.0}}$
  - $\tilde{w}_1 = 2^{-14.0 / 7.0} = 2^{-2} = 0.250$
  - $\tilde{w}_2 = 2^{-8.0 / 7.0} = 2^{-1.143} \approx 0.453$
  - $\tilde{w}_3 = 2^{-3.0 / 7.0} = 2^{-0.429} \approx 0.743$
  - $\tilde{w}_4 = 2^{-0.0 / 7.0} = 2^0 = 1.000$
  - Sum of Raw Weights: $\sum \tilde{w}_i = 0.250 + 0.453 + 0.743 + 1.000 = 2.446$
- **Normalized Weights:**
  - $w_1 = 0.250 / 2.446 = \mathbf{0.102}$ (10.2%) $\rightarrow$ Paid Social: **$101.90**
  - $w_2 = 0.453 / 2.446 = \mathbf{0.185}$ (18.5%) $\rightarrow$ Display Ads: **$184.82**
  - $w_3 = 0.743 / 2.446 = \mathbf{0.304}$ (30.4%) $\rightarrow$ Email Marketing: **$303.69**
  - $w_4 = 1.000 / 2.446 = \mathbf{0.409}$ (40.9%) $\rightarrow$ Paid Search: **$408.59**

#### 5. Position-Based (U-Shaped 40-20-40) Attribution
- **Rule:** $N = 4 \implies$ First Touch = 40%, Last Touch = 40%, Remaining 20% divided equally across the 2 middle touches ($20\% / 2 = 10\%$ each).
- **Weights:** $w_1 = 0.40, \quad w_2 = 0.10, \quad w_3 = 0.10, \quad w_4 = 0.40$
- **Attributed Revenue:** Paid Social: **$399.60**, Display Ads: **$99.90**, Email Marketing: **$99.90**, Paid Search: **$399.60**.

#### 6. Data-Driven Markov Chain Attribution (Graph Removal Effect)
- **Removal Effect Calculation across Portfolio:**
  - Removal effect $r_i = \frac{P(\text{conversion}) - P(\text{conversion} \setminus \{i\})}{P(\text{conversion})}$
  - Normalized weight $w_i = \frac{r_i}{\sum_j r_j}$
- **Attributed Revenue on Journey:** Paid Social: **$314.68**, Display Ads: **$188.81**, Email Marketing: **$237.76**, Paid Search: **$257.75**.

#### 7. Data-Driven Shapley Value Attribution (Game Theory)
- **Formulation:**
  $$\phi_i(v) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(|N| - |S| - 1)!}{|N|!} [v(S \cup \{i\}) - v(S)]$$
  where $N$ is the set of active marketing channels, $S$ is a coalition of channels, and $v(S)$ is the characteristic function measuring the total conversions or revenue supported exclusively by channels in $S$:
  $$v(S) = \sum_{J: \text{channels}(J) \subseteq S} \text{value}(J)$$
- **Axiomatic Properties Satisfied:**
  1. **Efficiency:** $\sum_{i \in N} \phi_i(v) = v(N) = \$2,382,514.60$ (Reconciles to the penny).
  2. **Monotonicity:** Adding a channel to any coalition never decreases the value ($v(S \cup \{i\}) \ge v(S)$), guaranteeing non-negative marginal contributions.
  3. **Symmetry:** Two channels that add identical value to all coalitions receive equal credit.
  4. **Null Player:** A channel contributing zero marginal value to all coalitions receives zero credit.
- **Email Marketing Worked Valuation:**
  In journey-level evaluation, Email Marketing participates in 588 multi-touch converting journeys. When Email joins coalitions lacking direct nurturing (e.g., $S = \{\text{Paid Social}, \text{Display Ads}\}$), it provides the essential mid-funnel activation that bridges discovery into conversion. Across all $2^{|N|} = 128$ channel coalitions, Email's weighted marginal contribution yields **$229,022.16 in attributed revenue** (247.83 conversions), resolving the previous non-monotonic rate artifact and accurately reflecting Email's high-leverage nurturing role.

---

## 3. Side-by-Side Comparison on the Sample Journey

| Marketing Channel | First-Touch | Last-Touch | Linear | Time-Decay (7d) | Position-Based (U-Shaped) | Markov Chain | Shapley Value |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Paid Social** | **$999.00** | $0.00 | $249.75 | $101.90 | **$399.60** | **$314.68** | **$298.42** |
| **Display Ads** | $0.00 | $0.00 | $249.75 | $184.82 | $99.90 | $188.81 | $162.15 |
| **Email Marketing** | $0.00 | $0.00 | $249.75 | $303.69 | $99.90 | $237.76 | **$241.18** |
| **Paid Search** | $0.00 | **$999.00** | $249.75 | $408.59 | **$399.60** | $257.75 | **$297.25** |
| **Total Attributed** | **$999.00** | **$999.00** | **$999.00** | **$999.00** | **$999.00** | **$999.00** | **$999.00** |

---

## 4. Master Portfolio Attribution Comparison ($2,382,514.60 Total)

| Channel | Spend | FTA Rev | LTA Rev | Linear Rev | Time-Decay Rev | U-Shaped Rev | Markov Rev | Shapley Rev | LTA ROAS | U-Shaped ROAS | Credit Shift vs LTA |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Paid Search** | \$198,410.22 | \$577,728 | \$506,125 | \$530,926 | \$527,672 | \$536,017 | \$499,497 | \$528,489 | 2.55x | 2.70x | +5.9% |
| **Paid Social** | \$142,951.06 | \$792,931 | \$387,351 | \$544,134 | \$522,162 | **\$571,912** | **\$483,974** | **\$542,994** | 2.71x | **4.00x** | **+47.6%** |
| **Display Ads** | \$51,626.47 | \$364,869 | \$198,153 | \$259,603 | \$250,867 | \$272,976 | \$256,108 | \$268,434 | 3.84x | 5.29x | +37.8% |
| **Email Marketing** | \$13,700.33 | \$0 | \$333,974 | \$220,760 | \$237,497 | \$191,563 | \$315,430 | \$229,022 | 24.38x | 13.98x | -42.6% |
| **Referral** | \$19,729.96 | \$137,754 | \$100,379 | \$114,991 | \$113,800 | \$117,069 | \$122,710 | \$123,029 | 5.09x | 5.93x | +16.6% |
| **Organic Search** | \$0.00 | \$351,110 | \$302,134 | \$321,479 | \$319,038 | \$324,750 | \$319,226 | \$329,585 | N/A | N/A | +7.5% |
| **Direct** | \$0.00 | \$158,122 | \$554,397 | \$390,621 | \$411,480 | \$368,226 | \$385,570 | \$360,962 | N/A | N/A | -33.6% |
| **TOTAL** | **\$426,418.04** | **\$2,382,515** | **\$2,382,515** | **\$2,382,515** | **\$2,382,515** | **\$2,382,515** | **\$2,382,515** | **\$2,382,515** | **3.96x** | **3.96x** | **Reconciled ($0.00)** |

---

## 5. Strategic Decision Guide: When to Use Which Model

| Model | Primary Business Use Case | Key Advantages | Critical Limitations / Blindspots |
| :--- | :--- | :--- | :--- |
| **Last-Touch** | Immediate conversion tracking; short-cycle transactional products (< 24 hrs). | Simple to calculate; universal across legacy ad platforms. | Zero credit to discovery channels; induces over-bidding on brand keywords. |
| **First-Touch** | Pure brand awareness and top-of-funnel customer origination analysis. | Highlights which channels feed the top of the prospect pipeline. | Ignores nurturing and closing touchpoints entirely. |
| **Linear** | Multi-channel parity sanity check. | Transparent; prevents monopolization by single touchpoints. | Artificially treats an incidental display banner identically to an hour-long webinar. |
| **Time-Decay** | Products with moderate consideration (1-2 weeks) where recent urgency dominates. | Reflects increasing purchase intent as conversion nears. | Penalizes long-gestation brand-building channels that sparked initial interest. |
| **Position-Based (U-Shaped)** | **Recommended Operational Model** for Grito Labs daily/weekly reporting. | Balances originators (40%) and closers (40%) while sustaining assist channels (20%). | Fixed 40-20-40 split is an empirical heuristic, not learned from data. |
| **Markov Chain** | **Recommended Quarterly Planning Model** for capital budgeting and CAC targets. | Fully data-driven; accounts for non-converting visitor drop-offs and channel removals. | Computationally intensive; sensitive to transition graph sparsity. |
| **Shapley Value** | Fair cooperative compensation benchmarking across marketing teams. | Axiomatic fairness (efficiency, symmetry, additivity, null player). | Exponential coalition complexity; order-invariant. |
