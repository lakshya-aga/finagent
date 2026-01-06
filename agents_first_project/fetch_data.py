
import os
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv

def fetch_nifty50_data(api_key):
    """
    Fetches NIFTY 50 daily price data for the last 10 years from Alpha Vantage.
    """
    ts = TimeSeries(key=api_key, output_format='pandas')
    # Fetching 'full' history for daily data. Alpha Vantage free tier might have limitations.
    # We'll assume the 'full' data will cover 10 years if available.
    print("Fetching NIFTY 50 data from Alpha Vantage...")
    try:
        data, meta_data = ts.get_daily(symbol='NSE:NIFTY', outputsize='full')
        print("Data fetched successfully.")
        # Rename columns for clarity and consistency
        data.columns = ['open', 'high', 'low', 'close', 'volume']
        data.index = pd.to_datetime(data.index)
        # Filter for the last 10 years
        ten_years_ago = pd.Timestamp.now() - pd.DateOffset(years=10)
        data = data[data.index >= ten_years_ago]
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Please ensure your API key is correct and you have access to NSE:NIFTY data.")
        return None

def main():
    load_dotenv()
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")

    if not api_key:
        print("ALPHAVANTAGE_API_KEY not found in .env file.")
        return

    nifty_data = fetch_nifty50_data(api_key)

    if nifty_data is not None and not nifty_data.empty:
        output_file = 'nifty_50_data.parquet'
        nifty_data.to_parquet(output_file)
        print(f"NIFTY 50 data saved to {output_file}")
    else:
        print("No data to save or data fetching failed.")

if __name__ == "__main__":
    main()
