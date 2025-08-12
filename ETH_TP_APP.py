import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ETH TP APP", page_icon="🦄", layout="centered")

st.title("ETH TP APP")

# Inputs utilisateur
pru = st.number_input("PRU ($) :", value=1500.0, step=1.0, format="%.2f")
tp_input = st.text_input("TP (paliers) :", value="100:25,150:50,200:25")

def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        price = response.json()["ethereum"]["usd"]
        return price
    except Exception as e:
        st.error(f"Erreur récupération prix ETH : {e}")
        return None

def get_eth_chart():
    url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=1&interval=hourly"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Erreur récupération graphique ETH : {e}")
        return None

if st.button("Rafraîchir le prix d'ETH"):
    eth_price = get_eth_price()
    if eth_price:
        st.markdown(f"💰 **Prix actuel de l'ETH : ${eth_price:.2f}**")

        # Affichage graphique
        df_chart = get_eth_chart()
        if df_chart is not None:
            fig = px.line(df_chart, x='timestamp', y='price', title='Graphique ETH sur 24h')
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)

        # Affichage paliers TP
        tp_list = []
        for i, palier in enumerate(tp_input.split(','), 1):
            try:
                perc_str, sell_str = palier.split(':')
                perc = float(perc_str)
                sell = float(sell_str)
                tp_price = pru * (1 + perc/100)
                statut = "En attente"
                color = "orange"
                # Ici tu peux ajouter la logique pour modifier le statut
                st.markdown(f"""
                <div style="background-color:#121212; padding:10px; border-radius:5px; margin-top:5px; color:white;">
                <b style="color:#FFA500;">TP{i}</b> +{perc:.1f}% → ${tp_price:.2f} | Vendre {sell:.1f}% | <span style="color:{color}; font-weight:bold;">{statut}</span>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                pass
    else:
        st.error("Impossible de récupérer le prix actuel de l'ETH.")

# Footer discret
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 5px;
        width: 100%;
        text-align: center;
        color: rgba(153, 153, 153, 0.4);
        font-size: 10px;
        pointer-events: none;
        user-select: none;
        font-family: monospace;
    }
    </style>
    <div class="footer">
        © 2025 1way
    </div>
    """,
    unsafe_allow_html=True,
)
