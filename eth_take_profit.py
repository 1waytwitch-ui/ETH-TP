import streamlit as st
import requests

# --------------------------
# 🔧 Fonctions principales
# --------------------------

def get_eth_price():
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        )
        data = response.json()
        return data['ethereum']['usd']
    except:
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

# --------------------------
# 🌐 Interface Streamlit
# --------------------------

st.set_page_config(page_title="ETH TP APP", layout="centered")
st.title("📈 ETH TP APP")

st.markdown("Suivi des take profits sur Ethereum.")

# 📥 Inputs utilisateur
pru = st.number_input("🎯 PRU (Prix d'achat ETH)", min_value=0.0, value=1500.0, step=10.0)
tp_input = st.text_input("📊 TP (paliers, ex: 10:25,20:50)", value="10:25,20:50,30:25")

# Bouton d'action
if st.button("🔍 Vérifier les TP"):

    # Parsing des entrées
    try:
        tp_settings = []
        for item in tp_input.split(','):
            gain, sell = map(float, item.strip().split(':'))
            tp_settings.append((gain, sell))

        current_price = get_eth_price()
        if current_price is None:
            st.error("Erreur : impossible de récupérer le prix ETH.")
        else:
            tp_levels = calculate_take_profits(pru, tp_settings)

            st.success(f"💰 Prix actuel ETH : {current_price} USD")
            st.write(f"🎯 PRU saisi : {pru} USD")
            st.markdown("---")
            st.markdown("### 📋 Résultats des paliers :")

            for tp_name, data in tp_levels.items():
                status = "✅ **Atteint**" if current_price >= data['price_level'] else "🔜 En attente"
                st.markdown(
                    f"- **{tp_name}** : +{data['gain_pct']}% → `{data['price_level']} USD` | "
                    f"Vente {data['sell_pct']}% — {status}"
                )

    except Exception as e:
        st.error(f"Erreur dans le format TP : {e}")
