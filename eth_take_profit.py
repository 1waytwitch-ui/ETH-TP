import requests
import ipywidgets as widgets
from IPython.display import display, clear_output

def get_eth_price():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd")
        data = response.json()
        return data['ethereum']['usd']
    except Exception as e:
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

def display_status(current_price, pru, tp_levels, output):
    with output:
        clear_output()
        print("="*40)
        print("📊 Paliers de Take Profit :")
        for tp_name, data in tp_levels.items():
            status = "✅ Atteint" if current_price >= data['price_level'] else "🔜 En attente"
            print(f" - {tp_name}: +{data['gain_pct']}% → {data['price_level']} USD | Vendre {data['sell_pct']}% ({status})")
        print(f"\n💰 Prix actuel de l'ETH : {current_price} USD")
        print(f"🎯 PRU : {pru} USD")
        print("="*40)

def on_button_click(b):
    try:
        pru = float(pru_text.value)
        tp_input = tp_text.value
        tp_settings = []
        for item in tp_input.split(','):
            gain, sell = map(float, item.strip().split(':'))
            tp_settings.append((gain, sell))
        tp_levels = calculate_take_profits(pru, tp_settings)
        current_price = get_eth_price()
        if current_price is None:
            with output:
                clear_output()
                print("Erreur récupération prix ETH.")
        else:
            display_status(current_price, pru, tp_levels, output)
    except Exception as e:
        with output:
            clear_output()
            print(f"Erreur dans les entrées : {e}")

# Widgets pour l'input
pru_text = widgets.Text(value='1500', description='PRU ($) :')
tp_text = widgets.Text(value='100:25,150:50,200:25', description='TP (paliers) :')
refresh_button = widgets.Button(description="Rafraîchir le prix d'ETH")

output = widgets.Output()

refresh_button.on_click(on_button_click)

display(pru_text, tp_text, refresh_button, output)