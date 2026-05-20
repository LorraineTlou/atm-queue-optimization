# config.py - Parameters derived from clean_atm_data.csv via handoff_summary.py

# Arrival rate λ (customers per minute)
NORMAL_LAMBDA = 0.9944
PAYDAY_LAMBDA = 1.4630

# Average service time (seconds → converted to minutes)
# Real ATM transaction: insert card → PIN → amount → dispense → receipt
NORMAL_SERVICE_TIME_MIN = 45.37 / 60       # 45.37 sec from dataset
PAYDAY_SERVICE_TIME_MIN = 74.70 / 60       # 74.70 sec from dataset

# Average withdrawal amounts (includes outlier $500-$1,000 salary withdrawals)
NORMAL_AVG_WITHDRAWAL = 64.28
PAYDAY_AVG_WITHDRAWAL = 175.69

# Realistic Queue Behaviour Defaults
BALK_TOLERANCE = 10.0      # Queue length where join probability is 50%
PATIENCE_MEAN = 15.0       # Average minutes a customer is willing to wait
PATIENCE_STD = 4.0         # Standard deviation of customer patience
ENABLE_DIURNAL = True      # Enable time-varying peaks throughout the day