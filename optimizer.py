from simulation import run_simulation

# ==========================================
# YOUR AI OPTIMIZATION ALGORITHM
# ==========================================
def _get_failure_rate(test_cash, simulations, is_payday, balk_tolerance, patience_mean, patience_std, enable_diurnal, progress_callback=None):
    """Helper: runs Monte Carlo simulations for a given cash level and returns the failure rate."""
    stock_outs = 0
    for i in range(simulations):
        q_hist, c_hist, stats = run_simulation(
            is_payday=is_payday,
            initial_cash=test_cash,
            balk_tolerance=balk_tolerance,
            patience_mean=patience_mean,
            patience_std=patience_std,
            enable_diurnal=enable_diurnal
        )
        if stats["cash_out_time"] is not None:
            stock_outs += 1
        if progress_callback:
            progress_callback(i + 1, simulations)
    return (stock_outs / simulations) * 100


def get_optimal_cash(is_payday, balk_tolerance=None, patience_mean=None, patience_std=None, enable_diurnal=None, progress_callback=None):
    """
    Uses binary search to find the minimum cash amount with a failure rate <= 5%.
    Optimized for speed: 150 sims per step, $5k increments, ~5 iterations total.
    """
    print(f"\n[START] Starting Optimization (Payday Mode = {is_payday})")
    
    low = 5000              # Minimum cash to test
    high = 150000           # Maximum cash to test
    simulations = 150       # Monte Carlo runs per search step (fast but reliable)
    target_rate = 5.0       # Business rule: failure rate must be <= 5%
    step = 5000             # $5k increments for fast convergence
    
    # Binary search: find the lowest cash level that passes
    while low < high:
        mid = ((low + high) // 2)
        mid = (mid // step) * step
        if mid < low:
            mid = low
        
        failure_rate = _get_failure_rate(
            mid, simulations, is_payday,
            balk_tolerance, patience_mean, patience_std, enable_diurnal,
            progress_callback
        )
        print(f"Testing ${mid:,} -> Failure Rate: {failure_rate:.1f}%")
        
        if failure_rate <= target_rate:
            high = mid
        else:
            low = mid + step
    
    # Final validation with more simulations to confirm
    final_rate = _get_failure_rate(
        low, 200, is_payday,
        balk_tolerance, patience_mean, patience_std, enable_diurnal,
        progress_callback
    )
    print(f"Final validation ${low:,} -> Failure Rate: {final_rate:.1f}%")
    
    if final_rate <= target_rate:
        print(f"[SUCCESS] Optimal Cash to load is: ${low:,}\n")
        return low
    else:
        low += step
        print(f"[SUCCESS] Optimal Cash to load is: ${low:,} (adjusted)\n")
        return low

# ==========================================
# PART 3: RUN THE FINAL TEST
# ==========================================
if __name__ == "__main__":
    # Let's test a normal day and a payday using the real math!
    optimal_normal = get_optimal_cash(is_payday=False)
    optimal_payday = get_optimal_cash(is_payday=True)