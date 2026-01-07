
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import os

def load_data_from_csv(symbol):
    file_name = f"{symbol}_last_year.csv"
    if not os.path.exists(file_name):
        print(f"Error: Data file {file_name} not found.")
        return None
    df = pd.read_csv(file_name, index_col=0, parse_dates=True)
    df = df.astype(float)
    return df

def plot_ohlc(df, symbol):
    print(f"Plotting OHLC for {symbol}...")
    fig_name = f"{symbol}_ohlc.png"
    mpf.plot(df, type="candle", style="yahoo", title=f"{symbol} OHLC Last Year",
             ylabel="Price", savefig=fig_name)
    print(f"OHLC plot for {symbol} saved to {fig_name}")

if __name__ == "__main__":
    symbol = "AAPL"
    stock_data = load_data_from_csv(symbol)
    if stock_data is not None:
        plot_ohlc(stock_data, symbol)
