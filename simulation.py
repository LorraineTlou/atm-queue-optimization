import numpy as np
import config

def run_simulation(is_payday=False, initial_cash=10000):
    """
    Runs a discrete-time simulation for a single ATM over one working day (8 AM - 5 PM).
    Total simulation minutes: 540.
    
    Args:
        is_payday (bool): Uses payday parameters if True, otherwise normal parameters.
        initial_cash (float): Starting amount of cash in the ATM.
        
    Returns:
        tuple: (queue_length_history, cash_vault_history, stats)
    """
    # Load parameters based on payday condition from config.py
    if is_payday:
        arr_lambda = config.PAYDAY_LAMBDA
        srv_mean = config.PAYDAY_SERVICE_TIME_MIN
        wd_amounts = [20, 50, 100, 200]
        # Weighted higher for payday
        wd_probs = [0.1, 0.2, 0.4, 0.3] 
    else:
        arr_lambda = config.NORMAL_LAMBDA
        srv_mean = config.NORMAL_SERVICE_TIME_MIN
        wd_amounts = [20, 50, 100, 200]
        # Weighted lower for normal day
        wd_probs = [0.4, 0.3, 0.2, 0.1]
        
    max_minutes = 540
    current_cash = initial_cash
    queue_length = 0
    server_busy_until = 0
    
    queue_length_history = []
    cash_vault_history = []
    
    total_customers_arrived = 0
    total_customers_served = 0
    max_q_len = 0
    cash_out_time = None

    for minute in range(max_minutes):
        # 1. Generate customer arrivals using a Poisson distribution
        arrivals = np.random.poisson(arr_lambda)
        total_customers_arrived += arrivals
        
        # 2. Add arrivals to the queue
        queue_length += arrivals
        
        # 3. If ATM is free and queue > 0, serve one customer
        if minute >= server_busy_until and queue_length > 0:
            # 4. Service time using exponential distribution (Discrete-time fix)
            service_time = max(1, int(np.random.exponential(srv_mean)))
            server_busy_until = minute + service_time
            
            queue_length -= 1
            total_customers_served += 1
            
            # 5 & 6. Withdraw money and check cash limits
            wd = np.random.choice(wd_amounts, p=wd_probs)
            
            if current_cash >= wd:
                current_cash -= wd
            else:
                # Prevent withdrawal if ATM cash is insufficient
                current_cash = 0
                cash_out_time = minute
                queue_length_history.append(queue_length)
                cash_vault_history.append(current_cash)
                break
                
        # Calculate max queue length
        if queue_length > max_q_len:
            max_q_len = queue_length
            
        # 7. Save queue length and cash left for that minute
        queue_length_history.append(queue_length)
        cash_vault_history.append(current_cash)

    # Correct unserved customer statistics
    total_customers_unserved = total_customers_arrived - total_customers_served

    stats = {
        "total_customers_arrived": total_customers_arrived,
        "total_customers_served": total_customers_served,
        "total_customers_unserved": total_customers_unserved,
        "max_queue_length": max_q_len,
        "cash_out_time": cash_out_time
    }
    
    return queue_length_history, cash_vault_history, stats

if __name__ == "__main__":
    np.random.seed(42) # For reproducible output during test run
    
    print("--- Normal Day Simulation ---")
    norm_q_hist, norm_c_hist, normal_stats = run_simulation(is_payday=False, initial_cash=10000)
    for k, v in normal_stats.items():
        print(f"{k}: {v}")
        
    print("\n--- Payday Simulation ---")
    pay_q_hist, pay_c_hist, payday_stats = run_simulation(is_payday=True, initial_cash=10000)
    for k, v in payday_stats.items():
        print(f"{k}: {v}")
