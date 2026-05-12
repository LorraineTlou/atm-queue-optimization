import pandas as pd
import numpy as np

df = pd.read_csv('data/clean_atm_data.csv')
df['arrival_time'] = pd.to_datetime(df['arrival_time'])

# Duration of the simulation window
total_minutes = (
    df['arrival_time'].max() - df['arrival_time'].min()
).total_seconds() / 60

# λ = average arrival rate (customers per minute)
lambda_overall = len(df) / total_minutes

# μ = average service rate (customers per minute)
avg_service_seconds = df['service_time_seconds'].mean()
mu_overall = 60 / avg_service_seconds  # convert to per-minute rate

# Breakdown by day type
summary = df.groupby('day_type').agg(
    avg_service_time=('service_time_seconds', 'mean'),
    avg_withdrawal=('withdrawal_amount_usd', 'mean'),
    count=('customer_id', 'count')
)

print("=" * 55)
print("       HANDOFF PARAMETERS FOR SIMULATION TEAM")
print("=" * 55)
print(f"  λ (arrival rate)  : {lambda_overall:.4f} customers/minute")
print(f"  μ (service rate)  : {mu_overall:.4f} customers/minute")
print(f"  Avg service time  : {avg_service_seconds:.2f} seconds")
print(f"  Total customers   : {len(df)}")
print("\n  Breakdown by Day Type:")
print(summary.to_string())
print("=" * 55)
print("\n✅ Share these λ and μ values with the Simulation Programmer!")