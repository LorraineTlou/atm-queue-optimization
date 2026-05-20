# Local ATM Simulation (Queue & Cash Optimization)

A Monte Carlo simulation and optimization engine built in Python to predict ATM queue lengths and calculate optimal physical USD vault levels during high-stress payday scenarios.

## 🚀 Recent Updates & Key Features

### 1. High-Performance Cash Optimisation (Binary Search)
- Replaced the slow linear search with an optimized **Binary Search** Monte Carlo algorithm.
- Performs 150 simulations per $5k step, rapidly converging on the optimal vault cash level.
- Calculates the **minimum safe amount** to load with a ≤5% failure rate (95% survival) in under **8 seconds**.

### 2. Realistic Queue Dynamics
- **Balking:** Customers evaluate the queue length before joining. Modeled using a Hill equation where probability of joining drops as the queue grows.
- **Reneging:** Customers have patience thresholds and will abandon the queue if their wait time is too long.
- **Diurnal (Time-Varying) Arrivals:** Arrival rates dynamically scale, creating realistic morning, lunch, and afternoon traffic peaks.

### 3. Data-Driven Withdrawal & Service Models
- **Realistic Service Times:** Corrected synthetic ATM transaction times to hardware-realistic levels (~45s normal, ~75s payday). This allows the simulated ATM to process realistic throughput (~430 customers/day max).
- **Mixture Model Withdrawals:** Upgraded from rigid 4-tier fixed amounts to a continuous normal distribution matching the actual dataset parameters.
- **Outlier Salary Collections:** Added an outlier event model where 3-8% of users withdraw between $500–$1,000 to mirror real-world end-of-month salary cash-outs, ensuring realistic vault depletion.

### 4. Enhanced UI/UX Dashboard
- Built with **Streamlit** for a clean, professional presentation.
- Added a new **"How It Works"** tab detailing the underlying math and queuing theory.
- Included interactive toggles for realistic queue behaviors.
- Added secondary metrics tracking Average Wait Time, Customers Unserved, Balking, and Reneging counts.

## 🛠️ How to Run

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the Dashboard:**
   ```bash
   streamlit run app.py
   ```
3. **Data Generation (Optional):**
   If you want to rebuild the synthetic datasets from scratch:
   ```bash
   cd data_engineer
   python generate_data.py
   python clean_data.py
   python handoff_summary.py
   ```

## 📊 Tech Stack
- **Python 3**
- **Streamlit** (Interactive Dashboard UI)
- **NumPy & Pandas** (Data Engineering & Monte Carlo Engine)
- **Matplotlib** (Data Visualization)
