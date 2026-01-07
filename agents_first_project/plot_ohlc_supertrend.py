import pandas as pd
import mplfinance as mpf
import numpy as np
import requests
import os
import argparse
import dotenv

dotenv.load_dotenv()

def get_alphavantage_data(ticker, start_date, end_date):
    """Fetches OHLC data from Alpha Vantage."""
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHAVANTAGE_API_KEY environment variable not set.")

    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "compact",  # or "compact"
        "apikey": api_key
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError(f"Could not retrieve data for {ticker}. Alpha Vantage response: {data}")

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    })

    # Filter by date range
    df = df[(df.index >= start_date) & (df.index <= end_date)]
    df = df.sort_index()
    return df

def calculate_supertrend(data, window=10, multiplier=3):
    """Calculates Supertrend indicator."""
    high_series = data['High'].squeeze()
    low_series = data['Low'].squeeze()
    close_series = data['Close'].squeeze()

    high_low = high_series - low_series
    high_prev_close = abs(high_series - close_series.shift(1))
    low_prev_close = abs(low_series - close_series.shift(1))

    tr = pd.DataFrame({'hl': high_low, 'hpc': high_prev_close, 'lpc': low_prev_close}, index=data.index).max(axis=1)
    atr = tr.ewm(span=window, adjust=False).mean()

    data['basic_upper_band'] = ((high_series + low_series) / 2) + (multiplier * atr)
    data['basic_lower_band'] = ((high_series + low_series) / 2) - (multiplier * atr)

    data['final_upper_band'] = data['basic_upper_band']
    data['final_lower_band'] = data['basic_lower_band']
    data['supertrend'] = np.nan
    data['supertrend_direction'] = np.nan

    for i in range(1, len(data)):
        current_close = data.iloc[i]['Close']
        prev_final_upper_band = data['final_upper_band'].iloc[i-1]
        prev_final_lower_band = data['final_lower_band'].iloc[i-1]
        prev_supertrend_direction = data['supertrend_direction'].iloc[i-1]

        if current_close > prev_final_upper_band:
            data.loc[data.index[i], 'supertrend_direction'] = 1
        elif current_close < prev_final_lower_band:
            data.loc[data.index[i], 'supertrend_direction'] = -1
        else:
            data.loc[data.index[i], 'supertrend_direction'] = prev_supertrend_direction
            if data.loc[data.index[i], 'supertrend_direction'] == 1:
                data.loc[data.index[i], 'final_lower_band'] = max(data['basic_lower_band'].iloc[i], prev_final_lower_band)
            elif data.loc[data.index[i], 'supertrend_direction'] == -1:
                data.loc[data.index[i], 'final_upper_band'] = min(data['basic_upper_band'].iloc[i], prev_final_upper_band)

        if data.loc[data.index[i], 'supertrend_direction'] == 1:
            data.loc[data.index[i], 'supertrend'] = data.loc[data.index[i], 'final_lower_band']
        else:
            data.loc[data.index[i], 'supertrend'] = data.loc[data.index[i], 'final_upper_band']
    return data

def plot_ohlc_supertrend(ticker, start_date="2023-01-01", end_date=None):
    """
    Fetches OHLC data for a given ticker, calculates Supertrend, and plots it.

    Args:
        ticker (str): The stock ticker symbol.
        start_date (str): Start date for fetching data (YYYY-MM-DD).
        end_date (str): End date for fetching data (YYYY-MM-DD). Defaults to today.
    """
    if end_date is None:
        end_date = pd.Timestamp.today().strftime("%Y-%m-%d")

    print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
    try:
        data = get_alphavantage_data(ticker, start_date, end_date)
    except ValueError as e:
        print(f"Error fetching data: {e}")
        return

    if data.empty:
        print(f"No data fetched for {ticker}. Please check the ticker symbol or date range.")
        return
    print(data.head())
    data = calculate_supertrend(data.copy()) # Use .copy() to avoid SettingWithCopyWarning

    # Debug print statement
    print(f"DataFrame columns before plotting: {data.columns.tolist()}")
    if 'Volume' not in data.columns:
        print("Error: 'Volume' column not found in DataFrame.")

    mc = mpf.make_marketcolors(up='#00ff00', down='#ff0000', wick='inherit', edge='inherit', volume='#eb4034')
    s = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)

    apds = [
        mpf.make_addplot(data['supertrend'], color='blue', width=0.75, panel=0, ylabel="Supertrend")
    ]

    fig, axes = mpf.plot(data, type='candle', style=s, title=f"{ticker} OHLC with Supertrend",
                       ylabel='Price', volume=True, ylabel_lower='Volume', figsize=(12, 8), addplot=apds, returnfig=True)

    fig.savefig(f"{ticker}_ohlc_supertrend.png")
    print(f"Plot saved as {ticker}_ohlc_supertrend.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot OHLC and Supertrend for a given stock ticker.")
    parser.add_argument("--symbol", required=True, help="The stock ticker symbol (e.g., IBM, NIFTY50).")
    parser.add_argument("--start_date", default="2023-01-01", help="Start date for fetching data (YYYY-MM-DD).")
    parser.add_argument("--end_date", help="End date for fetching data (YYYY-MM-DD). Defaults to today.")
    
    args = parser.parse_args()
    
    plot_ohlc_supertrend(ticker=args.symbol, start_date=args.start_date, end_date=args.end_date)