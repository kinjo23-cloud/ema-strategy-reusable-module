import ccxt
import pandas as pd
import ta
import time

# Connect to Binance API using ccxt
binance = ccxt.binance()

# Define the symbol to trade
symbol = 'BTC/USDT'

# Define the timeframes to fetch data for
timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '1d']

# Function to fetch OHLCV data for each timeframe
def fetch_data(symbol, timeframe):
    ohlcv = binance.fetch_ohlcv(symbol, timeframe, limit=100)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# Function to calculate EMAs for each dataframe
def calculate_ema(df, periods):
    for period in periods:
        df[f'EMA_{period}'] = ta.trend.ema_indicator(df['close'], window=period)
    return df

# Function to craft the bullish strategy
def bullish_strategy(data):
    ema21_crosses_above_ema50_1m = data['1m']['EMA_21'].iloc[-2] < data['1m']['EMA_50'].iloc[-2] and data['1m']['EMA_21'].iloc[-1] > data['1m']['EMA_50'].iloc[-1]
    ema21_above_ema200_5m = data['5m']['EMA_21'].iloc[-1] > data['5m']['EMA_200'].iloc[-1]
    ema9_above_ema21_15m = data['15m']['EMA_9'].iloc[-1] > data['15m']['EMA_21'].iloc[-1]   
    close_above_ema50_1m = data['1m']['close'].iloc[-1] > data['1m']['EMA_50'].iloc[-1] # Check if the last candle close is above EMA_50

    if ema21_crosses_above_ema50_1m and ema21_above_ema200_5m and ema9_above_ema21_15m:
        return "Buy Signal"
    else:
        return "No Signal"

# Function to craft the bearish strategy
def bearish_strategy(data):
    ema9_crosses_below_ema21_1m = data['1m']['EMA_9'].iloc[-2] > data['1m']['EMA_21'].iloc[-2] and data['1m']['EMA_9'].iloc[-1] < data['1m']['EMA_21'].iloc[-1]
    ema21_below_ema200_5m = data['5m']['EMA_21'].iloc[-1] < data['5m']['EMA_200'].iloc[-1]
    ema9_below_ema21_1h = data['1h']['EMA_9'].iloc[-1] < data['1h']['EMA_21'].iloc[-1]

    if ema9_crosses_below_ema21_1m and ema21_below_ema200_5m and ema9_below_ema21_1h:
        return "Sell Signal"
    else:
        return "No Signal"

# Function to place orders based on the signal
def place_order(signal):
    if signal == "Buy Signal":
        print("Placing Buy Order...")
    elif signal == "Sell Signal":
        print("Placing Sell Order...")
    else:
        print("No trade signal. Waiting...")

# Function to run the strategy continuously
def run_continuous():
    while True:
        # Fetch data for all timeframes
        data = {}
        for tf in timeframes:
            data[tf] = fetch_data(symbol, tf)

        # Calculate EMAs for each timeframe
        for tf in timeframes:
            data[tf] = calculate_ema(data[tf], [9, 21, 50, 200])

        # Apply the strategy (you can choose any strategy here)
        signal = bullish_strategy(data)  # or bearish_strategy(data), trend_continuation_strategy(data)
        
        # Print the closing time of the last candle
        last_candle_time = data['1m']['timestamp'].iloc[-1]
        print(f"Last candle closed at: {last_candle_time}")

        # Place an order based on the signal
        place_order(signal)
        
        # Sleep for 60 seconds before running again
        time.sleep(60)

# Start the continuous loop
run_continuous()
