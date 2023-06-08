import discord
import requests
import json
import os
import asyncio
from dotenv import load_dotenv
from pycoingecko import CoinGeckoAPI
from discord_bot_utils import get_eth_price, get_graph, get_candle



# pycoingecko startup
cg = CoinGeckoAPI()

CRYPTOLIST = 100
crypto_list = cg.get_coins_markets(vs_currency='usd', per_page=CRYPTOLIST)

# Checks coin gecko server status
response = requests.get('https://api.coingecko.com/api/v3/ping')
ping = json.loads(response.text)
ping_status = ping['gecko_says']
print(f'CoinGeckoAPI server status: {ping_status}')

# Discord startup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)



async def update_crypto_list():
    crypto_list
    
    while True:
        crypto_list = cg.get_coins_markets(vs_currency='usd', per_page=CRYPTOLIST)
        await asyncio.sleep(600)  # Update every 10 minutes


async def update_eth_price():
    await client.wait_until_ready()
    while not client.is_closed():
        eth_price = get_eth_price()
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'Ethereum: ${eth_price:.2f}'))
        await asyncio.sleep(60)  # Updates every minute

    
# Next and Previous buttons for !list
class List_menu(discord.ui.View):
    def __init__(self, start_index=10):
        super().__init__()
        self.start_index = start_index

    @discord.ui.button(label='Previous', style=discord.ButtonStyle.red)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title='List of Valid Coins Names', color=discord.Colour.og_blurple())

        # Moves back 10 coins
        if self.start_index > 0:
            self.start_index -= 10

        start = self.start_index
        end = self.start_index + 10

        embed.set_author(name=f'{client.user.name}', icon_url=client.user.avatar)
        embed.set_thumbnail(url='https://play-lh.googleusercontent.com/CcboHyK1Id9XQWa8HXb_81Rvgqy7J816OHiTcGlezcwC-tx4cnrrXPx1x6cR0PowqA')

        for i in range(start, end):
            coin_id = crypto_list[i]['id']
            coin_name = crypto_list[i]['name']
            coin_symbol = crypto_list[i]['symbol']

            embed.add_field(name=f'{i + 1}. {coin_name} - ${coin_symbol}', value=f'!chart {coin_id}', inline=False)

        embed.set_footer(text=f'{client.user.name} data by CoinGecko')

        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.green)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title='List of Valid Coins Names', color=discord.Colour.og_blurple())

        # Moves forward 10 coins
        start = self.start_index
        end = self.start_index + 10

        if end >= CRYPTOLIST:
            end = CRYPTOLIST

        embed.set_author(name=f'{client.user.name}', icon_url=client.user.avatar)
        embed.set_thumbnail(url='https://play-lh.googleusercontent.com/CcboHyK1Id9XQWa8HXb_81Rvgqy7J816OHiTcGlezcwC-tx4cnrrXPx1x6cR0PowqA')

        print(start, end)
        for i in range(start, end):
            coin_id = crypto_list[i]['id']
            coin_name = crypto_list[i]['name']
            coin_symbol = crypto_list[i]['symbol']

            embed.add_field(name=f'{i + 1}. {coin_name} - ${coin_symbol}', value=f'!chart {coin_id}', inline=False)

        embed.set_footer(text=f'{client.user.name} data by CoinGecko')

        if end < CRYPTOLIST:
            self.start_index += 10

        await interaction.response.edit_message(embed=embed)


class Swap_menu(discord.ui.View):
    def __init__(self):
        super().__init__()
        


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(update_eth_price())


@client.event
async def on_message(message):
    crypto_list

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

    # Makes a list of the top 100 coins
    if message.content.startswith('!list'):
        view = List_menu()

        embed=discord.Embed(title='List of Valid Coins Names', color=discord.Colour.og_blurple())
        embed.set_author(name=f'{client.user.name}', icon_url=client.user.avatar)
        embed.set_thumbnail(url='https://play-lh.googleusercontent.com/CcboHyK1Id9XQWa8HXb_81Rvgqy7J816OHiTcGlezcwC-tx4cnrrXPx1x6cR0PowqA')


        # Prints top 10 intial coins
        for i in range(10):
            coin_id = crypto_list[i]['id']
            coin_name = crypto_list[i]['name']
            coin_symbol = crypto_list[i]['symbol']

            embed.add_field(name=f'{i + 1}. {coin_name} - ${coin_symbol}', value=f'!chart {coin_id}', inline=False)

        embed.set_footer(text=f'{client.user.name} data by CoinGecko')

        await message.channel.send(view=view, embed=embed)


    if message.content.startswith('!swap'):
        view = Swap_menu()

        # Checks if command is correctly formated
        try:
            _, coin1_amount, coin1, coin2 = message.content.split(' ', 3)
            coin1_amount = float(coin1_amount)
            coin1 = coin1.lower()
            coin2 = coin2.lower()

        except:
            await message.channel.send('Use "!swap # coin1_name coin2_name" for this command')

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


        view.add_item(discord.ui.Button(label='Swap', style=discord.ButtonStyle.link, url='https://app.uniswap.org/#/swap'))
        await message.channel.send(view=view, embed=embed)


    # Shows all data of that coin including chart
    if message.content.startswith('!chart'):

        # Searches the 2nd word as the coin after !chart
        try:
            _, coin_id = message.content.split(' ', 1)
            coin_id = coin_id.lower()

        except:
            await message.channel.send('Use "!chart coin_name" for this command.')


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

        get_graph(coin_id, coin_7_day)


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
        file = discord.File(r'D:\CS\Python\projects\Crypto-Discord-Bot\img\chart.png', filename='chart.png')
        embed.set_image(url='attachment://chart.png')

        embed.set_footer(text=f'{client.user.name} data by CoinGecko')

        await message.channel.send(file=file, embed=embed)


    # Shows a candlestick graph 
    if message.content.startswith('!candle'):

         # Searches the 2nd word as the coin after !candle
        try:
            _, coin_id = message.content.split(' ', 1)
            coin_id = coin_id.lower()

        except:
            await message.channel.send('Use "!chart coin_name" for this command.')


        coin_names = list()
        for coin in crypto_list:
            coin_names.append(coin['id'])


        # checks if coin_name is a valid coin 
        if coin_id not in coin_names:
            await message.channel.send(f'{coin_id} is not a valid coin')
            return


        get_candle(coin_id)
        coin_data = cg.get_coin_by_id(coin_id, localization=False, tickers=False)

        coin_symbol = coin_data['symbol'].upper()
        coin_image_url = coin_data['image']['large']

        embed = discord.Embed(title=f'${coin_symbol}', color=discord.Colour.og_blurple())
        embed.set_author(name=f'{client.user.name}', icon_url=client.user.avatar)
        embed.set_thumbnail(url=f'{coin_image_url}')

        embed.add_field(name=f'7 day candle of {coin_id}', value='', inline=True)

        file = discord.File(r'D:\CS\Python\projects\Crypto-Discord-Bot\img\candle.png', filename='candle.png')
        embed.set_image(url='attachment://candle.png')

        embed.set_footer(text=f'{client.user.name} data by CoinGecko')
        await message.channel.send(file=file, embed=embed)


load_dotenv()
client.run(os.getenv('TOKEN'))