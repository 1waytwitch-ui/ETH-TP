import streamlit as st
import requests
from datetime import datetime, timedelta

# --- Mise en cache pendant 15 minutes pour limiter les appels à l'API ---
@st.cache_data(ttl=900)
def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()['ethereum']['usd']
    except Exception as e:
        st.error(f"Erreur récupération prix ETH : {e}")
        return None

# --- Calcul des TP (Take Profit) ---
def calculate_tp_levels(pru, multipliers, sell_percentages):
    return [
        {
            "label": f"x{multiplier}",
            "target_price": round(pru * multiplier, 2),
            "sell_pct": sell_pct
        }
        for multiplier, sell_pct in zip(multipliers, sell_percentages)
    ]

# --- Affichage des TP ---
def display_tp_status(current_price, tp_levels, pru):
    st.markdown(f"<p class='price-current'>💰 Prix actuel de l'ETH : <strong>${current_price}</strong></p>", unsafe_allow_html=True)
    st.markdown(f"<p>🎯 PRU : <strong>${pru}</strong></p>", unsafe_allow_html=True)
    gains_total = 0
    total_eth_sold = 0
    for tp in tp_levels:
        status = "✅ Atteint" if current_price >= tp["target_price"] else "🔜 En attente"
        status_class = "status-reached" if current_price >= tp["target_price"] else "status-pending"

        if current_price >= tp["target_price"]:
            # Simuler un portefeuille de 1 ETH pour calcul des gains
            eth_sold = tp["sell_pct"] / 100
            gain = tp["target_price"] * eth_sold
            gains_total += gain
            total_eth_sold += eth_sold

        st.markdown(
            f"""
            <div class="tp-box">
                <span class="tp-level">{tp["label"]}</span> → <strong>${tp["target_price"]}</strong> | Vendre {tp["sell_pct"]}% 
                <span class="{status_class}">{status}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- Affichage des gains ---
    if gains_total > 0:
        st.markdown(
            f"""
            <div class="gains-box">
                💵 <span class="gains-title">Gains estimés réalisés :</span>
                <span class="gains-amount">${gains_total:,.1f}</span> pour 
                <span class="gains-eth">{total_eth_sold:.2f} ETH</span> vendus.
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Style CSS ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: white;
    }
    .title {
        font-weight: bold;
        color: #8a2be2;
        font-size: 3rem;
    }
    .tp-box {
        background: #1a1e24;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .tp-level {
        color: #f0a500;
        font-weight: bold;
    }
    .status-reached {
        color: #32cd32;
        font-weight: bold;
        margin-left: 10px;
    }
    .status-pending {
        color: #ffa500;
        font-weight: bold;
        margin-left: 10px;
    }
    .price-current {
        font-size: 1.4rem;
        color: #4dd0e1;
    }
    .gains-box {
        font-size: 1.3rem;
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 12px;
        margin-top: 25px;
    }
    .gains-title {
        font-weight: bold;
    }
    .gains-amount {
        color: #90ee90;
        font-weight: bold;
        padding: 0 5px;
    }
    .gains-eth {
        color: #00bcd4;
        font-weight: bold;
        padding-left: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Titre ---
st.markdown('<h1 class="title">ETH TP APP</h1>', unsafe_allow_html=True)

# --- Inputs ---
col1, col2 = st.columns(2)
with col1:
    pru = st.number_input("PRU ($)", value=1500.0, step=10.0, min_value=0.0)
with col2:
    st.markdown("Multiplicateurs : x2, x2.5, x3 — Ventes : 25%, 50%, 25%")

if st.button("Rafraîchir le prix d'ETH"):
    current_price = get_eth_price()
    if current_price:
        tp_levels = calculate_tp_levels(
            pru,
            multipliers=[2, 2.5, 3],
            sell_percentages=[25, 50, 25]
        )
        display_tp_status(current_price, tp_levels, pru)
    else:
        st.error("Impossible de récupérer le prix actuel de l'ETH.")

# --- Signature discrète ---
st.markdown("<br><p style='text-align: center; color: grey; font-size: 0.8rem;'>© 1way</p>", unsafe_allow_html=True)
