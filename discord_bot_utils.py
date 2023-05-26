from pycoingecko import CoinGeckoAPI
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

cg = CoinGeckoAPI()

def get_eth_price():
    eth_data = cg.get_price(ids='ethereum', vs_currencies='usd')
    return eth_data['ethereum']['usd']

# Convert unix time to a more readable time
def unix_to_date(unix_time):
    timestamp = datetime.fromtimestamp((unix_time/1000))
    return f"{timestamp.strftime('%d-%m-%Y %H:%M:%S')}"


def get_graph(token):

    # coin_graph gives list of [unix timestamp, price]
    coin_graph = cg.get_coin_market_chart_by_id(id=f'{token}', vs_currency='usd', days='7')

    new_data = {}
    for each in coin_graph['prices']:
        date = unix_to_date(each[0])
        new_data[date] = each[1]
        
    # sets dictionary dates and prices into df.
    df = pd.DataFrame({'Dates': new_data.keys(), 'Prices': new_data.values()})
    
    df.plot(x='Dates', y='Prices', kind='line', legend=None, color="black", xlabel="Date", ylabel="Price")	
    plt.title(f'Last 7 days of {token}', fontsize=14, color='black', fontweight='bold')

    plt.xticks([])
    
    # Sets chart into 'filename' and used later
    filename = r"D:\CS\Python\projects\discord_bot\img\chart.png"
    plt.savefig(filename)

    plt.close()