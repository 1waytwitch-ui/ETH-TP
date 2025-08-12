import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime

# --- Style CSS personnalisé ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .title {
        font-weight: bold;
        color: #8a2be2;
        font-size: 3rem;
        margin-bottom: 0;
    }
    .subtitle {
        color: #bbb;
        margin-top: 0;
        margin-bottom: 1rem;
    }
    .tp-box {
        background: #1a1e24;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        color: white !important;
    }
    .tp-level {
        color: #f0a500;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .status-reached {
        color: #32cd32;  /* vert */
        font-weight: bold;
    }
    .status-pending {
        color: #ffa500;  /* orange */
        font-weight: bold;
    }
    .price-current {
        color: #4dd0e1;
        font-weight: bold;
        font-size: 1.3rem;
    }
    .button-primary {
        background-color: #8a2be2;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-weight: bold;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title">ETH TP APP</h1>', unsafe_allow_html=True)

def get_eth_price():
    url_coingecko = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    try:
        response = requests.get(url_coingecko, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data['ethereum']['usd']
    except requests.RequestException as e:
        st.error(f"Erreur récupération prix ETH : {e}")
        return None

def get_eth_24h_data():
    url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=1&interval=hourly"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        prices = data['prices']  # Liste de [timestamp, prix]
        # Convertir en DataFrame pandas
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        # Convertir timestamp ms en datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except requests.RequestException as e:
        st.error(f"Erreur récupération graphique ETH : {e}")
        return None

def calculate_take_profits(pru, tp_settings):
    tp_levels = {}
    for i, (percent_gain, percent_sell) in enumerate(tp_settings, start=1):
        level_price = pru * (1 + percent_gain / 100)
        tp_levels[f"TP{i}"] = {
            "gain_pct": percent_gain,
            "sell_pct": percent_sell,
            "price_level": round(level_price, 2)
        }
    return tp_levels

def display_status(current_price, pru, tp_levels):
    st.markdown(f"<p class='price-current'>💰 Prix actuel de l'ETH : ${current_price}</p>", unsafe_allow_html=True)
    st.markdown(f"<p>🎯 PRU : ${pru}</p>", unsafe_allow_html=True)

    for tp_name, data in tp_levels.items():
        status = "✅ Atteint" if current_price >= data['price_level'] else "🔜 En attente"
        status_class = "status-reached" if current_price >= data['price_level'] else "status-pending"
        
        st.markdown(
            f"""
            <div class="tp-box">
                <span class="tp-level">{tp_name}</span>: +{data['gain_pct']}% → <strong>${data['price_level']}</strong> | Vendre {data['sell_pct']}%
                <span class="{status_class}">{status}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_eth_chart(df):
    if df is not None and not df.empty:
        chart = alt.Chart(df).mark_line(color="#8a2be2").encode(
            x=alt.X('timestamp:T', axis=alt.Axis(title='Heure')),
            y=alt.Y('price:Q', axis=alt.Axis(title='Prix USD')),
            tooltip=[alt.Tooltip('timestamp:T', title='Heure'), alt.Tooltip('price:Q', title='Prix USD')]
        ).properties(
            width=700,
            height=300,
            title="Graphique ETH sur les dernières 24h"
        )
        st.altair_chart(chart, use_container_width=True)

# Inputs
col1, col2 = st.columns([1,3])
with col1:
    pru = st.number_input("PRU ($) :", min_value=0.0, value=1500.0, step=1.0, format="%.2f")
with col2:
    tp_input = st.text_input("TP (paliers) :", value="100:25,150:50,200:25")

if st.button("Rafraîchir le prix d'ETH"):
    try:
        tp_settings = []
        for item in tp_input.split(','):
            gain, sell = map(float, item.strip().split(':'))
            tp_settings.append((gain, sell))
        
        current_price = get_eth_price()
        if current_price is None:
            st.error("Impossible de récupérer le prix de l'ETH.")
        else:
            tp_levels = calculate_take_profits(pru, tp_settings)
            display_status(current_price, pru, tp_levels)

            # Afficher graphique 24h ETH
            df_24h = get_eth_24h_data()
            display_eth_chart(df_24h)

    except Exception as e:
        st.error(f"Erreur dans les entrées : {e}")
