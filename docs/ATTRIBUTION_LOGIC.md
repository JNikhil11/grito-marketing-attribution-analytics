# Grito Labs Multi-Touch Attribution Logic & Mathematical Reference

**Document Version:** 1.0  
**Target Audience:** Marketing Analytics Leads, Data Engineers, and Financial Controllers  

---

## 1. Overview of Attribution Paradigms

Marketing attribution is the science of assigning credit for a business conversion to touchpoints encountered along a prospective customer's path to purchase.

Models are classified into two broad families:
1. **Rule-Based (Heuristic) Models:** Pre-determined mathematical rules applied uniformly across all journeys (First-Touch, Last-Touch, Linear, Time-Decay, Position-Based).
2. **Data-Driven (Algorithmic) Models:** Credit derived probabilistically from observed behavioral path sequences and removal effects (Markov Chains, Shapley Values).

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
- **Attributed Revenue:**
  - Paid Social: **$999.00**
  - Display Ads: **$0.00**
  - Email Marketing: **$0.00**
  - Paid Search: **$0.00**

#### 2. Last-Touch Attribution (LTA)
- **Rule:** 100% to touchpoint 4.
- **Weights:** $w_1 = 0.0, \quad w_2 = 0.0, \quad w_3 = 0.0, \quad w_4 = 1.0$
- **Attributed Revenue:**
  - Paid Social: **$0.00**
  - Display Ads: **$0.00**
  - Email Marketing: **$0.00**
  - Paid Search: **$999.00**

#### 3. Linear Attribution
- **Rule:** Equal distribution: $w_i = 1 / N = 1 / 4 = 0.25$.
- **Weights:** $w_1 = 0.25, \quad w_2 = 0.25, \quad w_3 = 0.25, \quad w_4 = 0.25$
- **Attributed Revenue:**
  - Paid Social: **$249.75** (25%)
  - Display Ads: **$249.75** (25%)
  - Email Marketing: **$249.75** (25%)
  - Paid Search: **$249.75** (25%)

#### 4. Time-Decay Attribution (7-Day Half-Life: $\tau = 7.0$)
- **Formula:** $\tilde{w}_i = 2^{-\frac{\Delta t_i}{7.0}}$
  - $\tilde{w}_1 = 2^{-14.0 / 7.0} = 2^{-2} = 0.250$
  - $\tilde{w}_2 = 2^{-8.0 / 7.0} = 2^{-1.143} \approx 0.453$
  - $\tilde{w}_3 = 2^{-3.0 / 7.0} = 2^{-0.429} \approx 0.743$
  - $\tilde{w}_4 = 2^{-0.0 / 7.0} = 2^0 = 1.000$
  - **Sum of Raw Weights:** $\sum \tilde{w}_i = 0.250 + 0.453 + 0.743 + 1.000 = 2.446$
- **Normalized Weights:** $w_i = \tilde{w}_i / 2.446$
  - $w_1 = 0.250 / 2.446 = \mathbf{0.102}$ (10.2%)
  - $w_2 = 0.453 / 2.446 = \mathbf{0.185}$ (18.5%)
  - $w_3 = 0.743 / 2.446 = \mathbf{0.304}$ (30.4%)
  - $w_4 = 1.000 / 2.446 = \mathbf{0.409}$ (40.9%)
- **Attributed Revenue:**
  - Paid Social: **$101.90**
  - Display Ads: **$184.82**
  - Email Marketing: **$303.69**
  - Paid Search: **$408.59**

#### 5. Position-Based (U-Shaped 40-20-40) Attribution
- **Rule:** $N = 4 \implies$ First Touch = 40%, Last Touch = 40%, Remaining 20% divided equally across the 2 middle touches ($20\% / 2 = 10\%$ each).
- **Weights:** $w_1 = 0.40, \quad w_2 = 0.10, \quad w_3 = 0.10, \quad w_4 = 0.40$
- **Attributed Revenue:**
  - Paid Social: **$399.60** (40%)
  - Display Ads: **$99.90** (10%)
  - Email Marketing: **$99.90** (10%)
  - Paid Search: **$399.60** (40%)

#### 6. Data-Driven Markov Chain Attribution (Sample Sub-Graph)
- **Removal Effect Calculation across Portfolio:**
  - Paid Social Removal Effect: $19.3\% \implies \mathbf{31.5\%}$ normalized weight
  - Display Ads Removal Effect: $11.6\% \implies \mathbf{18.9\%}$ normalized weight
  - Email Marketing Removal Effect: $14.6\% \implies \mathbf{23.8\%}$ normalized weight
  - Paid Search Removal Effect: $15.8\% \implies \mathbf{25.8\%}$ normalized weight
- **Attributed Revenue:**
  - Paid Social: **$314.68**
  - Display Ads: **$188.81**
  - Email Marketing: **$237.76**
  - Paid Search: **$257.75**

---

## 3. Side-by-Side Comparison on the Sample Journey

| Marketing Channel | First-Touch | Last-Touch | Linear | Time-Decay (7d) | Position-Based (U-Shaped) | Markov Chain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Paid Social** | **$999.00** | $0.00 | $249.75 | $101.90 | **$399.60** | **$314.68** |
| **Display Ads** | $0.00 | $0.00 | $249.75 | $184.82 | $99.90 | $188.81 |
| **Email Marketing** | $0.00 | $0.00 | $249.75 | $303.69 | $99.90 | $237.76 |
| **Paid Search** | $0.00 | **$999.00** | $249.75 | $408.59 | **$399.60** | $257.75 |
| **Total Attributed** | **$999.00** | **$999.00** | **$999.00** | **$999.00** | **$999.00** | **$999.00** |

---

## 4. Strategic Decision Guide: When to Use Which Model

| Model | Primary Business Use Case | Key Advantages | Critical Limitations / Blindspots |
| :--- | :--- | :--- | :--- |
| **Last-Touch** | Immediate conversion tracking; short-cycle transactional products (< 24 hrs). | Simple to calculate; universal across legacy ad platforms. | Zero credit to discovery channels; induces over-bidding on brand keywords. |
| **First-Touch** | Pure brand awareness and top-of-funnel customer origination analysis. | Highlights which channels feed the top of the prospect pipeline. | Ignores nurturing and closing touchpoints entirely. |
| **Linear** | Multi-channel parity sanity check. | Transparent; prevents monopolization by single touchpoints. | Artificially treats an incidental display banner identically to an hour-long webinar. |
| **Time-Decay** | Products with moderate consideration (1-2 weeks) where recent urgency dominates. | Reflects increasing purchase intent as conversion nears. | Penalizes long-gestation brand-building channels that sparked initial interest. |
| **Position-Based (U-Shaped)** | **Recommended Operational Model** for Grito Labs daily/weekly reporting. | Balances originators (40%) and closers (40%) while sustaining assist channels (20%). | Fixed 40-20-40 split is an empirical heuristic, not learned from data. |
| **Markov Chain** | **Recommended Quarterly Planning Model** for capital budgeting and CAC targets. | Fully data-driven; accounts for non-converting visitor drop-offs and channel removals. | Computationally intensive; sensitive to transition graph sparsity. |
| **Shapley Value** | Fair cooperative compensation benchmarking across marketing teams. | Axiomatic fairness (efficiency, symmetry, additivity, null player). | Exponential coalition complexity; ignores chronological sequence order. |
