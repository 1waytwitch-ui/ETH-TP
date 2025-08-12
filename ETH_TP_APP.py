import streamlit as st
import requests

def get_eth_price():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd")
        data = response.json()
        return data['ethereum']['usd']
    except Exception:
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

st.title("ETH TP APP")

pru = st.number_input("PRU ($) :", value=1500.0, step=1.0)

tp_input = st.text_input("TP (paliers) :", value="100:25,150:50,200:25")

if st.button("Rafraîchir le prix d'ETH"):
    try:
        tp_settings = []
        for item in tp_input.split(','):
            gain, sell = map(float, item.strip().split(':'))
            tp_settings.append((gain, sell))
        
        tp_levels = calculate_take_profits(pru, tp_settings)
        current_price = get_eth_price()
        
        if current_price is None:
            st.error("Erreur récupération prix ETH.")
        else:
            st.markdown("---")
            st.write(f"💰 **Prix actuel de l'ETH** : {current_price} USD")
            st.write(f"🎯 **PRU** : {pru} USD")
            st.write("📊 **Paliers de Take Profit :**")
            for tp_name, data in tp_levels.items():
                status = "✅ Atteint" if current_price >= data['price_level'] else "🔜 En attente"
                st.write(f"- {tp_name}: +{data['gain_pct']}% → {data['price_level']} USD | Vendre {data['sell_pct']}% ({status})")
            st.markdown("---")
    except Exception as e:
        st.error(f"Erreur dans les entrées : {e}")
