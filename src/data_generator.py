"""
A/B Test Data Generator
Creates realistic e-commerce experiment data for analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

np.random.seed(42)

# Configuration
N_USERS_PER_VARIANT = 50000
CONTROL_CONVERSION_RATE = 0.125  # 12.5%
TREATMENT_LIFT = 0.021  # +2.1 percentage points
TREATMENT_CONVERSION_RATE = CONTROL_CONVERSION_RATE + TREATMENT_LIFT

# Revenue parameters
AVG_ORDER_VALUE = 85
ORDER_VALUE_STD = 35

# Device distribution
DEVICE_DIST = {'desktop': 0.45, 'mobile': 0.45, 'tablet': 0.10}

# Device-specific conversion multipliers
DEVICE_CONVERSION_MULT = {'desktop': 1.15, 'mobile': 0.82, 'tablet': 1.02}

# New user rate and conversion multiplier
NEW_USER_RATE = 0.35
NEW_USER_CONVERSION_MULT = 0.68


def generate_ab_test_data():
    """Generate realistic A/B test data."""
    print("🔄 Generating A/B test data...")
    
    data = []
    start_date = datetime(2024, 1, 15)
    test_duration_days = 14
    
    for variant in ['control', 'treatment']:
        base_rate = CONTROL_CONVERSION_RATE if variant == 'control' else TREATMENT_CONVERSION_RATE
        n_users = N_USERS_PER_VARIANT
        
        print(f"   Generating {variant}: {n_users:,} users")
        
        for i in range(n_users):
            # Random timestamp within test period
            days_offset = np.random.uniform(0, test_duration_days)
            hours_offset = np.random.uniform(0, 24)
            timestamp = start_date + timedelta(days=days_offset, hours=hours_offset)
            
            # Device assignment
            device = np.random.choice(
                list(DEVICE_DIST.keys()),
                p=list(DEVICE_DIST.values())
            )
            
            # New user flag
            is_new_user = np.random.random() < NEW_USER_RATE
            
            # Calculate conversion probability with modifiers
            conversion_prob = base_rate
            conversion_prob *= DEVICE_CONVERSION_MULT[device]
            if is_new_user:
                conversion_prob *= NEW_USER_CONVERSION_MULT
            
            # Clip to valid probability range
            conversion_prob = np.clip(conversion_prob, 0.01, 0.5)
            
            # Determine conversion
            converted = np.random.random() < conversion_prob
            
            # Calculate revenue
            if converted:
                # Log-normal distribution for realistic order values
                revenue = np.random.lognormal(
                    mean=np.log(AVG_ORDER_VALUE) - 0.5 * (ORDER_VALUE_STD/AVG_ORDER_VALUE)**2,
                    sigma=ORDER_VALUE_STD/AVG_ORDER_VALUE
                )
                revenue = round(max(10, min(500, revenue)), 2)  # Clip to reasonable range
            else:
                revenue = 0.0
            
            data.append({
                'user_id': f'{variant[0]}{i+1:06d}',
                'timestamp': timestamp,
                'variant': variant,
                'converted': int(converted),
                'revenue': revenue,
                'device': device,
                'new_user': int(is_new_user)
            })
    
    df = pd.DataFrame(data)
    
    # Shuffle the data
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Print summary statistics
    print("\n📊 Summary Statistics:")
    for variant in ['control', 'treatment']:
        variant_data = df[df['variant'] == variant]
        conv_rate = variant_data['converted'].mean() * 100
        revenue = variant_data[variant_data['converted'] == 1]['revenue'].mean()
        print(f"   {variant.title()}:")
        print(f"      Conversion Rate: {conv_rate:.2f}%")
        print(f"      Avg Order Value: ${revenue:.2f}")
    
    return df


def add_novelty_effect(df):
    """Add novelty effect to first few days (optional realism)."""
    df = df.copy()
    
    # First 3 days have slightly higher treatment effect (novelty)
    first_days = df['timestamp'] < df['timestamp'].min() + timedelta(days=3)
    treatment_first_days = first_days & (df['variant'] == 'treatment')
    
    # 10% of treatment users in first 3 days get artificial boost
    boost_mask = treatment_first_days & (np.random.random(len(df)) < 0.1)
    
    # This is just for demonstration - in real analysis we'd exclude these
    df.loc[boost_mask & (df['converted'] == 0), 'novelty_flag'] = 1
    df['novelty_flag'] = df.get('novelty_flag', 0).fillna(0).astype(int)
    
    return df


def generate_guardrail_metrics(df):
    """Generate guardrail metric data."""
    print("\n🛡️ Generating guardrail metrics...")
    
    guardrails = []
    
    for variant in ['control', 'treatment']:
        variant_data = df[df['variant'] == variant]
        n_users = len(variant_data)
        
        # Cart abandonment (inverse of conversion, with noise)
        abandonment_rate = 0.682 if variant == 'control' else 0.651
        
        # Page load time
        load_time = 2.1 if variant == 'control' else 2.0
        
        # Error rate
        error_rate = 0.003 if variant == 'control' else 0.002
        
        # Bounce rate
        bounce_rate = 0.42 if variant == 'control' else 0.40
        
        guardrails.append({
            'variant': variant,
            'cart_abandonment_rate': abandonment_rate,
            'avg_page_load_time': load_time,
            'error_rate': error_rate,
            'bounce_rate': bounce_rate,
            'n_users': n_users
        })
    
    return pd.DataFrame(guardrails)


def main():
    """Generate and save all data files."""
    # Generate main A/B test data
    df = generate_ab_test_data()
    
    # Generate guardrail metrics
    guardrails_df = generate_guardrail_metrics(df)
    
    # Save files
    project_root = Path(__file__).parent.parent
    
    # Save to raw
    raw_dir = project_root / 'data' / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(raw_dir / 'ab_test_data.csv', index=False)
    guardrails_df.to_csv(raw_dir / 'guardrail_metrics.csv', index=False)
    
    # Save to sample
    sample_dir = project_root / 'data' / 'sample'
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(sample_dir / 'ab_test_data.csv', index=False)
    guardrails_df.to_csv(sample_dir / 'guardrail_metrics.csv', index=False)
    
    print(f"\n💾 Saved data to:")
    print(f"   {raw_dir}")
    print(f"   {sample_dir}")
    
    print(f"\n📊 Dataset Summary:")
    print(f"   Total users: {len(df):,}")
    print(f"   Control: {len(df[df['variant']=='control']):,}")
    print(f"   Treatment: {len(df[df['variant']=='treatment']):,}")
    print(f"   Test duration: 14 days")
    
    print("\n✅ Data generation complete!")
    
    return df, guardrails_df


if __name__ == '__main__':
    main()
