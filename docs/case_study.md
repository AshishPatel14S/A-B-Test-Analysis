# A/B Test Analysis Framework

## Case Study

---

### TL;DR

Conducted rigorous statistical analysis of checkout flow A/B test, finding a +1.95pp lift (18% relative improvement) in conversion rate, statistically significant at p < 0.001, translating to $9.9M in annualized revenue lift.

---

### Role & Timeline

**Role:** Data Analyst (Solo Project)  
**Timeline:** 2 weeks  
**Responsibilities:** Experiment design, statistical analysis, visualization, stakeholder communication

---

### Business Context

An e-commerce company redesigned their checkout flow to reduce friction. Before rolling out to all users, they ran a 14-day A/B test:

- **Control:** Original 4-step checkout
- **Treatment:** New streamlined 2-step checkout
- **Traffic Split:** 50/50 random assignment
- **Sample Size:** 100,000 users total

**Key Questions:**
1. Does the new checkout increase conversion?
2. Is the lift statistically significant?
3. What's the business impact?
4. Any segment-specific effects?

---

### Methodology

**Statistical Tests:**
- Chi-squared test for independence
- Z-test for proportions
- Fisher's exact test (robustness)
- Bayesian A/B test (probability of winning)

**Key Checks:**
- Sample Ratio Mismatch (SRM) test
- Segment-level consistency check across device and user type
- Confidence intervals (Wilson score)
- Effect size (Cohen's h)

---

### Results

| Metric | Control | Treatment | Difference |
|--------|---------|-----------|------------|
| Users | 50,000 | 50,000 | - |
| Conversions | 5,421 | 6,396 | +975 |
| Rate | 10.84% | 12.79% | +1.95pp |
| 95% CI | [10.57%, 11.12%] | [12.50%, 13.09%] | [1.55%, 2.35%] |

**Statistical Significance:**
- p-value: < 0.001
- Statistical significance: p < 0.001
- 95% CI for lift: [1.55pp, 2.35pp]
- P(Treatment > Control): >99.9% (Bayesian estimate)

**Business Impact** (assuming 500,000 monthly visitors, $85 AOV)**
- Additional monthly conversions: ~9,750
- Monthly revenue lift: $828,750
- Annualized revenue lift: ~$9.9M

---

### Segment Analysis

| Segment | Control | Treatment | Lift | Significant? |
|---------|---------|-----------|------|--------------|
| Desktop | 12.51% | 14.81% | +2.30pp | ✅ Yes |
| Mobile | 9.16% | 10.58% | +1.42pp | ✅ Yes |
| Tablet | 10.88% | 13.85% | +2.97pp | ✅ Yes |
| New Users | 8.14% | 9.77% | +1.63pp | ✅ Yes |
| Returning | 12.30% | 14.41% | +2.11pp | ✅ Yes |

> *Segment results are exploratory and should be used for monitoring, not as separate rollout decisions.*

**Key Insight:** Returning users showed the larger absolute lift (+2.11pp); new users showed a stronger relative improvement (+20.1%) — both segments benefited significantly from the streamlined checkout.

---

### Guardrail Metrics

All guardrails passed:

| Metric | Control | Treatment | Change |
|--------|---------|-----------|--------|
| Avg Order Value | $84.71 | $85.10 | +0.5% ✅ |
| Cart Abandonment | 68.2% | 65.1% | -3.1pp ✅ |
| Error Rate | 0.3% | 0.2% | -33% ✅ |

---

### Recommendation

**✅ Ship the Treatment**

The new checkout flow should be rolled out to 100% of users because:

1. **Statistically significant** improvement (p < 0.001)
2. **Practically significant** lift (+18% relative)
3. **Positive lift across major device and user-type segments** (desktop, mobile, tablet, new/returning users)
4. **No negative guardrail impacts**
5. **Estimated** $9.9M annualized revenue lift under stated traffic and AOV assumptions

---

### Visualization Highlights

![A/B Test Results](img/ab_test_results.png)

The analysis includes:
- Conversion comparison charts
- Time series of cumulative rates
- Segment breakdown analysis
- Bayesian posterior distributions
- Power analysis curves

---

### Skills Demonstrated

- **Hypothesis testing** (frequentist and Bayesian)
- **Power analysis** and sample size calculation
- **Confidence interval** construction
- **Exploratory segmentation** across device and user-type groups
- **Segmentation analysis**
- **Business impact** quantification
- **Stakeholder communication**

---

**Code:** [GitHub Repository](https://github.com/AshishPatel14S/A-B-Test-Analysis)  
**Full Report:** [ab_test_report.md](../reports/ab_test_report.md)  
**Contact:** ashishpatelap1403@gmail.com
