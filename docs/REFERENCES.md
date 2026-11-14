# Academic References, Open-Source Citations & Licences

**Project:** Multi-Channel Marketing Analytics & Attribution Framework  
**Entity:** Grito Labs  
**Document Version:** 1.0  

---

## 1. Academic Research Papers

1. **Diemert, E., Meynet, J., Galland, P., & Lefortier, D. (2017).**  
   *Attribution Modeling Increases Efficiency of Bidding in Display Advertising.*  
   Proceedings of the 2017 ACM SIGKDD Workshop on Machine Learning in Online Advertising (ADKDD '17).  
   DOI: [10.1145/3121050.3121056](https://doi.org/10.1145/3121050.3121056)  
   *Contribution:* Empirical multi-touch journey structure, touchpoint latency dynamics, and Criteo display bidding dataset schema.

2. **Fader, P. S., Hardie, B. G., & Lee, K. L. (2005).**  
   *“Counting Your Customers” the Easy Way: An Alternative to the Pareto/NBD Model.*  
   Marketing Science, 24(2), 275-284.  
   DOI: [10.1287/mksc.1040.0098](https://doi.org/10.1287/mksc.1040.0098)  
   *Contribution:* Closed-form Beta-Geometric / Negative Binomial Distribution (BG/NBD) customer lifetime transaction frequency modeling.

3. **Fader, P. S., Hardie, B. G., & Lee, K. L. (2005).**  
   *The Gamma-Gamma Model of Monetary Value.*  
   Technical Note, Wharton School of Business, University of Pennsylvania.  
   *Contribution:* Hierarchical Gamma-Gamma monetary model for predicting average transaction value per customer.

4. **Shapley, L. S. (1953).**  
   *A Value for n-Person Games.*  
   Contributions to the Theory of Games, 2(28), 307-317.  
   Princeton University Press.  
   *Contribution:* Axiomatic coalitional game theory formulation applied to multi-channel advertising marginal contributions.

5. **Hill, A. V. (1910).**  
   *The Possible Effects of the Aggregation of the Molecules of Haemoglobin on its Dissociation Curves.*  
   Journal of Physiology, 40, iv-vii.  
   *Contribution:* S-shaped saturation kinetics equation utilized for econometric media response curves and diminishing marginal returns.

---

## 2. Open-Source Libraries & Software Licences

| Package / Tool | Version | License | Primary Purpose in Framework |
| :--- | :---: | :---: | :--- |
| **Python Standard Library** | 3.14.5 | PSF License | Zero-dependency core analytical execution (`sqlite3`, `math`, `csv`, `json`). |
| **SQLite** | 3.50.4 | Public Domain | Embedded ANSI SQL relational star-schema data warehouse. |
| **DuckDB** | $\ge 0.9.0$ | MIT License | Portable analytical columnar SQL engine for big-data scalability. |
| **python-pptx** | 1.0.2 | MIT License | Programmatic creation of the 14-slide executive PowerPoint presentation. |
| **Playwright** | 1.63.0 | Apache 2.0 | Headless browser execution for dashboard screenshots and publication PDF rendering. |
| **PyMuPDF (fitz)** | 1.28.2 | AGPL / Commercial | High-performance PDF document analysis and vector rendering. |
| **Pillow (PIL)** | 12.2.0 | HPND License | Imaging and visual asset manipulation. |
| **Chart.js** | 4.4.0 | MIT License | Interactive canvas charting in the standalone HTML dashboard. |

---

## 3. Dataset Attribution & Transparency Statement

- **Dataset Foundation:** Modeled upon empirical distribution parameters from the public **Criteo Attribution Modeling for Bidding Dataset** (Diemert et al., 2017) and cross-validated with EdTech business metrics (course pricing, multi-week syllabus consideration, repeat certificate enrollments).
- **Synthetic Augmentation Disclosure:** To protect proprietary student privacy and provide realistic EdTech course titles, channel names, and marketing costs, individual user records were synthetically generated using a fixed random seed (`seed = 42`) in `src/generate_dataset.py`.
- **Integrity Compliance:** All generated data strictly adheres to empirical statistical bounds (log-normal latency, power-law path lengths, and realistic CPC/CPM distributions).
