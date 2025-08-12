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

# --- CSS global pour compatibilité light/dark ---
st.markdown("""
    <style>
        .tp-box {
            background-color: #f5f5f5;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 10px;
            color: #222;
            font-size: 16px;
            border: 1px solid #ddd;
        }
        .tp-title {
            color: #d97706;
            font-weight: bold;
        }
        .tp-status-green {
            color: #22c55e;
            font-weight: bold;
        }
        .tp-status-orange {
            color: #f97316;
            font-weight: bold;
        }
        .gains-box {
            font-size: 18px;
            background-color: #f0f9ff;
            border-left: 4px solid #0ea5e9;
            padding: 10px;
            margin-top: 20px;
            color: #111;
        }
        .gains-amount {
            color: #15803d;
            font-weight: bold;
        }
        .signature {
            text-align: right;
            font-size: 10px;
            color: #888;
            margin-top: 50px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Titre ---
st.markdown("<h1 style='color:#4f46e5;'>ETH TP APP</h1>", unsafe_allow_html=True)

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
                reached = current_price >= data['price_level']
                status = "✅ Atteint" if reached else "⏳ En attente"
                status_class = "tp-status-green" if reached else "tp-status-orange"

                st.markdown(f"""
                    <div class="tp-box">
                        <span class="tp-title">{tp_name}</span> : x{data['multiple']} → 
                        <strong>${data['price_level']}</strong> | Vendre {data['sell_pct']}%
                        <span class="{status_class}">({status})</span>
                    </div>
                """, unsafe_allow_html=True)

            # Estimation des gains
            total_value, total_sold = calculate_estimated_gains(bag, tp_levels, current_price)
            if total_sold > 0:
                st.markdown(f"""
                    <div class="gains-box">
                        💵 Gains estimés réalisés : 
                        <span class="gains-amount">${total_value}</span> pour 
                        <span class="gains-amount">{total_sold} ETH</span> vendus.
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Aucun palier atteint pour le moment.")

    except Exception as e:
        st.error(f"Erreur dans les entrées : {e}")

# --- Signature discrète ---
st.markdown("<div class='signature'>© 1way</div>", unsafe_allow_html=True)

# --- Suivi manuel de la performance du portefeuille ---
st.markdown("---")
st.markdown("## 📊 Suivi de la performance du portefeuille")

col1, col2 = st.columns(2)
with col1:
    montant_investi = st.number_input("💵 Montant investi initial ($)", min_value=0.0, value=1000.0, step=100.0, format="%.2f")
with col2:
    valeur_actuelle = st.number_input("📈 Valeur actuelle du portefeuille ($)", min_value=0.0, value=1500.0, step=100.0, format="%.2f")

if montant_investi > 0:
    profit_loss = valeur_actuelle - montant_investi
    rendement_pct = (profit_loss / montant_investi) * 100

    color = "#32cd32" if profit_loss >= 0 else "#ffa500"  # vert ou orange
    emoji = "📈" if profit_loss >= 0 else "📉"

    st.markdown(f"""
        <div style="
            background-color: #1a1e24;
            border-radius: 12px;
            padding: 15px;
            margin-top: 10px;
            color: white;
            font-size: 16px;
        ">
            <p>{emoji} <strong>Valeur actuelle :</strong> <span style="color:#4dd0e1;">${valeur_actuelle:,.2f}</span></p>
            <p>💵 <strong>Investi initialement :</strong> ${montant_investi:,.2f}</p>
            <p>📊 <strong>Rendement :</strong> <span style="color:{color}; font-weight:bold;">{rendement_pct:.2f}%</span></p>
            <p>💰 <strong>Gains/Pertes :</strong> <span style="color:{color}; font-weight:bold;">${profit_loss:,.2f}</span></p>
        </div>
    """, unsafe_allow_html=True)


