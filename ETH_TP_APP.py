import streamlit as st
import requests

st.set_page_config(
    page_title="ETH TP APP",
    layout="centered"  # page moins large, centrée
)

st.title("ETH TP APP")

# Fonction pour récupérer le prix ETH via CoinGecko
def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['ethereum']['usd']
    except Exception as e:
        st.error(f"Erreur récupération prix ETH : {e}")
        return None

# Inputs utilisateur
pru = st.number_input("PRU ($) :", min_value=0.0, value=1500.0, step=10.0, format="%.2f")
tp_input = st.text_input("TP (paliers) :", value="100:25,150:50,200:25")

if st.button("Rafraîchir le prix d'ETH"):
    eth_price = get_eth_price()
else:
    eth_price = None

if eth_price is not None:
    st.markdown(f"💰 **Prix actuel de l'ETH : ${eth_price:.2f}**")
    st.markdown(f"🎯 **PRU : ${pru:.2f}**")

    # Traitement des paliers
    tp_list = []
    try:
        for i, tp in enumerate(tp_input.split(','), 1):
            perc, sell = tp.split(':')
            perc = float(perc)
            sell = float(sell)
            target_price = pru * (1 + perc/100)
            status = "En attente"
            status_color = "orange"

            if eth_price >= target_price:
                status = "Atteint"
                status_color = "green"

            tp_list.append((i, perc, sell, target_price, status, status_color))
    except Exception as e:
        st.error(f"Erreur dans le format des TP : {e}")

    # Affichage des paliers avec style
    for i, perc, sell, target_price, status, status_color in tp_list:
        st.markdown(f"""
        <div style="background-color:#1e1e1e; padding:10px; border-radius:5px; margin-bottom:8px; color:white;">
        <b style="color:#ff9900;">TP{i}</b> : +{perc}% → ${target_price:.2f} | Vendre {sell}% 
        <span style="color:{status_color}; font-weight:bold;">{status}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("Cliquez sur 'Rafraîchir le prix d'ETH' pour récupérer le prix actuel.")
