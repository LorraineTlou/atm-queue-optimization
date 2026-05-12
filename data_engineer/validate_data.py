import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

df = pd.read_csv('data/clean_atm_data.csv')
df['arrival_time'] = pd.to_datetime(df['arrival_time'])
df_sorted = df.sort_values('arrival_time').reset_index(drop=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Inter-Arrival Times: Synthetic Data vs Exponential Fit', fontsize=13)

for i, day in enumerate(['Normal', 'Payday']):
    # Filter by day type
    subset = df_sorted[df_sorted['day_type'] == day].copy()
    subset = subset.reset_index(drop=True)

    # Compute inter-arrival times in minutes
    arrival_minutes = (
        subset['arrival_time'] - subset['arrival_time'].iloc[0]
    ).dt.total_seconds() / 60

    inter_arrival = np.diff(arrival_minutes.values)
    inter_arrival = inter_arrival[inter_arrival > 0]

    # KS Test
    loc, scale = stats.expon.fit(inter_arrival, floc=0)
    ks_stat, p_value = stats.kstest(inter_arrival, 'expon', args=(loc, scale))

    print("=" * 50)
    print(f"KS TEST — {day} Day Inter-Arrival Times")
    print(f"  Sample size  : {len(inter_arrival)}")
    print(f"  Mean gap     : {inter_arrival.mean():.4f} minutes")
    print(f"  KS Statistic : {ks_stat:.4f}")
    print(f"  P-Value      : {p_value:.4f}")
    if p_value > 0.05:
        print(f"  ✅ PASS: {day} arrivals follow Exponential distribution")
    else:
        print(f"  ❌ FAIL: {day} arrivals do not fit")
    print("=" * 50)

    # Plot
    axes[i].hist(inter_arrival, bins=40, density=True,
                 alpha=0.6, color='steelblue' if day == 'Normal' else 'coral',
                 label='Synthetic Data')
    x = np.linspace(0, inter_arrival.max(), 300)
    axes[i].plot(x, stats.expon.pdf(x, loc, scale),
                 'r-', linewidth=2, label='Fitted Exponential PDF')
    axes[i].set_title(f'{day} Day')
    axes[i].set_xlabel('Time Between Customers (minutes)')
    axes[i].set_ylabel('Density')
    axes[i].legend()

plt.tight_layout()
plt.savefig('data/arrival_distribution_plot.png', dpi=150)
plt.show()
print("\n📊 Plot saved to data/arrival_distribution_plot.png")