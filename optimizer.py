from simulation import run_simulation

# ==========================================
# YOUR AI OPTIMIZATION ALGORITHM
# ==========================================
def get_optimal_cash(is_payday):
    print(f"\n🚀 Starting Optimization (Payday Mode = {is_payday})")
    
    test_cash = 5000       # We start testing at $5,000
    max_cash = 150000       # We stop testing at $50,000
    simulations = 1000     # Monte Carlo rule: run it 1,000 times
    
    while test_cash <= max_cash:
        stock_outs = 0 
        
        # Run the REAL simulation 1,000 times for THIS specific cash amount
        for _ in range(simulations):
            
            # --- THE INTEGRATION ---
            # We pass your test_cash to her initial_cash parameter
            q_hist, c_hist, stats = run_simulation(is_payday=is_payday, initial_cash=test_cash)
            
            # If cash_out_time is NOT None, the ATM ran out of money!
            if stats["cash_out_time"] is not None:
                stock_outs += 1
                
        # Calculate the failure rate
        failure_rate = (stock_outs / simulations) * 100
        print(f"Testing ${test_cash:,} -> Failure Rate: {failure_rate:.1f}%")
        
        # THE BUSINESS RULE: We want the failure rate to be 5% or less
        if failure_rate <= 5.0:
            print(f"✅ SUCCESS! Optimal Cash to load is: ${test_cash:,}\n")
            return test_cash
            
        # If the failure rate is too high, add $1,000 and try again
        test_cash += 1000

    print("❌ Could not find a safe amount within the limit.")
    return max_cash

# ==========================================
# PART 3: RUN THE FINAL TEST
# ==========================================
if __name__ == "__main__":
    # Let's test a normal day and a payday using the real math!
    optimal_normal = get_optimal_cash(is_payday=False)
    optimal_payday = get_optimal_cash(is_payday=True)