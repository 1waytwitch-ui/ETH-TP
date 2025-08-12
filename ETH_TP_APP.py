import streamlit as st
import requests
import time

# --- Cache manuel pour le prix ETH (15 min)
cache = {
    "price": None,
    "timestamp": 0
}

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

def calculate_tp_levels(pru, tp_settings):
    tp_levels = {}
    for i, (multiple, sell_pct) in enumerate(tp_settings, start=1):
        level_price = pru * multiple
        tp_levels[f"TP{i}"] = {
            "multiple": multiple,
            "sell_pct": sell_pct,
            "price_level": round(level_price, 2)
        }
    return tp_levels

def calculate_estimated_gains(bag, tp_levels, current_price):
    total_sold = 0.0
    total_value = 0.0
    for data in tp_levels.values():
        if current_price >= data["price_level"]:
            qty_to_sell = (bag * data["sell_pct"]) / 100
            total_sold += qty_to_sell
            total_value += qty_to_sell * data["price_level"]
    return round(total_value, 2), round(total_sold, 4)

# --- INTERFACE ---
st.markdown("<h1 style='color:#8a2be2;'>ETH TP APP</h1>", unsafe_allow_html=True)

# --- Inputs utilisateur
col1, col2, col3 = st.columns(3)
with col1:
    pru = st.number_input("🎯 PRU ($)", min_value=0.0, value=1500.0, step=1.0, format="%.2f")
with col2:
    tp_input = st.text_input("📈 TP (x:sell%)", value="2:25,2.5:50,3:25")
with col3:
    bag = st.number_input("👛 Quantité ETH détenue", min_value=0.0, value=1.0, step=0.1, format="%.4f")

# --- Action bouton
if st.button("🔁 Rafraîchir le prix d'ETH"):
    try:
        # Traitement des TP
        tp_settings = []
        for item in tp_input.split(','):
            multiple, sell = map(float, item.strip().split(':'))
            tp_settings.append((multiple, sell))

        current_price = get_eth_price()
        if current_price is None:
            st.error("Prix ETH indisponible.")
        else:
            st.success(f"💰 Prix actuel de l'ETH : **${current_price}**")
            st.markdown(f"🧮 PRU : **${pru}**")

            tp_levels = calculate_tp_levels(pru, tp_settings)

            # Affichage des TP
            for tp_name, data in tp_levels.items():
                status = "✅ Atteint" if current_price >= data['price_level'] else "⏳ En attente"
                color = "green" if status == "✅ Atteint" else "orange"
                st.markdown(f"""
                    <div style='
                        background-color:#1a1e24;
                        border-radius:10px;
                        padding:10px;
                        margin-bottom:10px;
                        color:white;
                        font-size:16px;
                    '>
                        <strong style='color:#f0a500;'>{tp_name}</strong> : x{data['multiple']} → 
                        <strong>${data['price_level']}</strong> | Vendre {data['sell_pct']}%
                        <span style='color:{color}; font-weight:bold;'> ({status})</span>
                    </div>
                """, unsafe_allow_html=True)

            # Estimation des gains
            total_value, total_sold = calculate_estimated_gains(bag, tp_levels, current_price)
            st.markdown("---")
            st.markdown(f"💵 **Gains estimés réalisés :** `${total_value}` pour `{total_sold} ETH` vendus.")
    except Exception as e:
        st.error(f"Erreur dans les entrées : {e}")

# --- Signature discrète ---
st.markdown("<div style='text-align:right; font-size:10px; color:#555;'>© 1way</div>", unsafe_allow_html=True)
