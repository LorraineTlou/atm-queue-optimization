import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

base_time = datetime(2025, 1, 1, 8, 0, 0)
end_time = datetime(2025, 1, 1, 17, 0, 0)
total_seconds = (end_time - base_time).total_seconds()

def generate_stream(day_type, rate_per_minute, service_mean, service_std,
                    withdrawal_mean, withdrawal_std):
    """Generate one clean Poisson arrival stream."""
    records = []
    current = 0  # seconds from start

    while current < total_seconds:
        # Gap between arrivals in seconds
        gap = np.random.exponential(scale=60 / rate_per_minute)
        current += gap

        if current >= total_seconds:
            break

        arrival = base_time + timedelta(seconds=current)
        service = max(10, np.random.normal(loc=service_mean, scale=service_std))
        withdrawal = round(float(np.clip(
            np.random.normal(loc=withdrawal_mean, scale=withdrawal_std), 10, 500
        )), 2)

        records.append({
            'arrival_time': arrival,
            'day_type': day_type,
            'service_time_seconds': round(service, 2),
            'withdrawal_amount_usd': withdrawal
        })

    return records

# Generate two clean separate streams
normal_records = generate_stream(
    day_type='Normal',
    rate_per_minute=2,        # 2 customers per minute
    service_mean=60,
    service_std=15,
    withdrawal_mean=50,
    withdrawal_std=20
)

payday_records = generate_stream(
    day_type='Payday',
    rate_per_minute=5,        # 5 customers per minute
    service_mean=180,
    service_std=40,
    withdrawal_mean=120,
    withdrawal_std=40
)

# Sample 30% of normal and 70% of payday to reflect realistic day mix
normal_sample = pd.DataFrame(normal_records).sample(frac=0.5, random_state=42)
payday_sample = pd.DataFrame(payday_records).sample(frac=0.3, random_state=42)

# Merge and sort by arrival time
df = pd.concat([normal_sample, payday_sample], ignore_index=True)
df = df.sort_values('arrival_time').reset_index(drop=True)
df.insert(0, 'customer_id', range(1, len(df) + 1))

df.to_csv('data/raw_atm_data.csv', index=False)
print(f"✅ Generated {len(df)} records → saved to data/raw_atm_data.csv")
print(df.head())
print(f"\nDay type counts:\n{df['day_type'].value_counts()}")
print(f"\nMean service times:\n{df.groupby('day_type')['service_time_seconds'].mean()}")