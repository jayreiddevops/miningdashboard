import streamlit as st
import requests
from datetime import datetime, timezone

st.set_page_config(page_title="⛏️ Mining Dashboard", layout="wide")

# -------------------------------
# 🔧 CONFIG
# -------------------------------
POOL_API = "https://api.woolypooly.com/api/v1/miner/kas/{wallet}/stats"
COIN_PRICE_API = "https://api.coingecko.com/api/v3/simple/price?ids=kaspa&vs_currencies=usd"
WALLET = "qrn6q4hywx4z9j4hmdp6vt4ec3a7w80akde3j26cpanz3crn89wq6rr6n2j7s"
RIG_NAME = "vast4090"

# -------------------------------
# 🧮 FUNCTIONS
# -------------------------------
def get_pool_stats(wallet):
    try:
        res = requests.get(POOL_API.format(wallet=wallet))
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Pool API error: {res.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to pool: {e}")
        return None

def get_kaspa_price():
    try:
        res = requests.get(COIN_PRICE_API)
        if res.status_code == 200:
            return res.json()["kaspa"]["usd"]
        else:
            return None
    except:
        return None

def calc_profit(daily_kas, kas_price, daily_cost):
    income_usd = daily_kas * kas_price
    profit = income_usd - daily_cost
    return income_usd, profit

# -------------------------------
# 🧭 SIDEBAR SETTINGS
# -------------------------------
st.sidebar.header("⚙️ Settings")
daily_cost = st.sidebar.number_input("Daily Miner Cost (USD)", min_value=0.0, value=5.00, step=0.5)
refresh = st.sidebar.button("🔄 Refresh Data")

# -------------------------------
# 📊 MAIN DASHBOARD
# -------------------------------
st.title("⛏️ Kaspa Mining Dashboard")
st.caption("Real-time profit tracking and pool performance")

pool_data = get_pool_stats(WALLET)
kas_price = get_kaspa_price()

if pool_data and kas_price:
    # Extract relevant stats
    hashrate = pool_data.get("hashrate", 0) / 1e9  # GH/s
    reported_hashrate = pool_data.get("reportedHashrate", 0) / 1e9
    daily_est_kas = pool_data.get("estimatedRewards24h", 0)
    unpaid_balance = pool_data.get("balance", 0)
    worker_count = len(pool_data.get("workers", {}))
    last_update = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    income_usd, profit_usd = calc_profit(daily_est_kas, kas_price, daily_cost)

    # KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💰 Kaspa Price (USD)", f"${kas_price:.4f}")
    kpi2.metric("📈 Pool Hashrate (GH/s)", f"{hashrate:.2f}")
    kpi3.metric("⚙️ Active Workers", worker_count)
    kpi4.metric("💸 Unpaid Balance (KAS)", f"{unpaid_balance:.2f}")

    # Financials
    st.subheader("📊 Profitability (24h)")
    st.write(f"**Estimated Kaspa/day:** {daily_est_kas:.4f} KAS")
    st.write(f"**Income/day (USD):** ${income_usd:.2f}")
    st.write(f"**Cost/day (USD):** ${daily_cost:.2f}")
    st.write(f"**Profit/day (USD):** ${profit_usd:.2f}")

    if profit_usd > 0:
        st.success("✅ You're mining profitably!")
    else:
        st.warning("⚠️ Currently at a loss — consider cost optimization.")

    st.divider()
    st.caption(f"Last updated: {last_update} | Wallet: {WALLET} | Rig: {RIG_NAME}")

else:
    st.error("Could not fetch pool or price data. Check network or API limits.")

st.markdown("---")
st.caption("🧱 Mining Dashboard v1.0 • Built for Jay Reid (Vast4090) • Powered by Streamlit & WoolyPooly")
