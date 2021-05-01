 # Elon Musk Twitter Binance Dogecoin Tradingbot
 
 Automatically buys Dogecoin on Binance whenever Elon Musk tweets about Dogecoin (tweet text contains "doge") usign market orders. Also puts up a sell limit order on a configurable price target (+20% by default).
 Uses Selenium for bypassing twitter-api rate limits. It will check @elonmusk on twitter every 10 seconds.
 
 Requires python3.9 and `requests, python-binance, schedule, selenium`.
 
 See main.py for max spending amount and the coin to spend.
 
 Start with
 `API_KEY=your_binance_api_key API_SECRET=your_binance_api_secret python3.9 main.py`
 
 optionally headless on a server:
 `MOZ_HEADLESS=1 API_KEY=your_binance_api_key API_SECRET=your_binance_api_secret python3.9 main.py`
