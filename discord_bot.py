import discord
import requests
import json
import os
from dotenv import load_dotenv
import asyncio
from pycoingecko import CoinGeckoAPI
from discord_bot_utils import get_eth_price, get_graph


# pycoingecko startup
cg = CoinGeckoAPI()

# Checks coin gecko server status
response = requests.get('https://api.coingecko.com/api/v3/ping')
ping = json.loads(response.text)
ping_status = ping['gecko_says']
print(f'CoinGeckoAPI server status: {ping_status}')

# Discord startup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


async def update_eth_price():
    await client.wait_until_ready()
    while not client.is_closed():
        eth_price = get_eth_price()
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Ethereum: ${eth_price:.2f}"))
        await asyncio.sleep(60)  # Updates every minute
    

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(update_eth_price())



@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!help'):
        await message.channel.send(
'''!chart "coin_name" shows current price and more about that coin.
!list shows the top 10 coins.
!swap "# coin1_name coin2_name shows the price conversion between the two coins''')

    if message.content.startswith('!about'):
        await message.channel.send('''
GOCrypto is a discord bot that shows current data of the top 10 cryptocurrecny.
Use !help for help with commands.''')

    # Makes a list of the top 10 coins and shows commands to check
    if message.content.startswith('!list'):
        crypto_list = cg.get_coins_markets(vs_currency='usd', per_page=10)
        count = 1

        embed=discord.Embed(title='List of Valid Coins Names', color=discord.Colour.og_blurple())

        embed.set_author(name=f'{client.user.name}', icon_url=client.user.avatar)

        embed.set_thumbnail(url='https://play-lh.googleusercontent.com/CcboHyK1Id9XQWa8HXb_81Rvgqy7J816OHiTcGlezcwC-tx4cnrrXPx1x6cR0PowqA')

        for coin in crypto_list:
            coin_id = coin['id']
            coin_name = coin['name']
            coin_symbol = coin['symbol'].upper()

            embed.add_field(name=f'{count}. {coin_name} - ${coin_symbol}', value=f'!chart {coin_id}', inline=False)
            
            count = count + 1

        embed.set_footer(text=f'{client.user.name} data by CoinGecko')

        await message.channel.send(embed=embed)

    if message.content.startswith('!swap'):

        # Checks if command is correctly formated
        try:
            _, coin1_amount, coin1, coin2 = message.content.split(' ', 3)
            coin1_amount = float(coin1_amount)
            coin1 = coin1.lower()
            coin2 = coin2.lower()

        except:
            await message.channel.send('Use "!swap # coin1_name coin2_name" for this command')

        crypto_list = cg.get_coins_markets(vs_currency='usd', per_page=10)

        coin_names = list()
        for coin in crypto_list:
            coin_names.append(coin['id'])


        # checks if coin1 or coin2 is a valid coin 
        if coin1 not in coin_names or coin2 not in coin_names:
            await message.channel.send('coin 1 or coin 2 is not a valid coin')
            return

        coin1_usdc = cg.get_price(ids=coin1, vs_currencies='usd')
        coin2_usdc = cg.get_price(ids=coin2, vs_currencies='usd')

        coin1_usdc = coin1_usdc[coin1]['usd']
        coin2_usdc = coin2_usdc[coin2]['usd']
        coin1_usdc = coin1_amount * coin1_usdc

        convert = coin1_usdc / coin2_usdc

        coin1_data = cg.get_coin_by_id(coin1, localization=False, tickers=False)
        coin1_symbol = coin1_data['symbol'].upper()

        coin2_data = cg.get_coin_by_id(coin2, localization=False, tickers=False)
        coin2_symbol = coin2_data['symbol'].upper()


        embed = discord.Embed(title=f'{coin1_symbol} --> {coin2_symbol}', color=discord.Colour.og_blurple())

        embed.set_author(name=f'{client.user.name}', icon_url=client.user.avatar)
        
        embed.set_thumbnail(url=f'https://seeklogo.com/images/U/uniswap-logo-782F5E6363-seeklogo.com.png')
        embed.add_field(name=f'{coin1_amount:.6f}', value=f'${coin1_usdc:,.2f}', inline=True)
        embed.add_field(name=f'{coin1_symbol}',value=f'${(coin1_usdc / coin1_amount):,.2f}', inline=True)

        embed.add_field(name='', value='', inline=False)

        embed.add_field(name=f'{convert:.6f}', value=f'${coin1_usdc:,.2f}', inline=True)
        embed.add_field(name=f'{coin2_symbol}',value=f'${coin2_usdc:,.2f}', inline=True)

        embed.set_footer(text=f'{client.user.name} data by CoinGecko')

        await message.channel.send(embed=embed)


    # Shows all data of that coin including chart
    if message.content.startswith('!chart'):

        # Searches the 2nd word as the coin after !chart
        try:
            _, coin_id = message.content.split(' ', 1)
            coin_id = coin_id.lower()

        except:
            await message.channel.send('Use "!chart coin_name" for this command.')

        crypto_list = cg.get_coins_markets(vs_currency='usd', per_page=10)

        coin_names = list()
        for coin in crypto_list:
            coin_names.append(coin['id'])


        # checks if coin_name is a valid coin 
        if coin_id not in coin_names:
            await message.channel.send(f'{coin_id} is not a valid coin')
            return


        # Uses API and gets all data of coin_id
        prices = cg.get_price(ids=f'{coin_id}', vs_currencies='usd', include_market_cap=True, include_24hr_vol=True)
        coin_data = cg.get_coin_by_id(coin_id, localization=False, tickers=False)



        coin_symbol = coin_data['symbol'].upper()
        coin_image_url = coin_data['image']['large']

        coin_30_day = coin_data['market_data']['price_change_percentage_30d']
        coin_24_hour =  coin_data['market_data']['price_change_percentage_24h']
        coin_7_day = coin_data['market_data']['price_change_percentage_7d']

        coin_current_price = prices[coin_id]['usd']
        coin_volume = prices[coin_id]['usd_24h_vol']
        coin_mc = prices[coin_id]['usd_market_cap']

        get_graph(coin_id)



        embed = discord.Embed(title=f'${coin_symbol}', color=discord.Colour.og_blurple())

        embed.set_author(name=f'{client.user.name}', icon_url=client.user.avatar)
        
        embed.set_thumbnail(url=f'{coin_image_url}')
        
        embed.add_field(name='Current Price', value=f'${coin_current_price:,}', inline=True)
        embed.add_field(name='24 Hour Volume', value=f'${coin_volume:,.0f}', inline=True)
        embed.add_field(name='Market Cap', value=f'${coin_mc:,.0f}', inline=True)

        embed.add_field(name='24 Hour', value=f'{coin_24_hour:.2f}%', inline=True)
        embed.add_field(name='7 day', value=f'{coin_7_day:.2f}%', inline=True)
        embed.add_field(name='30 day', value=f'{coin_30_day:.2f}%', inline=True)


        # Sets image from get_graph into embed.set_image
        file = discord.File(r"D:\CS\Python\projects\discord_bot\img\chart.png", filename="chart.png")
        embed.set_image(url="attachment://chart.png")

        embed.set_footer(text=f'{client.user.name} data by CoinGecko')

        await message.channel.send(file=file, embed=embed)

load_dotenv()
client.run(os.getenv('TOKEN'))