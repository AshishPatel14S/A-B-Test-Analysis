"""
Statistical Tests for A/B Analysis
Comprehensive statistical testing framework.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency, fisher_exact, norm
from typing import Tuple, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


def chi_squared_test(control_conversions: int, control_total: int,
                     treatment_conversions: int, treatment_total: int) -> Dict:
    """
    Perform chi-squared test for independence.
    
    Returns:
        Dictionary with test results
    """
    # Create contingency table
    contingency_table = np.array([
        [control_conversions, control_total - control_conversions],
        [treatment_conversions, treatment_total - treatment_conversions]
    ])
    
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    
    return {
        'test': 'chi_squared',
        'statistic': chi2,
        'p_value': p_value,
        'degrees_of_freedom': dof,
        'significant_at_05': p_value < 0.05,
        'significant_at_01': p_value < 0.01
    }


def z_test_proportions(p1: float, n1: int, p2: float, n2: int,
                       alternative: str = 'two-sided') -> Dict:
    """
    Perform z-test for difference in proportions.
    
    Args:
        p1: Control conversion rate
        n1: Control sample size
        p2: Treatment conversion rate
        n2: Treatment sample size
        alternative: 'two-sided', 'greater', or 'less'
        
    Returns:
        Dictionary with test results
    """
    # Pooled proportion
    p_pooled = (p1 * n1 + p2 * n2) / (n1 + n2)
    
    # Standard error
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
    
    # Z statistic
    z = (p2 - p1) / se
    
    # P-value
    if alternative == 'two-sided':
        p_value = 2 * (1 - norm.cdf(abs(z)))
    elif alternative == 'greater':
        p_value = 1 - norm.cdf(z)
    else:  # less
        p_value = norm.cdf(z)
    
    return {
        'test': 'z_test_proportions',
        'z_statistic': z,
        'p_value': p_value,
        'pooled_proportion': p_pooled,
        'standard_error': se,
        'significant_at_05': p_value < 0.05,
        'significant_at_01': p_value < 0.01
    }


def fishers_exact_test(control_conversions: int, control_total: int,
                       treatment_conversions: int, treatment_total: int) -> Dict:
    """
    Perform Fisher's exact test.
    Best for small sample sizes.
    
    Returns:
        Dictionary with test results
    """
    contingency_table = [
        [control_conversions, control_total - control_conversions],
        [treatment_conversions, treatment_total - treatment_conversions]
    ]
    
    odds_ratio, p_value = fisher_exact(contingency_table, alternative='two-sided')
    
    return {
        'test': 'fishers_exact',
        'odds_ratio': odds_ratio,
        'p_value': p_value,
        'significant_at_05': p_value < 0.05,
        'significant_at_01': p_value < 0.01
    }


def wilson_confidence_interval(successes: int, total: int, 
                                confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate Wilson score confidence interval for a proportion.
    More accurate than Wald interval, especially for small samples.
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if total == 0:
        return (0.0, 0.0)
    
    p = successes / total
    z = norm.ppf(1 - (1 - confidence) / 2)
    
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denominator
    
    return (max(0, center - margin), min(1, center + margin))


def confidence_interval_difference(p1: float, n1: int, p2: float, n2: int,
                                   confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval for difference in proportions.
    
    Returns:
        Tuple of (lower_bound, upper_bound) for (p2 - p1)
    """
    diff = p2 - p1
    z = norm.ppf(1 - (1 - confidence) / 2)
    
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    
    return (diff - z * se, diff + z * se)


def cohens_h(p1: float, p2: float) -> float:
    """
    Calculate Cohen's h effect size for difference in proportions.
    
    Interpretation:
        0.2 = small
        0.5 = medium
        0.8 = large
    """
    return 2 * (np.arcsin(np.sqrt(p2)) - np.arcsin(np.sqrt(p1)))


def relative_lift(control_rate: float, treatment_rate: float) -> Dict:
    """
    Calculate relative lift metrics.
    
    Returns:
        Dictionary with lift metrics
    """
    absolute_lift = treatment_rate - control_rate
    relative_lift = (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0
    
    return {
        'absolute_lift': absolute_lift,
        'relative_lift': relative_lift,
        'absolute_lift_pct': absolute_lift * 100,
        'relative_lift_pct': relative_lift * 100
    }


def sample_ratio_mismatch_test(n_control: int, n_treatment: int,
                                expected_ratio: float = 0.5) -> Dict:
    """
    Test for sample ratio mismatch (SRM).
    Important validity check for A/B tests.
    
    Returns:
        Dictionary with SRM test results
    """
    total = n_control + n_treatment
    expected_control = total * expected_ratio
    expected_treatment = total * (1 - expected_ratio)
    
    # Chi-squared test
    chi2 = ((n_control - expected_control)**2 / expected_control +
            (n_treatment - expected_treatment)**2 / expected_treatment)
    
    p_value = 1 - stats.chi2.cdf(chi2, df=1)
    
    actual_ratio = n_control / total
    
    return {
        'test': 'sample_ratio_mismatch',
        'expected_ratio': expected_ratio,
        'actual_ratio': actual_ratio,
        'chi2_statistic': chi2,
        'p_value': p_value,
        'srm_detected': p_value < 0.01,  # Very conservative threshold
        'status': 'OK' if p_value >= 0.01 else 'WARNING: SRM Detected'
    }


def bayesian_ab_test(control_conversions: int, control_total: int,
                     treatment_conversions: int, treatment_total: int,
                     prior_alpha: float = 1, prior_beta: float = 1,
                     n_samples: int = 100000) -> Dict:
    """
    Bayesian A/B test using Beta-Binomial model.
    
    Returns:
        Dictionary with Bayesian analysis results
    """
    # Posterior distributions (Beta)
    alpha_control = prior_alpha + control_conversions
    beta_control = prior_beta + control_total - control_conversions
    
    alpha_treatment = prior_alpha + treatment_conversions
    beta_treatment = prior_beta + treatment_total - treatment_conversions
    
    # Sample from posteriors
    samples_control = np.random.beta(alpha_control, beta_control, n_samples)
    samples_treatment = np.random.beta(alpha_treatment, beta_treatment, n_samples)
    
    # Probability that treatment > control
    prob_treatment_better = np.mean(samples_treatment > samples_control)
    
    # Expected lift
    lift_samples = samples_treatment - samples_control
    expected_lift = np.mean(lift_samples)
    lift_ci = np.percentile(lift_samples, [2.5, 97.5])
    
    # Risk (expected loss if we choose treatment but control is better)
    loss_if_treatment = np.maximum(samples_control - samples_treatment, 0)
    expected_loss = np.mean(loss_if_treatment)
    
    return {
        'test': 'bayesian',
        'prob_treatment_better': prob_treatment_better,
        'prob_control_better': 1 - prob_treatment_better,
        'expected_lift': expected_lift,
        'lift_ci_lower': lift_ci[0],
        'lift_ci_upper': lift_ci[1],
        'expected_loss_choosing_treatment': expected_loss,
        'recommendation': 'treatment' if prob_treatment_better > 0.95 else 'need_more_data'
    }


def run_all_tests(control_conversions: int, control_total: int,
                  treatment_conversions: int, treatment_total: int) -> Dict:
    """
    Run all statistical tests and return comprehensive results.
    
    Returns:
        Dictionary with all test results
    """
    p_control = control_conversions / control_total
    p_treatment = treatment_conversions / treatment_total
    
    results = {
        'summary': {
            'control_rate': p_control,
            'treatment_rate': p_treatment,
            'control_n': control_total,
            'treatment_n': treatment_total,
            'control_conversions': control_conversions,
            'treatment_conversions': treatment_conversions,
        },
        'lift': relative_lift(p_control, p_treatment),
        'effect_size': {
            'cohens_h': cohens_h(p_control, p_treatment),
            'interpretation': 'small' if abs(cohens_h(p_control, p_treatment)) < 0.2 
                            else 'medium' if abs(cohens_h(p_control, p_treatment)) < 0.5 
                            else 'large'
        },
        'confidence_intervals': {
            'control_95ci': wilson_confidence_interval(control_conversions, control_total),
            'treatment_95ci': wilson_confidence_interval(treatment_conversions, treatment_total),
            'difference_95ci': confidence_interval_difference(p_control, control_total, 
                                                              p_treatment, treatment_total)
        },
        'tests': {
            'chi_squared': chi_squared_test(control_conversions, control_total,
                                           treatment_conversions, treatment_total),
            'z_test': z_test_proportions(p_control, control_total, 
                                         p_treatment, treatment_total),
            'fishers_exact': fishers_exact_test(control_conversions, control_total,
                                                treatment_conversions, treatment_total),
            'bayesian': bayesian_ab_test(control_conversions, control_total,
                                         treatment_conversions, treatment_total)
        },
        'validity': {
            'srm': sample_ratio_mismatch_test(control_total, treatment_total)
        }
    }
    
    # Overall conclusion
    all_significant = (
        results['tests']['chi_squared']['significant_at_05'] and
        results['tests']['z_test']['significant_at_05'] and
        results['tests']['fishers_exact']['significant_at_05']
    )
    
    bayesian_conclusive = results['tests']['bayesian']['prob_treatment_better'] > 0.95
    
    results['conclusion'] = {
        'statistically_significant': all_significant,
        'bayesian_conclusive': bayesian_conclusive,
        'recommendation': 'ship_treatment' if (all_significant and bayesian_conclusive) 
                         else 'need_more_data',
        'confidence_level': 'high' if all_significant else 'low'
    }
    
    return results


def print_results(results: Dict):
    """Pretty print test results."""
    print("=" * 60)
    print("A/B TEST RESULTS")
    print("=" * 60)
    
    summary = results['summary']
    print(f"\n📊 Summary:")
    print(f"   Control: {summary['control_conversions']:,}/{summary['control_n']:,} "
          f"({summary['control_rate']*100:.2f}%)")
    print(f"   Treatment: {summary['treatment_conversions']:,}/{summary['treatment_n']:,} "
          f"({summary['treatment_rate']*100:.2f}%)")
    
    lift = results['lift']
    print(f"\n📈 Lift:")
    print(f"   Absolute: +{lift['absolute_lift_pct']:.2f} percentage points")
    print(f"   Relative: +{lift['relative_lift_pct']:.1f}%")
    
    effect = results['effect_size']
    print(f"\n📐 Effect Size:")
    print(f"   Cohen's h: {effect['cohens_h']:.3f} ({effect['interpretation']})")
    
    ci = results['confidence_intervals']
    print(f"\n📏 95% Confidence Intervals:")
    print(f"   Control: [{ci['control_95ci'][0]*100:.2f}%, {ci['control_95ci'][1]*100:.2f}%]")
    print(f"   Treatment: [{ci['treatment_95ci'][0]*100:.2f}%, {ci['treatment_95ci'][1]*100:.2f}%]")
    print(f"   Difference: [{ci['difference_95ci'][0]*100:.2f}%, {ci['difference_95ci'][1]*100:.2f}%]")
    
    print(f"\n🧪 Statistical Tests:")
    for name, test in results['tests'].items():
        if name == 'bayesian':
            print(f"   {name}: P(treatment > control) = {test['prob_treatment_better']*100:.1f}%")
        else:
            sig = "✅" if test.get('significant_at_05', False) else "❌"
            print(f"   {name}: p = {test['p_value']:.4f} {sig}")
    
    srm = results['validity']['srm']
    print(f"\n🔍 Validity Check:")
    print(f"   Sample Ratio: {srm['actual_ratio']:.4f} (expected: {srm['expected_ratio']})")
    print(f"   SRM Test: {srm['status']}")
    
    conclusion = results['conclusion']
    print(f"\n{'='*60}")
    print(f"📋 CONCLUSION: {conclusion['recommendation'].upper()}")
    print(f"   Statistical Significance: {'Yes' if conclusion['statistically_significant'] else 'No'}")
    print(f"   Bayesian Confidence: {'High' if conclusion['bayesian_conclusive'] else 'Low'}")
    print("=" * 60)
