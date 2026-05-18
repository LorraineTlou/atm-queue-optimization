import pandas as pd
import numpy as np

df = pd.read_csv('data/raw_atm_data.csv')
print(f"Records before cleaning: {len(df)}")

# --- STEP 1: Intentionally inject bad data ---
# Simulates real-world dirty data (people who forgot PIN, machine jams, etc.)
bad_indices = np.random.choice(df.index, size=50, replace=False)
df.loc[bad_indices, 'service_time_seconds'] = np.random.uniform(2700, 4500, size=50)
# 2700s = 45 mins, 4500s = 75 mins — clearly abnormal
print(f"🧪 Injected 50 outlier records")

# --- STEP 2: IQR Outlier Removal ---
Q1 = df['service_time_seconds'].quantile(0.25)
Q3 = df['service_time_seconds'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print(f"\nIQR Bounds → Lower: {lower_bound:.2f}s | Upper: {upper_bound:.2f}s")

outliers = df[
    (df['service_time_seconds'] < lower_bound) |
    (df['service_time_seconds'] > upper_bound)
]
print(f"🚨 Outliers detected: {len(outliers)}")

df_clean = df[
    (df['service_time_seconds'] >= lower_bound) &
    (df['service_time_seconds'] <= upper_bound)
].copy()

print(f"✅ Records after cleaning: {len(df_clean)}")
df_clean.to_csv('data/clean_atm_data.csv', index=False)