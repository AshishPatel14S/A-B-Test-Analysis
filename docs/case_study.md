# A/B Test Analysis Framework

## Case Study

---

### TL;DR

Conducted rigorous statistical analysis of checkout flow A/B test, finding a +1.95pp lift (18% relative improvement) in conversion rate with 99.9% statistical significance, translating to $9.9M annual revenue impact.

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
- Multiple comparison correction (Bonferroni)
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
- Confidence Level: 99.9%
- P(Treatment > Control): 100%

**Business Impact:**
- Monthly Revenue Lift: $828,750
- Annual Revenue Lift: $9.9M

---

### Segment Analysis

| Segment | Control | Treatment | Lift | Significant? |
|---------|---------|-----------|------|--------------|
| Desktop | 12.5% | 14.7% | +2.2pp | ✅ Yes |
| Mobile | 8.9% | 10.8% | +1.9pp | ✅ Yes |
| Tablet | 11.1% | 12.6% | +1.5pp | ✅ Yes |
| New Users | 7.4% | 9.5% | +2.1pp | ✅ Yes |
| Returning | 12.7% | 14.5% | +1.8pp | ✅ Yes |

**Key Insight:** New users showed the largest improvement, suggesting the streamlined flow particularly helps first-time buyers.

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
3. **Consistent across all segments** (desktop, mobile, new/returning)
4. **No negative guardrail impacts**
5. **High confidence** in $9.9M annual impact

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
- **Multiple comparison** corrections
- **Segmentation analysis**
- **Business impact** quantification
- **Stakeholder communication**

---

**Code:** [GitHub Repository Link](#)  
**Full Report:** [ab_test_report.md](../reports/ab_test_report.md)  
**Contact:** ashishpatelap1403@gmail.com
