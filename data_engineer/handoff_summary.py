import pandas as pd
import numpy as np

df = pd.read_csv('data/clean_atm_data.csv')
df['arrival_time'] = pd.to_datetime(df['arrival_time'])

SIMULATION_MINUTES = 540  # 8AM to 5PM

# --- Separate lambda per day type ---
normal_df = df[df['day_type'] == 'Normal']
payday_df = df[df['day_type'] == 'Payday']

lambda_normal = len(normal_df) / SIMULATION_MINUTES
lambda_payday = len(payday_df) / SIMULATION_MINUTES

# --- Separate mu per day type ---
mu_normal = 60 / normal_df['service_time_seconds'].mean()
mu_payday = 60 / payday_df['service_time_seconds'].mean()

# --- Overall averages ---
avg_service_normal = normal_df['service_time_seconds'].mean()
avg_service_payday = payday_df['service_time_seconds'].mean()

avg_withdrawal_normal = normal_df['withdrawal_amount_usd'].mean()
avg_withdrawal_payday = payday_df['withdrawal_amount_usd'].mean()

print("=" * 55)
print("       HANDOFF PARAMETERS FOR SIMULATION TEAM")
print("=" * 55)
print(f"\n  📅 NORMAL DAY")
print(f"     λ (arrival rate)  : {lambda_normal:.4f} customers/minute")
print(f"     μ (service rate)  : {mu_normal:.4f} customers/minute")
print(f"     Avg service time  : {avg_service_normal:.2f} seconds")
print(f"     Avg withdrawal    : ${avg_withdrawal_normal:.2f}")
print(f"     Customer count    : {len(normal_df)}")

print(f"\n  💰 PAYDAY")
print(f"     λ (arrival rate)  : {lambda_payday:.4f} customers/minute")
print(f"     μ (service rate)  : {mu_payday:.4f} customers/minute")
print(f"     Avg service time  : {avg_service_payday:.2f} seconds")
print(f"     Avg withdrawal    : ${avg_withdrawal_payday:.2f}")
print(f"     Customer count    : {len(payday_df)}")

print(f"\n  Total clean records : {len(df)}")
print("=" * 55)
print("\n✅ Share these separate λ and μ values with the Simulation Programmer!")