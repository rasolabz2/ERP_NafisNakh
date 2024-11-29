import ccxt
import pandas as pd
import pandas_ta as ta
import time

# اتصال به Binance
exchange = ccxt.binance()

def get_low_price_coins():
    try:
        markets = exchange.fetch_tickers()
        low_price_coins = [symbol for symbol, data in markets.items() if data['last'] < 1 and 'USDT' in symbol]
        return low_price_coins
    except Exception as e:
        print(f"Error fetching tickers: {e}")
        return []

def fetch_ohlcv(symbol, timeframe='4h', limit=100):
    try:
        return exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    except Exception as e:
        print(f"Error fetching OHLCV for {symbol}: {e}")
        return []

def calculate_rsi(data):
    try:
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['rsi'] = ta.rsi(df['close'], length=14)
        return df
    except Exception as e:
        print(f"Error calculating RSI: {e}")
        return pd.DataFrame()

def filter_coins_by_rsi_and_volume(coins):
    results = []
    for coin in coins:
        try:
            ohlcv = fetch_ohlcv(coin)
            if not ohlcv:
                continue
            df = calculate_rsi(ohlcv)
            if df.empty:
                continue
            if df['rsi'].iloc[-1] < 40 and df['volume'].mean() > 1000:  # شرط حجم
                results.append(coin)
        except Exception as e:
            print(f"Error processing {coin}: {e}")
        time.sleep(1)  # جلوگیری از محدودیت API
    return results

# دریافت کوین‌ها و فیلتر نهایی
low_price_coins = get_low_price_coins()
if low_price_coins:
    filtered_coins = filter_coins_by_rsi_and_volume(low_price_coins)
    print("Filtered coins:", filtered_coins)
else:
    print("No low-price coins found.")
