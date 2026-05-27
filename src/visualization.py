"""
Visualization Module for A/B Test Analysis
Generate publication-quality charts for experiment results.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('husl')


def plot_conversion_comparison(control_rate: float, treatment_rate: float,
                               control_ci: tuple, treatment_ci: tuple,
                               save_path: str = None):
    """Plot conversion rate comparison with confidence intervals."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    variants = ['Control', 'Treatment']
    rates = [control_rate * 100, treatment_rate * 100]
    errors_lower = [
        (control_rate - control_ci[0]) * 100,
        (treatment_rate - treatment_ci[0]) * 100
    ]
    errors_upper = [
        (control_ci[1] - control_rate) * 100,
        (treatment_ci[1] - treatment_rate) * 100
    ]
    
    colors = ['#3498db', '#2ecc71']
    bars = ax.bar(variants, rates, color=colors, width=0.6, edgecolor='white', linewidth=2)
    
    # Add error bars
    ax.errorbar(variants, rates, yerr=[errors_lower, errors_upper], 
                fmt='none', color='black', capsize=8, capthick=2, linewidth=2)
    
    # Add value labels
    for bar, rate, ci_low, ci_high in zip(bars, rates, 
                                          [control_ci[0]*100, treatment_ci[0]*100],
                                          [control_ci[1]*100, treatment_ci[1]*100]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                f'{rate:.2f}%\n[{ci_low:.2f}%, {ci_high:.2f}%]',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Add lift annotation
    lift = treatment_rate - control_rate
    lift_pct = (treatment_rate - control_rate) / control_rate * 100
    ax.annotate(f'+{lift*100:.2f}pp\n(+{lift_pct:.1f}%)',
                xy=(1, treatment_rate * 100),
                xytext=(1.3, (control_rate + treatment_rate) / 2 * 100),
                fontsize=14, fontweight='bold', color='#27ae60',
                arrowprops=dict(arrowstyle='->', color='#27ae60', lw=2))
    
    ax.set_ylabel('Conversion Rate (%)', fontsize=12)
    ax.set_title('A/B Test Results: Conversion Rate Comparison', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(rates) * 1.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"   Saved: {save_path}")
    
    plt.close()
    return fig


def plot_cumulative_conversions(df: pd.DataFrame, save_path: str = None):
    """Plot cumulative conversions over time for both variants."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    df = df.sort_values('timestamp')
    
    for variant, color in [('control', '#3498db'), ('treatment', '#2ecc71')]:
        variant_data = df[df['variant'] == variant].copy()
        variant_data['cumulative_conversions'] = variant_data['converted'].cumsum()
        variant_data['cumulative_users'] = range(1, len(variant_data) + 1)
        variant_data['cumulative_rate'] = (variant_data['cumulative_conversions'] / 
                                           variant_data['cumulative_users'] * 100)
        
        ax.plot(variant_data['timestamp'], variant_data['cumulative_rate'],
                label=variant.title(), color=color, linewidth=2)
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Cumulative Conversion Rate (%)', fontsize=12)
    ax.set_title('Conversion Rate Over Time', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    
    # Format x-axis
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"   Saved: {save_path}")
    
    plt.close()
    return fig


def plot_segmentation_analysis(df: pd.DataFrame, segment_col: str,
                               save_path: str = None):
    """Plot conversion rates by segment for both variants."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Calculate rates by segment
    segment_stats = df.groupby([segment_col, 'variant']).agg({
        'converted': ['sum', 'count']
    }).reset_index()
    segment_stats.columns = [segment_col, 'variant', 'conversions', 'total']
    segment_stats['rate'] = segment_stats['conversions'] / segment_stats['total'] * 100
    
    # Pivot for plotting
    pivot = segment_stats.pivot(index=segment_col, columns='variant', values='rate')
    
    x = np.arange(len(pivot.index))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, pivot['control'], width, label='Control', color='#3498db')
    bars2 = ax.bar(x + width/2, pivot['treatment'], width, label='Treatment', color='#2ecc71')
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.3,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel(segment_col.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel('Conversion Rate (%)', fontsize=12)
    ax.set_title(f'Conversion Rate by {segment_col.replace("_", " ").title()}', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index)
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"   Saved: {save_path}")
    
    plt.close()
    return fig


def plot_posterior_distributions(control_conversions: int, control_total: int,
                                 treatment_conversions: int, treatment_total: int,
                                 save_path: str = None):
    """Plot Bayesian posterior distributions for both variants."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Posterior parameters
    alpha_c = 1 + control_conversions
    beta_c = 1 + control_total - control_conversions
    alpha_t = 1 + treatment_conversions
    beta_t = 1 + treatment_total - treatment_conversions
    
    # X range
    x = np.linspace(0.08, 0.20, 1000)
    
    # Left plot: Posterior distributions
    ax = axes[0]
    
    y_control = stats.beta.pdf(x, alpha_c, beta_c)
    y_treatment = stats.beta.pdf(x, alpha_t, beta_t)
    
    ax.plot(x * 100, y_control, label='Control', color='#3498db', linewidth=2)
    ax.fill_between(x * 100, y_control, alpha=0.3, color='#3498db')
    
    ax.plot(x * 100, y_treatment, label='Treatment', color='#2ecc71', linewidth=2)
    ax.fill_between(x * 100, y_treatment, alpha=0.3, color='#2ecc71')
    
    ax.set_xlabel('Conversion Rate (%)', fontsize=12)
    ax.set_ylabel('Probability Density', fontsize=12)
    ax.set_title('Posterior Distributions', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    
    # Right plot: Lift distribution
    ax = axes[1]
    
    # Sample from posteriors
    samples_c = np.random.beta(alpha_c, beta_c, 100000)
    samples_t = np.random.beta(alpha_t, beta_t, 100000)
    lift_samples = (samples_t - samples_c) * 100
    
    ax.hist(lift_samples, bins=100, density=True, alpha=0.7, color='#9b59b6')
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='No Effect')
    ax.axvline(x=np.mean(lift_samples), color='#27ae60', linestyle='-', 
               linewidth=2, label=f'Mean: +{np.mean(lift_samples):.2f}pp')
    
    # Shade probability of positive lift
    positive_lift = lift_samples[lift_samples > 0]
    prob_positive = len(positive_lift) / len(lift_samples)
    
    ax.set_xlabel('Lift (percentage points)', fontsize=12)
    ax.set_ylabel('Probability Density', fontsize=12)
    ax.set_title(f'Lift Distribution\nP(Treatment > Control) = {prob_positive*100:.1f}%',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"   Saved: {save_path}")
    
    plt.close()
    return fig


def plot_power_analysis(baseline_rate: float = 0.125, 
                        mde_range: np.ndarray = None,
                        save_path: str = None):
    """Plot sample size requirements for different MDEs."""
    from scipy.stats import norm
    
    if mde_range is None:
        mde_range = np.linspace(0.005, 0.03, 50)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    alpha = 0.05
    power = 0.80
    z_alpha = norm.ppf(1 - alpha/2)
    z_beta = norm.ppf(power)
    
    sample_sizes = []
    for mde in mde_range:
        p1 = baseline_rate
        p2 = baseline_rate + mde
        
        # Sample size formula for two proportions
        p_pooled = (p1 + p2) / 2
        effect = abs(p2 - p1)
        
        n = (2 * p_pooled * (1 - p_pooled) * (z_alpha + z_beta)**2) / (effect**2)
        sample_sizes.append(int(n))
    
    ax.plot(mde_range * 100, sample_sizes, color='#3498db', linewidth=2)
    ax.fill_between(mde_range * 100, sample_sizes, alpha=0.2, color='#3498db')
    
    # Add reference lines
    for mde_ref, label in [(1.0, '1% MDE'), (2.0, '2% MDE')]:
        idx = np.argmin(np.abs(mde_range * 100 - mde_ref))
        n_ref = sample_sizes[idx]
        ax.axhline(y=n_ref, color='gray', linestyle='--', alpha=0.7)
        ax.axvline(x=mde_ref, color='gray', linestyle='--', alpha=0.7)
        ax.annotate(f'{label}: {n_ref:,}/variant',
                    xy=(mde_ref, n_ref),
                    xytext=(mde_ref + 0.3, n_ref * 1.1),
                    fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Minimum Detectable Effect (percentage points)', fontsize=12)
    ax.set_ylabel('Required Sample Size (per variant)', fontsize=12)
    ax.set_title(f'Power Analysis (α=0.05, Power=80%, Baseline={baseline_rate*100}%)',
                 fontsize=14, fontweight='bold')
    
    ax.set_ylim(0, max(sample_sizes) * 1.1)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"   Saved: {save_path}")
    
    plt.close()
    return fig


def plot_all_results(df: pd.DataFrame, results: dict, output_dir: str):
    """Generate all visualization plots."""
    print("\n📊 Generating visualizations...")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    summary = results['summary']
    ci = results['confidence_intervals']
    
    # 1. Main comparison chart
    plot_conversion_comparison(
        summary['control_rate'], summary['treatment_rate'],
        ci['control_95ci'], ci['treatment_95ci'],
        output_path / 'ab_test_results.png'
    )
    
    # 2. Cumulative conversions over time
    plot_cumulative_conversions(df, output_path / 'cumulative_conversions.png')
    
    # 3. Segmentation by device
    plot_segmentation_analysis(df, 'device', output_path / 'by_device.png')
    
    # 4. Segmentation by user type
    df['user_type'] = df['new_user'].map({0: 'Returning', 1: 'New'})
    plot_segmentation_analysis(df, 'user_type', output_path / 'by_user_type.png')
    
    # 5. Bayesian posterior distributions
    plot_posterior_distributions(
        summary['control_conversions'], summary['control_n'],
        summary['treatment_conversions'], summary['treatment_n'],
        output_path / 'bayesian_analysis.png'
    )
    
    # 6. Power analysis
    plot_power_analysis(0.125, save_path=output_path / 'power_analysis.png')
    
    print(f"\n✅ All visualizations saved to {output_path}")
