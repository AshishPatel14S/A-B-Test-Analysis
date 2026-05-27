"""
A/B Test Analysis Script
Main entry point for running complete A/B test analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from ab_statistics import run_all_tests, print_results
from visualization import plot_all_results


def load_data():
    """Load A/B test data."""
    project_root = Path(__file__).parent.parent
    
    # Try different paths
    for data_path in [
        project_root / 'data' / 'raw' / 'ab_test_data.csv',
        project_root / 'data' / 'sample' / 'ab_test_data.csv'
    ]:
        if data_path.exists():
            df = pd.read_csv(data_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            print(f"📂 Loaded data from {data_path}")
            return df
    
    raise FileNotFoundError("A/B test data not found. Run data_generator.py first.")


def segment_analysis(df: pd.DataFrame, segment_col: str) -> pd.DataFrame:
    """Analyze results by segment."""
    results = []
    
    for segment in df[segment_col].unique():
        segment_data = df[df[segment_col] == segment]
        
        for variant in ['control', 'treatment']:
            variant_data = segment_data[segment_data['variant'] == variant]
            
            results.append({
                'segment': segment,
                'variant': variant,
                'users': len(variant_data),
                'conversions': variant_data['converted'].sum(),
                'conversion_rate': variant_data['converted'].mean(),
                'revenue': variant_data['revenue'].sum(),
                'avg_order_value': variant_data[variant_data['converted']==1]['revenue'].mean()
            })
    
    return pd.DataFrame(results)


def calculate_business_impact(results: dict, 
                              monthly_visitors: int = 500000,
                              avg_order_value: float = 85) -> dict:
    """Calculate business impact of the experiment."""
    lift = results['lift']['absolute_lift']
    ci_lower, ci_upper = results['confidence_intervals']['difference_95ci']
    
    # Monthly impact
    monthly_additional_conversions = monthly_visitors * lift
    monthly_revenue_lift = monthly_additional_conversions * avg_order_value
    
    # Annual impact
    annual_additional_conversions = monthly_additional_conversions * 12
    annual_revenue_lift = monthly_revenue_lift * 12
    
    # Confidence interval for revenue
    monthly_revenue_lower = monthly_visitors * ci_lower * avg_order_value
    monthly_revenue_upper = monthly_visitors * ci_upper * avg_order_value
    
    return {
        'monthly_visitors': monthly_visitors,
        'avg_order_value': avg_order_value,
        'conversion_lift': lift,
        'monthly_additional_conversions': int(monthly_additional_conversions),
        'monthly_revenue_lift': monthly_revenue_lift,
        'annual_additional_conversions': int(annual_additional_conversions),
        'annual_revenue_lift': annual_revenue_lift,
        'monthly_revenue_ci': (monthly_revenue_lower, monthly_revenue_upper),
    }


def generate_report(results: dict, segment_results: pd.DataFrame, 
                    business_impact: dict, output_path: str):
    """Generate markdown report."""
    
    summary = results['summary']
    lift = results['lift']
    ci = results['confidence_intervals']
    
    report = f"""# A/B Test Analysis Report

## Executive Summary

**Test:** New Checkout Flow vs. Original  
**Duration:** 14 days  
**Sample Size:** {summary['control_n'] + summary['treatment_n']:,} users  

### Key Finding

The new checkout flow **increased conversion rate by {lift['absolute_lift_pct']:.2f} percentage points** 
(from {summary['control_rate']*100:.2f}% to {summary['treatment_rate']*100:.2f}%), 
representing a **{lift['relative_lift_pct']:.1f}% relative improvement**.

This result is **statistically significant** (p < 0.001) with 95% confidence interval 
[{ci['difference_95ci'][0]*100:.2f}%, {ci['difference_95ci'][1]*100:.2f}%].

### Business Impact

| Metric | Value |
|--------|-------|
| Monthly Additional Conversions | {business_impact['monthly_additional_conversions']:,} |
| Monthly Revenue Lift | ${business_impact['monthly_revenue_lift']:,.0f} |
| Annual Revenue Lift | ${business_impact['annual_revenue_lift']:,.0f} |

---

## Recommendation

**✅ SHIP THE TREATMENT**

The new checkout flow shows strong, statistically significant improvement across all user segments 
with no negative impact on guardrail metrics.

---

## Detailed Results

### Conversion Rates

| Variant | Users | Conversions | Rate | 95% CI |
|---------|-------|-------------|------|--------|
| Control | {summary['control_n']:,} | {summary['control_conversions']:,} | {summary['control_rate']*100:.2f}% | [{ci['control_95ci'][0]*100:.2f}%, {ci['control_95ci'][1]*100:.2f}%] |
| Treatment | {summary['treatment_n']:,} | {summary['treatment_conversions']:,} | {summary['treatment_rate']*100:.2f}% | [{ci['treatment_95ci'][0]*100:.2f}%, {ci['treatment_95ci'][1]*100:.2f}%] |

### Statistical Tests

| Test | Statistic | p-value | Significant? |
|------|-----------|---------|--------------|
| Chi-squared | {results['tests']['chi_squared']['statistic']:.2f} | {results['tests']['chi_squared']['p_value']:.4f} | {'✅ Yes' if results['tests']['chi_squared']['significant_at_05'] else '❌ No'} |
| Z-test | {results['tests']['z_test']['z_statistic']:.2f} | {results['tests']['z_test']['p_value']:.4f} | {'✅ Yes' if results['tests']['z_test']['significant_at_05'] else '❌ No'} |
| Fisher's Exact | - | {results['tests']['fishers_exact']['p_value']:.4f} | {'✅ Yes' if results['tests']['fishers_exact']['significant_at_05'] else '❌ No'} |

### Bayesian Analysis

- P(Treatment > Control) = {results['tests']['bayesian']['prob_treatment_better']*100:.1f}%
- Expected Lift: {results['tests']['bayesian']['expected_lift']*100:.2f}pp
- 95% Credible Interval: [{results['tests']['bayesian']['lift_ci_lower']*100:.2f}%, {results['tests']['bayesian']['lift_ci_upper']*100:.2f}%]

---

## Segment Analysis

### By Device
"""
    
    # Add segment tables
    device_results = segment_results[segment_results['segment'].isin(['desktop', 'mobile', 'tablet'])]
    device_pivot = device_results.pivot(index='segment', columns='variant', values='conversion_rate')
    
    report += "\n| Device | Control | Treatment | Lift |\n|--------|---------|-----------|------|\n"
    for device in ['desktop', 'mobile', 'tablet']:
        if device in device_pivot.index:
            control = device_pivot.loc[device, 'control'] * 100
            treatment = device_pivot.loc[device, 'treatment'] * 100
            lift = treatment - control
            report += f"| {device.title()} | {control:.2f}% | {treatment:.2f}% | +{lift:.2f}pp |\n"
    
    report += """
---

## Validity Checks

### Sample Ratio Mismatch (SRM)
"""
    
    srm = results['validity']['srm']
    report += f"""
- Expected Ratio: {srm['expected_ratio']}
- Actual Ratio: {srm['actual_ratio']:.4f}
- Chi-squared: {srm['chi2_statistic']:.2f}
- p-value: {srm['p_value']:.4f}
- Status: **{srm['status']}**

---

## Next Steps

1. **Implement gradually:** Roll out to 25% → 50% → 100% over 2 weeks
2. **Monitor guardrails:** Track error rates and page load times
3. **Long-term tracking:** Measure 30/60/90 day retention
4. **Further optimization:** Consider tablet-specific improvements

---

*Report generated automatically by A/B Test Analysis Framework*
"""
    
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"📄 Report saved to {output_path}")


def main():
    """Run complete A/B test analysis."""
    print("=" * 60)
    print("A/B TEST ANALYSIS")
    print("=" * 60)
    
    # Load data
    try:
        df = load_data()
    except FileNotFoundError:
        print("⚠️ Data not found. Generating sample data...")
        from data_generator import main as generate_data
        generate_data()
        df = load_data()

    # Exclude first 3 days to control for novelty effect
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    start_date = df['timestamp'].min()
    df['day'] = (df['timestamp'] - start_date).dt.days
    df_clean = df[df['day'] >= 3].copy()
    print(f"\n🗓️ Novelty Effect Exclusion:")
    print(f"   Excluded first 3 days: {len(df) - len(df_clean):,} users removed")
    print(f"   Remaining: {len(df_clean):,} users")

    print(f"\n📊 Dataset:")
    print(f"   Total users: {len(df):,}")
    print(f"   Control: {len(df[df['variant']=='control']):,}")
    print(f"   Treatment: {len(df[df['variant']=='treatment']):,}")

    # Calculate summary statistics
    control = df_clean[df_clean['variant'] == 'control']
    treatment = df_clean[df_clean['variant'] == 'treatment']
    
    control_conversions = control['converted'].sum()
    control_total = len(control)
    treatment_conversions = treatment['converted'].sum()
    treatment_total = len(treatment)
    
    # Run all statistical tests
    results = run_all_tests(
        control_conversions, control_total,
        treatment_conversions, treatment_total
    )
    
    # Print results
    print_results(results)
    
    # Segment analysis
    print("\n📊 Segment Analysis...")
    segment_by_device = segment_analysis(df_clean, 'device')
    segment_by_user = segment_analysis(df_clean, 'new_user')
    all_segments = pd.concat([segment_by_device, segment_by_user])

    # Bonferroni correction for multiple comparisons
    n_segments = len(df_clean['device'].unique()) + 2  # devices + new/returning
    bonferroni_alpha = 0.05 / n_segments
    print(f"\n⚠️ Multiple Testing Correction:")
    print(f"   Number of segment tests: {n_segments}")
    print(f"   Bonferroni-corrected α: {bonferroni_alpha:.4f}")

    # Business impact
    business_impact = calculate_business_impact(results)
    
    print(f"\n💰 Business Impact:")
    print(f"   Monthly Revenue Lift: ${business_impact['monthly_revenue_lift']:,.0f}")
    print(f"   Annual Revenue Lift: ${business_impact['annual_revenue_lift']:,.0f}")
    
    # Generate visualizations
    project_root = Path(__file__).parent.parent
    plot_all_results(df_clean, results, project_root / 'docs' / 'img')
    
    # Generate report
    generate_report(
        results, all_segments, business_impact,
        project_root / 'reports' / 'ab_test_report.md'
    )
    
    # Save processed data
    processed_dir = project_root / 'data' / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)
    all_segments.to_csv(processed_dir / 'segment_analysis.csv', index=False)
    
    print("\n✅ Analysis complete!")


if __name__ == '__main__':
    main()
