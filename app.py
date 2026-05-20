import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import config
from simulation import run_simulation
from optimizer import get_optimal_cash

# ==========================================
# PAGE CONFIGURATION & CUSTOM CSS
# ==========================================
st.set_page_config(
    page_title="ATM Queue & Cash Optimization", 
    layout="wide", 
    page_icon="🏦",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Premium aesthetics for a professional pitch */
    .stMetric {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    div[data-testid="stMetricValue"] {
        font-weight: 800;
        color: var(--text-color);
    }
    /* Stylish Primary Button */
    .stButton>button {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.5);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER SECTION
# ==========================================
st.title("🏦 Local ATM Simulation")
st.markdown("**Bulawayo CBD ATM Optimization Dashboard**")
st.markdown("*Simulating a busy ATM to calculate the exact amount of USD cash the bank needs to load, minimizing stock-outs while keeping queues controlled.*")
st.markdown("---")

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/000000/atm.png", width=80)
st.sidebar.header("⚙️ Simulation Controls")
st.sidebar.markdown("Adjust parameters below to see the simulation react in real-time.")

is_payday = st.sidebar.checkbox("🚨 Enable Payday Mode", value=False)

starting_usd = st.sidebar.slider(
    "💵 Starting USD ($)", 
    min_value=1000, 
    max_value=150000, 
    value=15000 if not is_payday else 50000, 
    step=1000
)

# Set dynamic defaults based on payday toggle
default_lambda = config.PAYDAY_LAMBDA if is_payday else config.NORMAL_LAMBDA

arrival_speed = st.sidebar.slider(
    "🚶 Baseline Arrival Speed (Cust/min)", 
    min_value=0.1, 
    max_value=5.0, 
    value=float(default_lambda), 
    step=0.1
)

# ==========================================
# REALISTIC QUEUE BEHAVIOURS TOGGLE
# ==========================================
st.sidebar.markdown("---")
enable_realistic = st.sidebar.checkbox(
    "🧠 Enable Realistic Queue Behaviours",
    value=True,
    help="Turns on Balking, Reneging, and Time-Varying Arrivals. Disable for basic M/M/1 simulation."
)

# Only show realistic controls when the master toggle is ON
if enable_realistic:
    enable_diurnal = st.sidebar.checkbox(
        "📈 Time-Varying Peaks (Diurnal)", 
        value=True, 
        help="Simulates morning, lunch, and afternoon traffic surges rather than a flat, constant arrival rate."
    )

    balk_tolerance = st.sidebar.slider(
        "🙅 Balking Tolerance (Queue Size)", 
        min_value=2, 
        max_value=30, 
        value=int(config.BALK_TOLERANCE), 
        step=1,
        help="The queue size at which an arriving customer has a 50% chance of walking away immediately."
    )

    patience_mean = st.sidebar.slider(
        "⏳ Customer Patience (Mean Min)", 
        min_value=2, 
        max_value=60, 
        value=int(config.PATIENCE_MEAN), 
        step=1,
        help="Average minutes a customer is willing to wait in line before giving up and leaving (reneging)."
    )

    patience_std = st.sidebar.slider(
        "⏳ Customer Patience (Std Dev Min)", 
        min_value=1, 
        max_value=15, 
        value=int(config.PATIENCE_STD), 
        step=1,
        help="Variation in customer patience."
    )
else:
    # Disable all realistic behaviours by using extreme values
    enable_diurnal = False
    balk_tolerance = 9999.0   # Effectively no balking
    patience_mean = 9999.0    # Effectively no reneging
    patience_std = 1.0

# ==========================================
# BACKEND WIRING
# ==========================================
# Override config dynamically so the backend recalculates with the slider's arrival speed
if is_payday:
    config.PAYDAY_LAMBDA = arrival_speed
else:
    config.NORMAL_LAMBDA = arrival_speed

# Force consistent random seed for the live demo so the queue doesn't jitter when only cash is changed.
np.random.seed(42)

# Run the simulation instantly
q_hist, c_hist, stats = run_simulation(
    is_payday=is_payday, 
    initial_cash=starting_usd,
    balk_tolerance=balk_tolerance,
    patience_mean=patience_mean,
    patience_std=patience_std,
    enable_diurnal=enable_diurnal
)

# ==========================================
# TABS: Simulation Dashboard | How It Works
# ==========================================
tab_dashboard, tab_how_it_works = st.tabs(["📊 Simulation Dashboard", "📖 How It Works"])

# ==========================================
# TAB 1: SIMULATION DASHBOARD
# ==========================================
with tab_dashboard:
    # ------ METRICS ------
    st.header("📊 Live Simulation Results (8:00 AM - 5:00 PM)")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Arrivals", f"{stats['total_customers_arrived']} people")
    col2.metric("Successfully Served", f"{stats['total_customers_served']} people")
    col3.metric("Peak Queue Length", f"{stats['max_queue_length']} people")

    if stats['cash_out_time'] is not None:
        hr = 8 + (stats['cash_out_time'] // 60)
        mn = stats['cash_out_time'] % 60
        cash_out_msg = f"{hr:02d}:{mn:02d}"
        col4.metric("Time of Cash Out", cash_out_msg, "- CRITICAL STOCK-OUT", delta_color="inverse")
    else:
        cash_out_msg = "N/A"
        col4.metric("Time of Cash Out", "N/A", "SAFE (Did not run out)")

    # Second row for realistic queueing behaviors
    if enable_realistic:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Average Wait Time", f"{stats['avg_wait_time']:.1f} mins")
        col6.metric("Balked (Walked Away)", f"{stats['total_balked']} people")
        col7.metric("Reneged (Gave Up Waiting)", f"{stats['total_reneged']} people")
        col8.metric("Total Unserved", f"{stats['total_customers_unserved']} people")

    # ------ GRAPHS ------
    time_axis = [8 + (m / 60) for m in range(len(q_hist))]

    col_graph1, col_graph2 = st.columns(2)

    with col_graph1:
        st.subheader("🚶 Queue Dynamics vs Time")
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        
        ax1.plot(time_axis, q_hist, color="#d32f2f", linewidth=2.5, label="Queue Length")
        ax1.set_xlabel("Time of Day (Hours)")
        ax1.set_ylabel("Queue Length (People)", color="#d32f2f")
        ax1.set_xlim(8, 17)
        ax1.tick_params(axis='y', labelcolor="#d32f2f")
        
        ax1.grid(True, linestyle="--", alpha=0.3, color="gray")
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.xaxis.label.set_color('gray')
        ax1.tick_params(axis='x', colors='gray')
        ax1.spines['bottom'].set_color('gray')
        ax1.spines['left'].set_color('gray')
        
        if enable_diurnal and "arrival_rates_history" in stats:
            ax1_twin = ax1.twinx()
            arr_time = [8 + (m / 60) for m in range(len(stats["arrival_rates_history"]))]
            ax1_twin.plot(arr_time, stats["arrival_rates_history"], color="#ff9800", linestyle=":", linewidth=2, label="Arrival Rate")
            ax1_twin.set_ylabel("Arrival Rate (Cust/min)", color="#ff9800")
            ax1_twin.tick_params(axis='y', labelcolor="#ff9800")
            ax1_twin.spines['top'].set_visible(False)
            ax1_twin.spines['left'].set_visible(False)
            ax1_twin.spines['right'].set_color('#ff9800')
            ax1_twin.spines['right'].set_visible(True)
            
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
        else:
            ax1.legend(loc="upper right")
            
        st.pyplot(fig1, transparent=True)

    with col_graph2:
        st.subheader("💵 Vault Cash Depletion vs Time")
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        
        ax2.plot(time_axis, c_hist, color="#388e3c", linewidth=2.5)
        ax2.fill_between(time_axis, c_hist, color="#388e3c", alpha=0.1)
        
        ax2.set_xlabel("Time of Day (Hours)")
        ax2.set_ylabel("Remaining Cash (USD)")
        ax2.set_xlim(8, 17)
        
        y_max = max(starting_usd * 1.1, 100)
        ax2.set_ylim(0, y_max)
        
        if stats['cash_out_time'] is not None:
            stockout_time = 8 + (stats['cash_out_time'] / 60)
            ax2.axvline(x=stockout_time, color="red", linestyle="--", linewidth=2, label=f"Stock-Out @ {cash_out_msg}")
            ax2.legend(loc="upper right", frameon=True, shadow=True)
            
        ax2.grid(True, linestyle="--", alpha=0.3, color="gray")
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.xaxis.label.set_color('gray')
        ax2.yaxis.label.set_color('gray')
        ax2.tick_params(axis='x', colors='gray')
        ax2.tick_params(axis='y', colors='gray')
        ax2.spines['bottom'].set_color('gray')
        ax2.spines['left'].set_color('gray')
        
        st.pyplot(fig2, transparent=True)

    st.markdown("---")

    # ------ OPTIMIZER ------
    st.header("💰 Cash Optimisation")
    st.write("Click below to automatically determine the **minimum safe amount** of cash to load so the ATM survives 95% of possible days.")

    if st.button("🚀 Run Optimizer Algorithm", type="primary"):
        progress_bar = st.progress(0, text="Starting optimization...")
        status_text = st.empty()
        
        step_count = [0]
        total_steps_estimate = [8]  # Binary search over $5k–$150k in $1k steps ≈ 8 iterations
        
        def update_progress(sim_num, sim_total):
            overall = min((step_count[0] * sim_total + sim_num) / (total_steps_estimate[0] * sim_total), 0.99)
            progress_bar.progress(overall, text=f"Step {step_count[0]+1}: Running simulation {sim_num}/{sim_total}...")
            if sim_num == sim_total:
                step_count[0] += 1
        
        optimal_cash = get_optimal_cash(
            is_payday,
            balk_tolerance=balk_tolerance,
            patience_mean=patience_mean,
            patience_std=patience_std,
            enable_diurnal=enable_diurnal,
            progress_callback=update_progress
        )
        
        progress_bar.progress(1.0, text="Optimization complete!")
        st.success(f"### ✅ Optimization Complete!\n"
                   f"To survive this scenario safely with a less than 5% failure rate, the bank must load exactly **${optimal_cash:,}**.")

# ==========================================
# TAB 2: HOW IT WORKS
# ==========================================
with tab_how_it_works:
    st.header("📖 How This Simulation Works")
    st.markdown("""
    This dashboard simulates a **single ATM in the Bulawayo CBD** over one full working day 
    (8:00 AM to 5:00 PM = 540 minutes). Every minute of the simulated day, the system generates 
    random customer arrivals, processes the queue, and depletes cash from the vault.
    """)

    st.markdown("---")

    # --- Concept 1: The Basic Simulation ---
    st.subheader("1️⃣ The Basic Simulation (M/M/1 Queue)")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("""
        At its core, this is a **Poisson arrival + Exponential service** model:
        
        - **Arrivals**: Each minute, a random number of customers arrive. The number follows a 
          [Poisson distribution](https://en.wikipedia.org/wiki/Poisson_distribution) with rate **λ** 
          (the "Arrival Speed" slider).
        - **Service**: When the ATM is free, the next customer in the queue is served. The time it takes 
          follows an [Exponential distribution](https://en.wikipedia.org/wiki/Exponential_distribution) 
          based on the average transaction time from our survey data.
        - **Cash Withdrawal**: Each served customer withdraws a random amount ($20, $50, $100, or $200) 
          weighted by the day type. The ATM's cash vault decreases accordingly.
        - **Stock-Out**: If the vault hits $0, the ATM shuts down — this is the "failure" we're trying to prevent.
        """)
    with col_b:
        st.info("💡 **Key Insight**: On a normal day, ~0.95 customers arrive per minute. "
                "On payday, that jumps to ~1.46 — a 53% surge.")

    st.markdown("---")

    # --- Concept 2: Realistic Queue Behaviours ---
    st.subheader("2️⃣ Realistic Queue Behaviours")
    st.markdown("When the **🧠 Enable Realistic Queue Behaviours** toggle is ON, three additional "
                "real-world effects are simulated:")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    
    with col_c1:
        st.markdown("#### 🙅 Balking")
        st.markdown("""
        **What it is**: A customer arrives, sees a long queue, and **walks away without joining**.
        
        **How it works**: The probability of joining decreases as the queue grows:
        
        *P(join) = 1 / (1 + (Q / K)²)*
        
        Where **Q** is the current queue length and **K** is the "Balking Tolerance" slider.
        
        - If K = 10, a queue of 10 people means only a **50% chance** of joining.
        - If K = 5, the same queue of 10 means only a **20% chance**.
        """)
        
    with col_c2:
        st.markdown("#### 😤 Reneging")
        st.markdown("""
        **What it is**: A customer **joins the queue** but **leaves** if they wait too long.
        
        **How it works**: Each customer gets a random "patience limit" drawn from a 
        Normal distribution:
        
        *patience ~ N(μ, σ)*
        
        Where **μ** is the "Customer Patience Mean" slider. If their wait time exceeds 
        their patience, they leave the queue and are counted as "Reneged".
        """)
        
    with col_c3:
        st.markdown("#### 📈 Time-Varying Arrivals")
        st.markdown("""
        **What it is**: Customer traffic isn't flat throughout the day. It **peaks** during:
        
        - 🌅 **Morning rush** (~9:00 AM)
        - 🍽️ **Lunch break** (~12:45 PM)  
        - 🌇 **End-of-day** (~4:30 PM)
        
        **How it works**: The base arrival rate λ is multiplied by a time-dependent curve 
        (sum of Gaussian peaks). The orange dotted line on the Queue Dynamics chart 
        shows this curve in action.
        """)

    st.markdown("---")

    # --- Concept 3: The Optimizer ---
    st.subheader("3️⃣ AI Cash Optimization (Monte Carlo + Binary Search)")
    st.markdown("""
    The optimizer answers: ***"What is the minimum amount of cash to load so the ATM survives 95% of possible days?"***
    """)
    
    col_d, col_e = st.columns([3, 2])
    with col_d:
        st.markdown("""
        **Step-by-step:**
        
        1. **Pick a cash amount** to test (e.g., $50,000).
        2. **Run 500 simulated days** (Monte Carlo) with that amount — each with random arrivals, 
           withdrawals, balking, reneging, and peak hours.
        3. **Count failures** — a "failure" is any day where the ATM ran out of cash before 5 PM.
        4. **Calculate the failure rate**: failures ÷ 500 × 100%.
        5. **Binary search**: If the rate is ≤ 5%, try a lower amount. If > 5%, try a higher amount. 
           Repeat until we converge on the **minimum safe amount**.
        
        This binary search approach tests only ~8 cash levels instead of 145 (the old linear scan), 
        making it **~20x faster**.
        """)
    with col_e:
        st.warning("⚠️ **Why 5%?**\n\n"
                   "The 5% failure threshold is a business decision. It means: *\"We accept that 1 in 20 "
                   "days the ATM may run dry — but 19 out of 20 days, customers will be served.\"* \n\n"
                   "You can adjust this threshold in the code (`target_rate` in `optimizer.py`).")

    st.markdown("---")
    
    # --- Concept 4: Interpreting the Dashboard ---
    st.subheader("4️⃣ How to Read the Dashboard")
    st.markdown("""
    | Metric | What It Means |
    |---|---|
    | **Total Arrivals** | Number of customers who showed up at the ATM that day |
    | **Successfully Served** | Customers who completed their transaction |
    | **Peak Queue Length** | Longest the queue got at any point in the day |
    | **Time of Cash Out** | When the ATM ran out of money (N/A = survived the whole day) |
    | **Average Wait Time** | Mean time a served customer spent waiting in line |
    | **Balked** | Customers who saw the queue and walked away |
    | **Reneged** | Customers who joined the queue but left before being served |
    | **Total Unserved** | Balked + Reneged + still in queue at closing |
    """)
