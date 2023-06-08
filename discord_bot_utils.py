from pycoingecko import CoinGeckoAPI
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import mplfinance as mpf

cg = CoinGeckoAPI()

def get_eth_price():
    eth_data = cg.get_price(ids='ethereum', vs_currencies='usd')
    return eth_data['ethereum']['usd']


def get_graph(token, coin_percentage):

    # coin_graph gives list of [unix timestamp, price]
    coin_graph = cg.get_coin_market_chart_by_id(id=f'{token}', vs_currency='usd', days='7')

    df = pd.DataFrame(coin_graph['prices'])
    df.columns = ['Date', 'Price']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')

    color = None
    if coin_percentage >= 0:
        color = 'green'
    else:
        color = 'red'

    # sets dictionary dates and prices into df.
    # df = pd.DataFrame({'Dates': new_data.keys(), 'Prices': new_data.values()})
    df.plot(x='Date',
            y='Price',
            kind='line',
            legend=None,
            color=f'{color}',
            xlabel='Date',
            ylabel='Price')	
    
    plt.title(f'Last 7 days of {token}', fontsize=14, color='black', fontweight='bold')

    # plt.xticks([])
    
    # Sets chart into 'filename' and used later
    filename = r'D:\CS\Python\projects\Crypto-Discord-Bot\img\chart.png'
    plt.savefig(filename)

    plt.close()

def get_candle(token):
    coin_ohlc = cg.get_coin_ohlc_by_id(id=token, vs_currency='usd', days='7')

    df = pd.DataFrame(coin_ohlc)
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')  # Convert to datetime
    df = df.set_index('Date')


    mpf.plot(df,
            type='candle',
            mav=(3,6),
            style='yahoo',
            tight_layout=True,
            savefig='img\candle.png')
