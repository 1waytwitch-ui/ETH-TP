import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="ETH TP APP", layout="wide")

st.title("ETH TP APP")

# Inputs Streamlit
pru = st.number_input("PRU ($) :", min_value=0.0, value=1500.0, step=1.0, format="%.2f")
tp_input = st.text_input("TP (paliers) :", "100:25,150:50,200:25")
refresh = st.button("Rafraîchir le prix d'ETH")

# Fonction pour récupérer le prix ETH actuel avec User-Agent (CoinCap)
def get_eth_price():
    url = "https://api.coincap.io/v2/assets/ethereum"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data['data']['priceUsd'])
    except Exception as e:
        st.error(f"Erreur récupération prix ETH : {e}")
        return None

# Fonction pour récupérer les données ETH 24h via CoinCap (hourly)
def get_eth_24h_data_coincap():
    url = "https://api.coincap.io/v2/assets/ethereum/history?interval=h1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        prices = data['data']
        df = pd.DataFrame(prices)
        df['timestamp'] = pd.to_datetime(df['time'], unit='ms')
        df['price'] = df['priceUsd'].astype(float)
        return df[['timestamp', 'price']]
    except Exception as e:
        st.error(f"Erreur récupération graphique ETH CoinCap : {e}")
        return None

# Calcul des niveaux TP
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

# Parse input TP
def parse_tp_input(tp_input):
    tp_settings = []
    try:
        for item in tp_input.split(','):
            gain, sell = map(float, item.strip().split(':'))
            tp_settings.append((gain, sell))
    except Exception:
        st.error("Format des paliers TP incorrect. Format attendu ex: 100:25,150:50")
    return tp_settings

# Affichage TP avec couleurs et texte blanc
def display_take_profits(current_price, pru, tp_levels):
    for tp_name, data in tp_levels.items():
        status = ""
        status_color = ""
        if current_price >= data['price_level']:
            status = "✅ Atteint"
            status_color = "green"
        else:
            status = "🔜 En attente"
            status_color = "orange"
        st.markdown(
            f"<div style='background-color:#111; color:white; padding:10px; margin-bottom:8px; border-radius:6px;'>"
            f"<b style='color:#ff9900'>{tp_name}</b> : +{data['gain_pct']}% → ${data['price_level']} | Vendre {data['sell_pct']}% | "
            f"<span style='color:{status_color}'>{status}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
        
# Exécution principale
if refresh:
    tp_settings = parse_tp_input(tp_input)
    tp_levels = calculate_take_profits(pru, tp_settings)

    current_price = get_eth_price()
    if current_price:
        st.markdown(f"💰 **Prix actuel de l'ETH :** ${current_price:.2f}")
        st.markdown(f"🎯 **PRU :** ${pru:.2f}")

        display_take_profits(current_price, pru, tp_levels)

        # Affichage graphique
        df = get_eth_24h_data_coincap()
        if df is not None and not df.empty:
            fig = px.line(df, x='timestamp', y='price',
                          title='Graphique ETH prix dernières 24h',
                          labels={'timestamp': 'Temps', 'price': 'Prix USD'})
            fig.update_layout(plot_bgcolor='#111', paper_bgcolor='#111', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Impossible de récupérer le prix actuel de l'ETH.")

else:
    st.info("Cliquez sur 'Rafraîchir le prix d'ETH' pour démarrer.")
