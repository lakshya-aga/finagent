
import requests
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import datetime
import time # Import the time module
import os

# Alpha Vantage API key
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY") # This should ideally be loaded from an environment variable for security

def fetch_stock_data(symbol, api_key):
    print(f"Fetching data for {symbol}...")
    # Removed outputsize=full as it's a premium feature. Default outputsize is compact (last 100 days).
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        print(f"Error fetching data for {symbol}: {data}")
        return None

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
    df = df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    })
    df.index = pd.to_datetime(df.index)
    df = df.astype(float) # Convert all data to float
    df = df.sort_index()

    # Filter for the last year - Note: With compact outputsize, this will only be the last 100 days or less.
    # If full year data is critical, a premium API key is required.
    one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
    df = df[df.index >= one_year_ago]
    return df

def save_data_to_csv(df, symbol):
    file_name = f"{symbol}_last_year.csv"
    df.to_csv(file_name)
    print(f"Data for {symbol} saved to {file_name}")

def plot_ohlc(df, symbol):
    print(f"Plotting OHLC for {symbol}...")
    fig_name = f"{symbol}_ohlc.png"
    mpf.plot(df, type="candle", style="yahoo", title=f"{symbol} OHLC Last Year",
             ylabel="Price", savefig=fig_name)
    print(f"OHLC plot for {symbol} saved to {fig_name}")

if __name__ == "__main__":
    symbols = ["AAPL", "GOOGL"]

    for i, symbol in enumerate(symbols):
        stock_data = fetch_stock_data(symbol, API_KEY)
        if stock_data is not None:
            save_data_to_csv(stock_data, symbol)
            plot_ohlc(stock_data, symbol)
        
        # Introduce a delay to respect API rate limits (5 requests per minute for free tier)
        if i < len(symbols) - 1: # Don't delay after the last request
            print("Waiting for 15 seconds to respect API rate limits...")
            time.sleep(15) # 15 seconds delay will allow 4 requests per minute, respecting the 5/min limit.
