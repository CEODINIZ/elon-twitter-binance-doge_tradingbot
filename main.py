from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from decimal import Decimal as D

import schedule, time, math, os

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

TWITTER_URL = 'https://twitter.com/elonmusk/'

driver = webdriver.Firefox()

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"}

API_KEY = os.getenv('API_KEY')
API_SECRET = os.environ.get('API_SECRET')

binance_client = Client(API_KEY, API_SECRET)

BUY_WITH = "USDT"

# how much BUY_WITH should be spent when buying DOGE?
max_spending = 400

# sell price multiplier (1.2: will create a limit SELL order at +20% from the original BUY price)
sell_price_mutiplier = 1.2

def check_balance():
    global max_spending
    
    balance = binance_client.get_asset_balance(asset=BUY_WITH)
    inUSDT = balance['free']
    if BUY_WITH != "USDT":
        # convert to USDT
        avg_market_price = binance_client.get_avg_price(symbol=BUY_WITH+'USDT')
        inUSDT = float(balance['free']) * float(avg_market_price['price'])
    
    print(f"Current spot wallet balance: {balance['free']} {BUY_WITH} / {inUSDT} USDT")
    
    if max_spending > float(balance['free']):
        print(f"WARNING: Your spot wallet balance is below your max spending. Will use your wallet balance {inUSDT} USDT instead.")
        max_spending = balance["free"]
    
def buy_coins():
    symbol = "DOGE" + BUY_WITH
    avg_market_price = binance_client.get_avg_price(symbol=symbol)

    quan = max_spending / float(avg_market_price["price"]) 
    sym_info = binance_client.get_symbol_info(symbol)

    lotSizeFilter = next(item for item in sym_info["filters"] if item["filterType"] == "LOT_SIZE")
    #corrected_Quantity = math.floor(quan / float(lotSizeFilter["stepSize"])) * float(lotSizeFilter["stepSize"])
    corrected_Quantity = float(D.from_float(quan).quantize(D(str(lotSizeFilter["stepSize"]).rstrip("0"))))

    try:
        order = binance_client.create_order(
            symbol=symbol,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=corrected_Quantity)
        
        avg_price = avg_market_price["price"]
        print(f"Bought {corrected_Quantity} {symbol} (avg market pric was {avg_price}), fills:")
        for fill in order["fills"]:
            qty = fill["qty"]
            price_fill = fill["price"]
            print(f"Qty: {qty}, Price: {price_fill}")
        
        # placing sell order
        sell_price = float(order["fills"][0]["price"])*sell_price_mutiplier

        priceFilter =  next(item for item in sym_info["filters"] if item["filterType"] == "PRICE_FILTER")

        sell_price_filtered = float(D.from_float(sell_price).quantize(D(priceFilter["tickSize"].rstrip("0"))))
        
        print(f"Placing sell order at avg price: : {sell_price_filtered}")
        sell_order = binance_client.order_limit_sell(
            symbol=symbol,
            quantity=corrected_Quantity,
            price=sell_price_filtered)
        
        print(f"Placed sell order at avg price: {sell_price_filtered}")
        
        
    except BinanceAPIException as e:
        print(e)
    except BinanceOrderException as e:
        print(e)

def get_latest_tweet():
    driver.get(TWITTER_URL)

    try:
        first_tweet_xpath = '//*[@data-testid="tweet"]'
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, first_tweet_xpath))
        )
    except TimeoutException as e:
        # tweets are not visible in some rare cases, return empty string instead
        return ""
    finally:
        return element.text
    

doge_found = False

def check_for_doge_tweet():
    global doge_found

    latest_tweet_text = get_latest_tweet().split("\n")[4]
    logging.info(f"Last tweet text: {latest_tweet_text}")

    if "doge" in latest_tweet_text.lower() and not doge_found:
        print("Found a doge Tweet!")
        print(latest_tweet_text)

        # buying coins
        doge_found = True
        buy_coins()

check_balance()
check_for_doge_tweet()
schedule.every(10).seconds.do(check_for_doge_tweet)

while True:
    schedule.run_pending()
    time.sleep(1)
