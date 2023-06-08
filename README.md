# Crypto Discord Bot


## This bot is written in Python and uses many modules including Discord, Matplotlib, Pandas, Pycoingecko API, and many more. Inspired by: <a href='https://github.com/ImKelp/Simple-Crypto-Dicord-Bot'>ImKelp/Simple-Crypto-Dicord-Bot</a>


## This project was made to provide usefulness to myself with up-to-date information about cryptocurrencies on Discord. This Python bot uses the pycoingecko API and retrieves and displays current data of the top 100 cryptocurrencies on Discord. Here are some key features this bot can do.


* Retrieves and displays data of current price, volume, market cap, and percentages of price changes.
* Shows a 7-day chart of the price, compares coin prices, and performs conversions between different coins. 
* Automatic real-time updates of the Ethereum price as the display status of the bot.
* Interactive commands for users to find what data they want to see.



## Commands

* **!help** - Explains what commands are used and an explanation of each command.
* **!about** - About this bot and what it does.
* **!list** -  Shows the top 100 valid cryptocurrencies.
* **!swap** - shows price conversion of a given price of a coin to another. Ex: "!swap 5.6 ethereum bitcoin"
* **!chart** - Displays current data and chart. Ex: "!chart Ethereum"
* **!candle** - Displays candlestick chart. Ex: "!candle Ethereum"

## Visual

![!chart](https://i.gyazo.com/f3730cdd54a38e216ba25c5ffce64185.png)
![!candle](https://i.gyazo.com/4e22eb94049ed017e774e8df6f569e20.png)
![!swap](https://i.gyazo.com/36d7a39e390359bee26a71919c413dbe.png)
![!list](https://i.gyazo.com/2ed3dd94fc755217704a2400291d2491.png)

## Issues

Spamming commands could lead to Pycoingecko API freezing the bot. There is no current fix, but short-term reset the bot and reload after a couple of minutes. 

If any other known bugs, or improvements I could adjust please feel free to submit them in the issue tab.
