
import pandas as pd
import numpy as np
import os
from alpha_vantage.timeseries import TimeSeries


def fetch_nifty50_data():
    """
    Fetches NIFTY 50 data using Alpha Vantage API.
    """
    api_key = os.getenv('ALPHAVANTAGE_API_KEY')
    if not api_key:
        print("Alpha Vantage API key not found. Using dummy data.")

    print("Fetching NIFTY 50 data from Alpha Vantage...")
    ts = TimeSeries(key=api_key, output_format='pandas')
    try:
        # Use '^NSEI' for NIFTY 50, 'full' for all available data
        data, meta_data = ts.get_daily(symbol='^NSEI', outputsize='full')
        # Alpha Vantage returns '4. close' for closing price
        data = data.rename(columns={'4. close': 'Close'})
        return data[['Close']].sort_index() # Ensure chronological order
    except Exception as e:
        print(f"Error fetching data from Alpha Vantage: {e}.")

def main():
    if not os.path.exists('data'):
        os.makedirs('data')

    df = fetch_nifty50_data()
    parquet_file_path = 'data/nifty50_prices.parquet'
    df.to_parquet(parquet_file_path)
    print(f"NIFTY 50 data saved to {parquet_file_path}")

if __name__ == "__main__":
    main()
