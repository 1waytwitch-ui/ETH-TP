import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ETH TP APP", layout="centered")

# Cache la récupération du prix ETH 5 minutes (300 secondes)
@st.cache_data(ttl=300)
def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["ethereum"]["usd"]

# Cache récupération graphique ETH (1h intervalle sur 24h)
@st.cache_data(ttl=300)
def get_eth_chart():
    url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=1&interval=hourly"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# Style CSS pour les TP
st.markdown("""
<style>
.tp-container {
    background-color: #121212;
    color: white;
    padding: 10px;
    margin: 10px 0;
    border-radius: 8px;
}
.tp-title {
    font-weight: bold;
    color: orange;
}
.tp-attente {
    color: orange;
    font-weight: bold;
}
.tp-atteint {
    color: #7AC74F;
    font-weight: bold;
}
.footer {
    font-size: 12px;
    color: #555;
    text-align: center;
    margin-top: 50px;
}
</style>
""", unsafe_allow_html=True)

st.title("ETH TP APP")

pru = st.number_input("PRU ($) :", value=1500.0, step=1.0, format="%.2f")
tp_input = st.text_input("TP (paliers) :", value="100:25,150:50,200:25")

# Bouton pour récupérer le prix ETH (pas à chaque modif)
if st.button("Rafraîchir le prix d'ETH"):
    try:
        eth_price = get_eth_price()
        st.success(f"💰 Prix actuel de l'ETH : ${eth_price:.2f}")
    except Exception as e:
        st.error(f"Erreur récupération prix ETH : {e}")
else:
    eth_price = None
    st.info("Cliquez sur 'Rafraîchir le prix d'ETH' pour récupérer le prix actuel.")

# Affichage graphique ETH si on a le prix (et donc les données)
if eth_price is not None:
    try:
        df = get_eth_chart()
        fig = px.line(df, x="timestamp", y="price", title="Cours ETH dernières 24h", labels={"timestamp": "Date", "price": "Prix (USD)"})
        fig.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur récupération graphique ETH : {e}")

# Affichage des TP (simple)
if tp_input:
    try:
        tp_list = tp_input.split(",")
        st.write(f"🎯 PRU : ${pru}")
        for i, tp in enumerate(tp_list, start=1):
            pct, sell = map(float, tp.split(":"))
            target_price = pru * (1 + pct/100)
            # Simplifions en supposant que si eth_price >= target_price alors "Atteint"
            status = "Atteint" if eth_price and eth_price >= target_price else "En attente"
            status_color = "tp-atteint" if status == "Atteint" else "tp-attente"

            st.markdown(f"""
            <div class="tp-container">
                <span class="tp-title">TP{i}</span> +{pct:.1f}% → ${target_price:.2f} | Vendre {sell:.1f}% 
                <span class="{status_color}"> {status}</span>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur format TP : {e}")

# Footer discret
st.markdown('<div class="footer">1way</div>', unsafe_allow_html=True)
