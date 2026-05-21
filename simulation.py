import numpy as np
import config

def get_diurnal_multiplier(minute):
    """
    Returns the arrival rate multiplier for a given minute of the working day.
    Morning peak: around 9:00 AM (minute 60)
    Lunch peak: around 12:45 PM (minute 285)
    Afternoon peak: around 4:30 PM (minute 510)
    """
    hour = 8.0 + (minute / 60.0)
    m_peak = 1.8 * np.exp(-((hour - 9.0) / 0.5)**2)
    l_peak = 2.2 * np.exp(-((hour - 12.75) / 0.75)**2)
    a_peak = 1.5 * np.exp(-((hour - 16.5) / 0.5)**2)
    return 0.4 + m_peak + l_peak + a_peak

def run_simulation(is_payday=False, initial_cash=10000, 
                   balk_tolerance=None, patience_mean=None, patience_std=None, 
                   enable_diurnal=None):
    """
    Runs a discrete-time simulation for a single ATM over one working day (8 AM - 5 PM).
    Total simulation minutes: 540.
    
    Args:
        is_payday (bool): Uses payday parameters if True, otherwise normal parameters.
        initial_cash (float): Starting amount of cash in the ATM.
        balk_tolerance (float): Queue size at which joining probability is 50%.
        patience_mean (float): Average customer patience limit in minutes.
        patience_std (float): Standard deviation of customer patience.
        enable_diurnal (bool): Whether to simulate peak hours.
        
    Returns:
        tuple: (queue_length_history, cash_vault_history, stats)
    """
    # Load parameters from config if not provided
    if balk_tolerance is None:
        balk_tolerance = config.BALK_TOLERANCE
    if patience_mean is None:
        patience_mean = config.PATIENCE_MEAN
    if patience_std is None:
        patience_std = config.PATIENCE_STD
    if enable_diurnal is None:
        enable_diurnal = config.ENABLE_DIURNAL

    # Load parameters based on payday condition from config.py
    if is_payday:
        arr_lambda = config.PAYDAY_LAMBDA
        srv_mean = config.PAYDAY_SERVICE_TIME_MIN
        wd_mean = config.PAYDAY_AVG_WITHDRAWAL   # ~$116.78
        wd_std = 40.0                             # From dataset: std=$40
    else:
        arr_lambda = config.NORMAL_LAMBDA
        srv_mean = config.NORMAL_SERVICE_TIME_MIN
        wd_mean = config.NORMAL_AVG_WITHDRAWAL    # ~$51.66
        wd_std = 20.0                             # From dataset: std=$20
        
    max_minutes = 540
    current_cash = initial_cash
    queue = []  # Will hold customer dicts: {"arrival_time": m, "patience": p}
    server_busy_until = 0
    
    queue_length_history = []
    cash_vault_history = []
    arrival_rates_history = []
    
    total_customers_arrived = 0
    total_customers_served = 0
    total_balked = 0
    total_reneged = 0
    served_wait_times = []
    max_q_len = 0
    cash_out_time = None

    # Precalculate and normalize diurnal multipliers to ensure consistent average arrival rates
    raw_multipliers = [get_diurnal_multiplier(m) for m in range(max_minutes)]
    mean_multiplier = np.mean(raw_multipliers)
    norm_multipliers = [m / mean_multiplier for m in raw_multipliers]

    for minute in range(max_minutes):
        # 1. Determine the arrival rate for this minute
        if enable_diurnal:
            lambda_t = arr_lambda * norm_multipliers[minute]
        else:
            lambda_t = arr_lambda
        arrival_rates_history.append(lambda_t)

        # 2. Generate customer arrivals using a Poisson distribution
        arrivals = np.random.poisson(lambda_t)
        total_customers_arrived += arrivals
        
        # 3. Process arrivals (balking check)
        for _ in range(arrivals):
            current_q_len = len(queue)
            # Probability of joining: Hill equation
            p_join = 1.0 / (1.0 + (current_q_len / balk_tolerance)**2)
            if np.random.random() < p_join:
                # Customer joins the queue with a randomized patience
                pat = max(2.0, np.random.normal(patience_mean, patience_std))
                queue.append({"arrival_time": minute, "patience": pat})
            else:
                total_balked += 1
                
        # 4. Process queue reneging (customers leaving due to long wait times)
        next_queue = []
        for customer in queue:
            wait_time = minute - customer["arrival_time"]
            if wait_time > customer["patience"]:
                total_reneged += 1
            else:
                next_queue.append(customer)
        queue = next_queue
        
        # 5. Serve customer if ATM is free and queue has people
        if minute >= server_busy_until and len(queue) > 0:
            customer = queue.pop(0)
            wait_time = minute - customer["arrival_time"]
            served_wait_times.append(wait_time)
            
            # Service time using exponential distribution
            service_time = max(1, int(np.random.exponential(srv_mean)))
            server_busy_until = minute + service_time
            
            total_customers_served += 1
            
            # Process cash withdrawal (mixture model with outlier support)
            # Small chance of a large "salary collection" withdrawal ($500–$1,000)
            if np.random.random() < (0.08 if is_payday else 0.03):
                # Outlier: large withdrawal
                wd = round(float(np.random.uniform(500, 1000)), 2)
            else:
                # Normal withdrawal from survey distribution
                wd = round(float(np.clip(np.random.normal(wd_mean, wd_std), 10, 500)), 2)
            if current_cash >= wd:
                current_cash -= wd
            else:
                current_cash = 0
                cash_out_time = minute
                queue_length_history.append(len(queue))
                cash_vault_history.append(current_cash)
                break
                
        # Calculate max queue length
        if len(queue) > max_q_len:
            max_q_len = len(queue)
            
        # Save histories
        queue_length_history.append(len(queue))
        cash_vault_history.append(current_cash)

    # Customers still in the queue at the end of the day are unserved
    left_in_queue = len(queue)
    total_customers_unserved = total_balked + total_reneged + left_in_queue
    avg_wait = np.mean(served_wait_times) if len(served_wait_times) > 0 else 0.0

    stats = {
        "total_customers_arrived": total_customers_arrived,
        "total_customers_served": total_customers_served,
        "total_customers_unserved": total_customers_unserved,
        "total_balked": total_balked,
        "total_reneged": total_reneged,
        "left_in_queue": left_in_queue,
        "avg_wait_time": avg_wait,
        "max_queue_length": max_q_len,
        "cash_out_time": cash_out_time,
        "arrival_rates_history": arrival_rates_history
    }
    
    return queue_length_history, cash_vault_history, stats

if __name__ == "__main__":
    np.random.seed(42) # For reproducible output during test run
    
    print("--- Normal Day Simulation ---")
    norm_q_hist, norm_c_hist, normal_stats = run_simulation(is_payday=False, initial_cash=10000)
    for k, v in normal_stats.items():
        if k != "arrival_rates_history":
            print(f"{k}: {v}")
        
    print("\n--- Payday Simulation ---")
    pay_q_hist, pay_c_hist, payday_stats = run_simulation(is_payday=True, initial_cash=10000)
    for k, v in payday_stats.items():
        if k != "arrival_rates_history":
            print(f"{k}: {v}")
