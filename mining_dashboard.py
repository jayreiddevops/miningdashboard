import streamlit as st
import requests
import sqlite3
from datetime import datetime

# ------------------------
# CONFIG
# ------------------------
API_URL = "https://woolypooly.com/en/api/coin/kas/wallet/"
WALLET_ADDRESS = "kaspa:qrn6q4hywx4z9j4hmdp6vt4ec3a7w80akde3j26cpanz3crn89wq6rr6n2j7s"
RIG_NAME = "vast4090"

# ------------------------
# DB SETUP
# ------------------------
conn = sqlite3.connect("costs.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS costs (
    date TEXT,
    rig TEXT,
    coin TEXT,
    cost_usd REAL
)""")
conn.commit()

# ------------------------
# FUNCTIONS
# ------------------------
def fetch_woolypooly_data(wallet):
    """Fetch miner stats from WoolyPooly API"""
    try:
        r = requests.get(API_URL + wallet)
        data = r.json()
        worker = data["workers"][0]
        hashrate = worker["hashrate"]
        balance = data["balance"]
        price_usd = data["price_usd"]
        revenue_24h = hashrate * 24 * 0.00000000001 * 0.053  # rough est
        return {
            "hashrate": round(hashrate / 1e9, 2),
            "balance": balance,
            "price_usd": price_usd,
            "revenue_24h": round(revenue_24h, 4),
        }
    except Exception as e:
        st.error(f"⚠️ Error fetching data: {e}")
        return None

def save_cost(rig, coin, cost_usd):
    c.execute("INSERT INTO costs VALUES (?, ?, ?, ?)", (datetime.now().date(), rig, coin, cost_usd))
    conn.commit()

def get_latest_cost(rig):
    c.execute("SELECT cost_usd FROM costs WHERE rig=? ORDER BY date DESC LIMIT 1", (rig,))
    row = c.fetchone()
    return row[0] if row else 0.0

# ------------------------
# STREAMLIT UI
# ------------------------
st.set_page_config(page_title="Vast Mining Dashboard", page_icon="💎", layout="centered")

st.title("💎 Vast Mining Dashboard")
st.subheader(f"Rig: {RIG_NAME} | Coin: Kaspa")

data = fetch_woolypooly_data(WALLET_ADDRESS)

if data:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💠 Hashrate (GH/s)", data["hashrate"])
        st.metric("💰 24h Revenue (USD est.)", f"${data['revenue_24h']}")
    with col2:
        st.metric("🪙 Wallet Balance", f"{data['balance']} KAS")
        st.metric("💵 KAS Price", f"${data['price_usd']}")

    st.divider()
    st.write("### ⚙️ Enter Daily Cost")
    cost_input = st.number_input("Daily cost in USD", value=get_latest_cost(RIG_NAME), step=0.1)
    if st.button("💾 Save Cost"):
        save_cost(RIG_NAME, "Kaspa", cost_input)
        st.success("Cost saved!")

    st.divider()
    profit = round(data["revenue_24h"] - cost_input, 2)
    profit_gbp = round(profit * 0.79, 2)
    st.write("### 📈 Profit/Loss Summary")
    col3, col4 = st.columns(2)
    with col3:
        st.metric("Net Profit (USD)", f"${profit}")
    with col4:
        st.metric("Net Profit (GBP)", f"£{profit_gbp}")

    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

else:
    st.warning("No data received from WoolyPooly. Check API or wallet address.")

