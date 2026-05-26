"""
Power Analysis Module
Sample size calculations and power analysis for A/B tests.
"""

import numpy as np
from scipy import stats
from scipy.stats import norm
from typing import Tuple, Dict, Optional


def calculate_sample_size(baseline_rate: float, 
                          mde: float,
                          alpha: float = 0.05,
                          power: float = 0.80,
                          two_sided: bool = True) -> int:
    """
    Calculate required sample size per variant.
    
    Args:
        baseline_rate: Control group conversion rate
        mde: Minimum detectable effect (absolute, e.g., 0.02 for 2%)
        alpha: Significance level (default 0.05)
        power: Statistical power (default 0.80)
        two_sided: Whether to use two-sided test
        
    Returns:
        Required sample size per variant
    """
    p1 = baseline_rate
    p2 = baseline_rate + mde
    
    # Z-scores
    if two_sided:
        z_alpha = norm.ppf(1 - alpha/2)
    else:
        z_alpha = norm.ppf(1 - alpha)
    z_beta = norm.ppf(power)
    
    # Pooled standard deviation
    p_pooled = (p1 + p2) / 2
    
    # Sample size formula
    n = (2 * p_pooled * (1 - p_pooled) * (z_alpha + z_beta)**2) / (mde**2)
    
    return int(np.ceil(n))


def calculate_power(baseline_rate: float,
                    mde: float,
                    sample_size: int,
                    alpha: float = 0.05,
                    two_sided: bool = True) -> float:
    """
    Calculate statistical power for given sample size.
    
    Args:
        baseline_rate: Control group conversion rate
        mde: Minimum detectable effect
        sample_size: Sample size per variant
        alpha: Significance level
        two_sided: Whether to use two-sided test
        
    Returns:
        Statistical power (0-1)
    """
    p1 = baseline_rate
    p2 = baseline_rate + mde
    
    # Z-score for alpha
    if two_sided:
        z_alpha = norm.ppf(1 - alpha/2)
    else:
        z_alpha = norm.ppf(1 - alpha)
    
    # Pooled standard error
    p_pooled = (p1 + p2) / 2
    se = np.sqrt(2 * p_pooled * (1 - p_pooled) / sample_size)
    
    # Critical value
    critical_value = z_alpha * se
    
    # Effect under alternative hypothesis
    effect = mde
    se_effect = np.sqrt(p1*(1-p1)/sample_size + p2*(1-p2)/sample_size)
    
    # Power = P(reject H0 | H1 is true)
    z_power = (effect - critical_value) / se_effect
    power = norm.cdf(z_power)
    
    return power


def calculate_mde(baseline_rate: float,
                  sample_size: int,
                  alpha: float = 0.05,
                  power: float = 0.80,
                  two_sided: bool = True) -> float:
    """
    Calculate minimum detectable effect for given sample size.
    
    Args:
        baseline_rate: Control group conversion rate
        sample_size: Sample size per variant
        alpha: Significance level
        power: Statistical power
        two_sided: Whether to use two-sided test
        
    Returns:
        Minimum detectable effect (absolute)
    """
    p = baseline_rate
    
    # Z-scores
    if two_sided:
        z_alpha = norm.ppf(1 - alpha/2)
    else:
        z_alpha = norm.ppf(1 - alpha)
    z_beta = norm.ppf(power)
    
    # MDE formula (approximation)
    mde = (z_alpha + z_beta) * np.sqrt(2 * p * (1 - p) / sample_size)
    
    return mde


def calculate_test_duration(daily_visitors: int,
                           required_sample_size: int,
                           traffic_split: float = 0.5) -> int:
    """
    Calculate required test duration in days.
    
    Args:
        daily_visitors: Average daily visitors
        required_sample_size: Required sample per variant
        traffic_split: Fraction of traffic in each variant
        
    Returns:
        Required test duration in days
    """
    daily_per_variant = daily_visitors * traffic_split
    days = required_sample_size / daily_per_variant
    
    return int(np.ceil(days))


def power_analysis_report(baseline_rate: float,
                          mde: float,
                          alpha: float = 0.05,
                          power: float = 0.80,
                          daily_visitors: int = 10000) -> Dict:
    """
    Generate comprehensive power analysis report.
    
    Returns:
        Dictionary with power analysis results
    """
    sample_size = calculate_sample_size(baseline_rate, mde, alpha, power)
    actual_power = calculate_power(baseline_rate, mde, sample_size, alpha)
    duration = calculate_test_duration(daily_visitors, sample_size)
    
    # What if scenarios
    sample_sizes_by_power = {}
    for pwr in [0.70, 0.80, 0.90, 0.95]:
        sample_sizes_by_power[f'power_{int(pwr*100)}'] = calculate_sample_size(
            baseline_rate, mde, alpha, pwr
        )
    
    mdes_by_sample = {}
    for n_mult in [0.5, 1.0, 2.0, 5.0]:
        n = int(sample_size * n_mult)
        mdes_by_sample[f'n_{n}'] = calculate_mde(baseline_rate, n, alpha, power)
    
    return {
        'inputs': {
            'baseline_rate': baseline_rate,
            'mde': mde,
            'alpha': alpha,
            'power': power,
            'daily_visitors': daily_visitors
        },
        'results': {
            'required_sample_size_per_variant': sample_size,
            'total_sample_size': sample_size * 2,
            'actual_power': actual_power,
            'test_duration_days': duration
        },
        'sensitivity': {
            'sample_by_power': sample_sizes_by_power,
            'mde_by_sample': mdes_by_sample
        }
    }


def print_power_analysis(report: Dict):
    """Pretty print power analysis results."""
    inputs = report['inputs']
    results = report['results']
    
    print("=" * 60)
    print("POWER ANALYSIS")
    print("=" * 60)
    
    print(f"\n📋 Inputs:")
    print(f"   Baseline Conversion Rate: {inputs['baseline_rate']*100:.1f}%")
    print(f"   Minimum Detectable Effect: {inputs['mde']*100:.1f}pp")
    print(f"   Significance Level (α): {inputs['alpha']}")
    print(f"   Statistical Power: {inputs['power']}")
    print(f"   Daily Visitors: {inputs['daily_visitors']:,}")
    
    print(f"\n📊 Results:")
    print(f"   Required Sample per Variant: {results['required_sample_size_per_variant']:,}")
    print(f"   Total Sample Size: {results['total_sample_size']:,}")
    print(f"   Actual Power: {results['actual_power']*100:.1f}%")
    print(f"   Estimated Duration: {results['test_duration_days']} days")
    
    print(f"\n📈 Sensitivity Analysis:")
    print(f"   Sample size by desired power:")
    for name, n in report['sensitivity']['sample_by_power'].items():
        power_pct = name.replace('power_', '')
        print(f"      {power_pct}% power: {n:,} per variant")
    
    print(f"\n   MDE by sample size:")
    for name, mde in report['sensitivity']['mde_by_sample'].items():
        n = name.replace('n_', '')
        print(f"      n={n}: {mde*100:.2f}pp detectable")


def main():
    """Run example power analysis."""
    print("Running power analysis...")
    
    # Example parameters
    baseline_rate = 0.125  # 12.5% conversion
    mde = 0.01  # 1 percentage point lift
    daily_visitors = 35000
    
    report = power_analysis_report(baseline_rate, mde, daily_visitors=daily_visitors)
    print_power_analysis(report)
    
    print("\n✅ Power analysis complete!")


if __name__ == '__main__':
    main()
