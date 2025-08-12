import streamlit as st
import requests

# --- Style CSS personnalisé ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .title {
        font-weight: bold;
        color: #8a2be2;
        font-size: 3rem;
        margin-bottom: 0;
    }
    .tp-box {
        background: #1a1e24;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        color: white !important;
    }
    .tp-level {
        color: #f0a500;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .status-reached {
        color: #32cd32;
        font-weight: bold;
    }
    .status-pending {
        color: #ffa500;
        font-weight: bold;
    }
    .price-current {
        color: #4dd0e1;
        font-weight: bold;
        font-size: 1.3rem;
    }
    .button-primary {
        background-color: #8a2be2;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-weight: bold;
        font-size: 1.1rem;
    }
    footer {
        font-size: 0.8rem;
        color: #555;
        text-align: center;
        margin-top: 20px;
        user-select: none;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="title">ETH TP APP</h1>', unsafe_allow_html=True)

def get_eth_price():
    url = "https://api.coincap.io/v2/assets/ethereum"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        price = float(data['data']['priceUsd'])
        return round(price, 2)
    except Exception as e:
        st.error(f"Erreur récupération prix ETH : {e}")
        return None

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

def display_status(current_price, pru, tp_levels):
    st.markdown(f"<p class='price-current'>💰 Prix actuel de l'ETH : ${current_price}</p>", unsafe_allow_html=True)
    st.markdown(f"<p>🎯 PRU : ${pru}</p>", unsafe_allow_html=True)

    for tp_name, data in tp_levels.items():
        status = "✅ Atteint" if current_price >= data['price_level'] else "🔜 En attente"
        status_class = "status-reached" if current_price >= data['price_level'] else "status-pending"
        st.markdown(f"""
            <div class="tp-box">
                <span class="tp-level">{tp_name}</span>: +{data['gain_pct']}% → <strong>${data['price_level']}</strong> | Vendre {data['sell_pct']}%
                <span class="{status_class}">{status}</span>
            </div>
        """, unsafe_allow_html=True)

# Inputs
pru = st.number_input("PRU ($) :", min_value=0.0, value=1500.0, step=1.0, format="%.2f")
tp_input = st.text_input("TP (paliers) :", value="100:25,150:50,200:25")

if st.button("Rafraîchir le prix d'ETH"):
    try:
        tp_settings = []
        for item in tp_input.split(','):
            gain, sell = map(float, item.strip().split(':'))
            tp_settings.append((gain, sell))
        
        current_price = get_eth_price()
        if current_price is None:
            st.error("Impossible de récupérer le prix de l'ETH.")
        else:
            tp_levels = calculate_take_profits(pru, tp_settings)
            display_status(current_price, pru, tp_levels)
    except Exception as e:
        st.error(f"Erreur dans les entrées : {e}")

st.markdown('<footer>© 1way</footer>', unsafe_allow_html=True)
