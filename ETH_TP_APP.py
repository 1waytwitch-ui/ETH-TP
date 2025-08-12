import streamlit as st
import requests
import time

# Cache manuel du prix ETH
cache = {
    "price": None,
    "timestamp": 0
}

def get_eth_price():
    # Cache 5 minutes
    now = time.time()
    if cache["price"] and now - cache["timestamp"] < 300:
        return cache["price"]
    
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        price = data['ethereum']['usd']
        
        # Mise à jour du cache
        cache["price"] = price
        cache["timestamp"] = now
        
        return price
    except requests.RequestException as e:
        st.error(f"Erreur récupération prix ETH : {e}")
        return None

st.title("ETH TP APP")

pru = st.number_input("PRU ($) :", min_value=0.0, value=1500.0, step=1.0, format="%.2f")
tp_input = st.text_input("TP (paliers) :", value="100:25,150:50,200:25")

if st.button("Rafraîchir le prix d'ETH"):
    tp_settings = []
    try:
        for item in tp_input.split(','):
            gain, sell = map(float, item.strip().split(':'))
            tp_settings.append((gain, sell))
    except:
        st.error("Format des paliers invalide. Utiliser gain:sell séparés par des virgules.")
        tp_settings = []
    
    if tp_settings:
        current_price = get_eth_price()
        if current_price is None:
            st.error("Impossible de récupérer le prix de l'ETH.")
        else:
            st.markdown(f"💰 Prix actuel de l'ETH : **${current_price}**")
            st.markdown(f"🎯 PRU : **${pru}**")

            for i, (gain, sell) in enumerate(tp_settings, 1):
                level_price = pru * (1 + gain / 100)
                status = "✅ Atteint" if current_price >= level_price else "🔜 En attente"
                st.markdown(f"TP{i} : +{gain}% → **${round(level_price, 2)}** | Vendre {sell}% → {status}")
