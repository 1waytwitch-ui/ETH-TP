import streamlit as st
import requests
import time

# Cache manuel (dictionnaire)
cache = {
    "price": None,
    "timestamp": 0
}

# Fonction de récupération du prix ETH avec mise en cache (15 min = 900 s)
def get_eth_price():
    now = time.time()
    if cache["price"] is not None and (now - cache["timestamp"] < 900):
        return cache["price"]

    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        price = float(data['ethereum']['usd'])
        
        cache["price"] = round(price, 2)
        cache["timestamp"] = now
        return cache["price"]
    except requests.RequestException as e:
        st.error(f"Erreur récupération prix ETH : {e}")
        return None

# Fonction pour calculer les niveaux de take profit
def calculate_take_profits(pru, tp_settings):
    tp_levels = {}
    for i, (gain_pct, sell_pct) in enumerate(tp_settings, start=1):
        level_price = pru * (1 + gain_pct / 100)
        tp_levels[f"TP{i}"] = {
            "gain_pct": gain_pct,
            "sell_pct": sell_pct,
            "price_level": round(level_price, 2)
        }
    return tp_levels

# --- Interface Streamlit ---
st.markdown("<h1 style='color:#8a2be2;'>ETH TP APP</h1>", unsafe_allow_html=True)

# Entrées utilisateur
pru = st.number_input("💼 PRU (Prix d'achat unitaire en $) :", min_value=0.0, value=1500.0, step=1.0, format="%.2f")
tp_input = st.text_input("🎯 TP (paliers au format gain:sell%) :", value="20:25,40:50,60:25")

if st.button("🔁 Rafraîchir le prix d'ETH"):
    try:
        # Conversion des paliers texte en liste de tuples
        tp_settings = []
        for item in tp_input.split(','):
            gain, sell = map(float, item.strip().split(':'))
            tp_settings.append((gain, sell))

        # Récupération prix ETH depuis CoinGecko (avec cache)
        current_price = get_eth_price()
        if current_price is None:
            st.error("Prix ETH indisponible.")
        else:
            st.success(f"💰 Prix actuel de l'ETH : **${current_price}**")
            st.markdown(f"🧮 Votre PRU : **${pru}**")

            tp_levels = calculate_take_profits(pru, tp_settings)

            # Affichage des niveaux de TP
            for tp_name, data in tp_levels.items():
                status = "✅ Atteint" if current_price >= data['price_level'] else "⏳ En attente"
                color = "green" if current_price >= data['price_level'] else "orange"
                st.markdown(f"""
                    <div style='
                        background-color:#1a1e24;
                        border-radius:10px;
                        padding:10px;
                        margin-bottom:10px;
                        color:white;
                        font-size:16px;
                    '>
                    <strong style='color:#f0a500;'>{tp_name}</strong> : +{data['gain_pct']}% → 
                    <strong>${data['price_level']}</strong> | Vendre {data['sell_pct']}% 
                    <span style='color:{color}; font-weight:bold;'>({status})</span>
                    </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erreur dans les entrées : {e}")

# Signature discrète
st.markdown("<div style='text-align:right; font-size:10px; color:#555;'>© 1way</div>", unsafe_allow_html=True)
