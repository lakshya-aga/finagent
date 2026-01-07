import os
import sys
import argparse

os.environ["ALPHAVANTAGE_API_KEY"] = "BPWQMYD9I2E15TFH"

parser = argparse.ArgumentParser(description="Run plot_ohlc_supertrend.py with Alpha Vantage API key set.")
parser.add_argument("--symbol", default="IBM", help="The stock ticker symbol (e.g., IBM, NIFTY50).")
parser.add_argument("--start_date", default="2023-01-01", help="Start date for fetching data (YYYY-MM-DD).")
parser.add_argument("--end_date", help="End date for fetching data (YYYY-MM-DD). Defaults to today.")

args = parser.parse_args()

sys.argv = ['plot_ohlc_supertrend.py', '--symbol', args.symbol]

if args.start_date:
    sys.argv.extend(['--start_date', args.start_date])
if args.end_date:
    sys.argv.extend(['--end_date', args.end_date])

with open("plot_ohlc_supertrend.py", "r") as f:
    code = f.read()
exec(code)