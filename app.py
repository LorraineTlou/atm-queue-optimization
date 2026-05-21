import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import config
from simulation import run_simulation
from optimizer import get_optimal_cash

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Local ATM Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# PROFESSIONAL CSS DESIGN SYSTEM
# ==========================================
st.markdown("""
<style>
    /* ---------- Google Font ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ---------- Fade-in animation ---------- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ---------- Header banner ---------- */
    .header-banner {
        text-align: center;
        padding: 1rem 0 2rem 0;
        margin-bottom: 0.5rem;
        animation: fadeInUp 0.6s ease-out;
    }
    .header-banner h1 {
        color: var(--text-color);
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0 0 0.25rem 0;
        letter-spacing: -0.5px;
    }
    .header-banner p {
        color: var(--text-color);
        opacity: 0.7;
        font-size: 1rem;
        margin: 0;
        font-weight: 500;
    }

    /* ---------- Metric cards ---------- */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg,
            var(--secondary-background-color) 0%,
            color-mix(in srgb, var(--secondary-background-color) 85%, #0ea5e9) 100%);
        padding: 1.1rem 1.25rem;
        border-radius: 12px;
        border: 1px solid rgba(14, 165, 233, 0.12);
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        animation: fadeInUp 0.5s ease-out both;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(14,165,233,0.12);
    }
    /* stagger the card animations */
    .stColumns > div:nth-child(1) div[data-testid="stMetric"] { animation-delay: 0.05s; }
    .stColumns > div:nth-child(2) div[data-testid="stMetric"] { animation-delay: 0.12s; }
    .stColumns > div:nth-child(3) div[data-testid="stMetric"] { animation-delay: 0.19s; }
    .stColumns > div:nth-child(4) div[data-testid="stMetric"] { animation-delay: 0.26s; }

    div[data-testid="stMetricValue"] {
        font-weight: 800;
        font-size: 1.6rem;
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.5px;
        opacity: 0.7;
    }

    /* ---------- Primary button ---------- */
    .stButton > button[kind="primary"],
    .stButton > button {
        background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
        color: #ffffff;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        letter-spacing: 0.3px;
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(30, 64, 175, 0.35);
        color: #ffffff;
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid rgba(128,128,128,0.15);
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.75rem 1.5rem;
        border-radius: 8px 8px 0 0;
        transition: background 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #0ea5e9;
    }

    /* ---------- Subheaders ---------- */
    h2, h3 {
        animation: fadeInUp 0.4s ease-out both;
    }

    /* ---------- Sidebar polish ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,
            var(--secondary-background-color) 0%,
            color-mix(in srgb, var(--secondary-background-color) 92%, #0f172a) 100%);
    }
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stCheckbox label {
        font-weight: 500;
        font-size: 0.85rem;
    }

    /* ---------- Divider ---------- */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(14,165,233,0.25), transparent);
        margin: 1.5rem 0;
    }

    /* ---------- Charts fade in ---------- */
    .stPlotlyChart, iframe, .stImage, img {
        animation: fadeInUp 0.5s ease-out both;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("Simulation Controls")

is_payday = st.sidebar.checkbox("Enable Payday Mode", value=False)

starting_usd = st.sidebar.slider(
    "Starting Cash (USD)",
    min_value=1000,
    max_value=150000,
    value=15000 if not is_payday else 50000,
    step=1000
)

default_lambda = config.PAYDAY_LAMBDA if is_payday else config.NORMAL_LAMBDA

arrival_speed = st.sidebar.slider(
    "Arrival Rate (Customers/min)",
    min_value=0.1,
    max_value=5.0,
    value=float(default_lambda),
    step=0.1
)

st.sidebar.markdown("---")
enable_realistic = st.sidebar.checkbox(
    "Enable Realistic Queue Behaviours",
    value=True,
    help="Turns on Balking, Reneging, and Time-Varying Arrivals."
)

if enable_realistic:
    enable_diurnal = st.sidebar.checkbox(
        "Time-Varying Peaks (Diurnal)",
        value=True,
        help="Simulates morning, lunch, and afternoon traffic surges."
    )

    balk_tolerance = st.sidebar.slider(
        "Balking Tolerance (Queue Size)",
        min_value=2,
        max_value=30,
        value=int(config.BALK_TOLERANCE),
        step=1,
        help="Queue size at which joining probability is 50%."
    )

    patience_mean = st.sidebar.slider(
        "Customer Patience (Mean Min)",
        min_value=2,
        max_value=60,
        value=int(config.PATIENCE_MEAN),
        step=1,
        help="Average minutes a customer waits before leaving."
    )

    patience_std = st.sidebar.slider(
        "Customer Patience (Std Dev Min)",
        min_value=1,
        max_value=15,
        value=int(config.PATIENCE_STD),
        step=1,
        help="Variation in customer patience."
    )
else:
    enable_diurnal = False
    balk_tolerance = 9999.0
    patience_mean = 9999.0
    patience_std = 1.0

# ==========================================
# BACKEND WIRING
# ==========================================
if is_payday:
    config.PAYDAY_LAMBDA = arrival_speed
else:
    config.NORMAL_LAMBDA = arrival_speed

np.random.seed(42)

q_hist, c_hist, stats = run_simulation(
    is_payday=is_payday,
    initial_cash=starting_usd,
    balk_tolerance=balk_tolerance,
    patience_mean=patience_mean,
    patience_std=patience_std,
    enable_diurnal=enable_diurnal
)

# ==========================================
# HEADER
# ==========================================
st.markdown("""
<div class="header-banner">
    <h1>Local ATM Simulation</h1>
    <p>Bulawayo CBD  |  Single ATM  |  8:00 AM – 5:00 PM</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# TABS
# ==========================================
tab_dashboard, tab_how = st.tabs(["Simulation Dashboard", "How It Works"])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab_dashboard:

    # --- Primary Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Arrivals", f"{stats['total_customers_arrived']}", 
                help="Total number of customers who arrived at the ATM location today.")
    col2.metric("Served", f"{stats['total_customers_served']}", 
                help="Customers who successfully completed a cash withdrawal.")
    col3.metric("Peak Queue", f"{stats['max_queue_length']}", 
                help="The maximum number of people waiting in line at any one time.")

    if stats['cash_out_time'] is not None:
        hr = 8 + (stats['cash_out_time'] // 60)
        mn = stats['cash_out_time'] % 60
        cash_out_msg = f"{hr:02d}:{mn:02d}"
        col4.metric("Cash-Out Time", cash_out_msg, "STOCK-OUT", delta_color="inverse", 
                    help="The exact time the ATM ran out of cash. If safe, it survived until 5:00 PM.")
    else:
        cash_out_msg = "N/A"
        col4.metric("Cash-Out Time", "N/A", "Safe", 
                    help="The exact time the ATM ran out of cash. If safe, it survived until 5:00 PM.")

    # --- Secondary Metrics (realistic mode) ---
    if enable_realistic:
        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Avg Wait", f"{stats['avg_wait_time']:.1f} min", 
                    help="The average time successfully served customers spent waiting in line.")
        col6.metric("Balked", f"{stats['total_balked']}", 
                    help="Customers who saw the long queue and walked away immediately.")
        col7.metric("Reneged", f"{stats['total_reneged']}", 
                    help="Customers who joined the queue but gave up and left after waiting too long.")
        col8.metric("Total Unserved", f"{stats['total_customers_unserved']}", 
                    f"{stats.get('left_in_queue', 0)} left in queue", delta_color="off",
                    help="Unserved = Balked + Reneged + Left in Queue at closing/stock-out.")

    st.markdown("---")

    # --- Graphs ---
    # Use white text so charts are legible in dark mode
    CHART_TEXT = "#e2e8f0"
    CHART_GRID = "rgba(255,255,255,0.1)"
    time_axis = [8 + (m / 60) for m in range(len(q_hist))]

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Queue Length vs Time")
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        fig1.patch.set_alpha(0)

        ax1.plot(time_axis, q_hist, color="#ef5350", linewidth=2, label="Queue Length")
        ax1.set_xlabel("Time of Day (Hours)", color=CHART_TEXT)
        ax1.set_ylabel("Queue Length", color="#ef5350")
        ax1.set_xlim(8, 17)
        ax1.set_facecolor("none")
        ax1.tick_params(axis='x', colors=CHART_TEXT)
        ax1.tick_params(axis='y', labelcolor="#ef5350")
        ax1.grid(True, linestyle="--", alpha=0.15, color="white")
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['bottom'].set_color(CHART_TEXT)
        ax1.spines['left'].set_color(CHART_TEXT)

        if enable_diurnal and "arrival_rates_history" in stats:
            ax1_twin = ax1.twinx()
            arr_time = [8 + (m / 60) for m in range(len(stats["arrival_rates_history"]))]
            ax1_twin.plot(arr_time, stats["arrival_rates_history"], color="#ffb74d", linestyle=":", linewidth=1.5, label="Arrival Rate")
            ax1_twin.set_ylabel("Arrival Rate (cust/min)", color="#ffb74d")
            ax1_twin.tick_params(axis='y', labelcolor="#ffb74d")
            ax1_twin.spines['top'].set_visible(False)
            ax1_twin.spines['right'].set_color("#ffb74d")

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize="small",
                       facecolor="#1e293b", edgecolor="#334155", labelcolor=CHART_TEXT)
        else:
            ax1.legend(loc="upper right", fontsize="small",
                       facecolor="#1e293b", edgecolor="#334155", labelcolor=CHART_TEXT)

        st.pyplot(fig1, transparent=True)

    with col_g2:
        st.subheader("Vault Cash Depletion vs Time")
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        fig2.patch.set_alpha(0)

        ax2.plot(time_axis, c_hist, color="#66bb6a", linewidth=2)
        ax2.fill_between(time_axis, c_hist, color="#66bb6a", alpha=0.08)
        ax2.set_xlabel("Time of Day (Hours)", color=CHART_TEXT)
        ax2.set_ylabel("Remaining Cash (USD)", color=CHART_TEXT)
        ax2.set_xlim(8, 17)
        ax2.set_ylim(0, max(starting_usd * 1.1, 100))
        ax2.set_facecolor("none")
        ax2.tick_params(axis='x', colors=CHART_TEXT)
        ax2.tick_params(axis='y', colors=CHART_TEXT)
        ax2.grid(True, linestyle="--", alpha=0.15, color="white")
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_color(CHART_TEXT)
        ax2.spines['left'].set_color(CHART_TEXT)

        if stats['cash_out_time'] is not None:
            stockout_time = 8 + (stats['cash_out_time'] / 60)
            ax2.axvline(x=stockout_time, color="#ef5350", linestyle="--", linewidth=1.5, label=f"Stock-Out @ {cash_out_msg}")
            ax2.legend(loc="upper right", fontsize="small",
                       facecolor="#1e293b", edgecolor="#334155", labelcolor=CHART_TEXT)

        st.pyplot(fig2, transparent=True)

    st.markdown("---")

    # --- Cash Optimisation ---
    st.subheader("Cash Optimisation")
    st.write("Determine the minimum safe cash to load so the ATM survives 95% of possible days.")

    if st.button("Run Optimiser", type="primary"):
        progress_bar = st.progress(0, text="Starting...")
        step_count = [0]
        total_steps_estimate = [8]

        def update_progress(sim_num, sim_total):
            overall = min((step_count[0] * sim_total + sim_num) / (total_steps_estimate[0] * sim_total), 0.99)
            progress_bar.progress(overall, text=f"Step {step_count[0]+1}: simulation {sim_num}/{sim_total}")
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

        progress_bar.progress(1.0, text="Done.")
        st.success(f"Optimal cash to load: **${optimal_cash:,}** (failure rate <= 5%)")

# ==========================================
# TAB 2: HOW IT WORKS
# ==========================================
with tab_how:
    st.header("How This Simulation Works")
    st.markdown("""
    This dashboard simulates a **single ATM in the Bulawayo CBD** over one working day 
    (8 AM - 5 PM, 540 minutes). Every simulated minute, the system generates 
    random customer arrivals, processes the queue, and depletes cash from the vault.
    """)

    st.markdown("---")

    st.subheader("1. The Basic Simulation (M/M/1 Queue)")
    st.markdown("""
    - **Arrivals**: Each minute, a random number of customers arrive following a 
      Poisson distribution with rate lambda (the Arrival Rate slider).
    - **Service**: When the ATM is free, the next customer is served. Service time 
      follows an Exponential distribution based on survey data (~45s normal, ~75s payday).
    - **Cash Withdrawal**: Each served customer withdraws a random amount drawn from a 
      continuous distribution (mean ~$64 normal, ~$176 payday). About 3-8% of customers 
      make large salary withdrawals of $500-$1,000.
    - **Stock-Out**: If the vault hits $0, the ATM shuts down.
    """)

    st.markdown("---")

    st.subheader("2. Realistic Queue Behaviours")
    st.markdown("When the **Enable Realistic Queue Behaviours** toggle is ON, three effects are added:")

    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        st.markdown("#### Balking")
        st.markdown("""
        A customer arrives, sees a long queue, and **walks away**.

        Probability of joining:  
        *P(join) = 1 / (1 + (Q / K)^2)*

        Where Q is queue length and K is the Balking Tolerance slider.
        """)

    with col_c2:
        st.markdown("#### Reneging")
        st.markdown("""
        A customer **joins** the queue but **leaves** if they wait too long.

        Each customer gets a random patience limit:  
        *patience ~ N(mean, std)*

        If wait time exceeds patience, they leave.
        """)

    with col_c3:
        st.markdown("#### Time-Varying Arrivals")
        st.markdown("""
        Traffic peaks during:
        - Morning rush (~9:00 AM)
        - Lunch break (~12:45 PM)
        - End-of-day (~4:30 PM)

        The base arrival rate is multiplied by a Gaussian sum curve.
        The orange dotted line on the chart shows this.
        """)

    st.markdown("---")

    st.subheader("3. Cash Optimisation (Monte Carlo + Binary Search)")
    st.markdown("""
    The optimiser answers: *"What is the minimum cash to load so the ATM survives 95% of days?"*

    **Steps:**
    1. Pick a cash amount to test (e.g. $50,000).
    2. Run 150 simulated days (Monte Carlo) with that amount.
    3. Count failures — any day the ATM ran out before 5 PM.
    4. Calculate failure rate: failures / 150 x 100%.
    5. Binary search: if rate <= 5%, try lower. If > 5%, try higher. Repeat until converged.

    This tests ~5 cash levels instead of scanning linearly, completing in under 10 seconds.
    """)

    st.markdown("---")

    st.subheader("4. Reading the Dashboard")
    st.markdown("""
    | Metric | Meaning |
    |---|---|
    | **Total Arrivals** | Customers who showed up at the ATM |
    | **Served** | Customers who completed a transaction |
    | **Peak Queue** | Longest queue at any point in the day |
    | **Cash-Out Time** | When the ATM ran out of money (N/A = survived) |
    | **Avg Wait** | Mean wait time for served customers |
    | **Balked** | Walked away without joining the queue |
    | **Reneged** | Joined the queue but left before being served |
    | **Total Unserved** | Balked + Reneged + still queued at closing |
    """)
