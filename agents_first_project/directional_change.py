
import pandas as pd
import numpy as np

def detect_directional_changes(prices: pd.Series, threshold: float) -> pd.Series:
    """
    Detects directional changes in a price series based on a given threshold.

    Args:
        prices: A pandas Series of prices (e.g., closing prices).
        threshold: The percentage threshold for detecting directional changes (e.g., 0.01 for 1%).

    Returns:
        A pandas Series indicating directional change events:
        1 for upward directional change,
        -1 for downward directional change,
        0 for no directional change.
    """
    dc_events = pd.Series(0, index=prices.index, dtype=int)
    
    if prices.empty:
        return dc_events

    last_high = prices.iloc[0]
    last_low = prices.iloc[0]
    
    # State: 0 = monitoring for uptrend (price > last_low * (1 + threshold))
    #        1 = monitoring for downtrend (price < last_high * (1 - threshold))
    current_state = 0 

    for i in range(1, len(prices)):
        current_price = prices.iloc[i]

        if current_state == 0:  # Monitoring for uptrend
            if current_price > last_low * (1 + threshold):
                dc_events.iloc[i] = 1  # Upward DC detected
                last_high = current_price
                current_state = 1
            elif current_price < last_low: # Update last_low if price drops further
                last_low = current_price
        
        elif current_state == 1:  # Monitoring for downtrend
            if current_price < last_high * (1 - threshold):
                dc_events.iloc[i] = -1  # Downward DC detected
                last_low = current_price
                current_state = 0
            elif current_price > last_high: # Update last_high if price rises further
                last_high = current_price

    return dc_events

if __name__ == '__main__':
    # Example Usage:
    # First, ensure you have run fetch_and_save_data.py to get nifty50_prices.parquet
    try:
        nifty_data = pd.read_parquet('data/nifty50_prices.parquet')
        close_prices = nifty_data['Close'] # Changed to 'Close'

        # Example threshold
        threshold_percentage = 1.0  # 1%
        threshold_value = threshold_percentage / 100.0

        print(f"Detecting directional changes with threshold: {threshold_percentage}%")
        directional_changes = detect_directional_changes(close_prices, threshold_value)

        print("\nDirectional Change Events (first 20):")
        print(directional_changes[directional_changes != 0].head(20))
        print(f"Total directional change events: {directional_changes[directional_changes != 0].count()}")

    except FileNotFoundError:
        print("Error: 'data/nifty50_prices.parquet' not found.")
        print("Please run 'fetch_and_save_data.py' first to download the NIFTY 50 data.")
    except Exception as e:
        print(f"An error occurred: {e}")
