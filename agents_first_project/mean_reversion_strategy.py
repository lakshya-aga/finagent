
import pandas as pd
import numpy as np
from directional_change import detect_directional_changes # Import the DC detection function
import matplotlib.pyplot as plt

def calculate_returns(prices, signals):
    """
    Calculates returns based on trading signals.
    signals: 1 for long, -1 for short, 0 for no position.
    """
    # Shift signals to account for execution at the next period's open/close
    # For simplicity, let's assume close-to-close returns based on signal
    returns = prices.pct_change().shift(-1) * signals.shift(1)
    return returns.fillna(0)

def calculate_profitability(returns):
    """Calculates cumulative profitability."""
    return (1 + returns).cumprod() - 1

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """
    Calculates the Sharpe Ratio.
    Assumes daily returns and annualizes.
    """
    daily_excess_returns = returns - risk_free_rate / 252 # Assuming 252 trading days
    if daily_excess_returns.std() == 0:
        return 0.0
    sharpe = np.sqrt(252) * daily_excess_returns.mean() / daily_excess_returns.std()
    return sharpe

def simple_mean_reversion_strategy(prices, window=20):
    """
    Implements a simple mean-reversion strategy.
    Goes short when price > SMA, long when price < SMA.
    """
    signals = pd.Series(0, index=prices.index, dtype=int)
    
    # Calculate Simple Moving Average
    sma = prices.rolling(window=window).mean()

    # Generate signals
    signals[prices < sma] = 1   # Go long when price is below SMA
    signals[prices > sma] = -1  # Go short when price is above SMA

    # We need to ensure we don't trade on the first `window` days as SMA is not defined
    signals[:window-1] = 0

    return signals

def regime_aware_mean_reversion_strategy(prices, window=20, dc_threshold=0.01):
    """
    Implements a mean-reversion strategy with regime detection.
    Reverses logic when regime changes (detected by directional changes).
    """
    signals = pd.Series(0, index=prices.index, dtype=int)
    
    # Calculate Simple Moving Average
    sma = prices.rolling(window=window).mean()

    # Detect directional changes
    dc_events = detect_directional_changes(prices, dc_threshold)

    # Initialize current regime logic: 0 for normal, 1 for reversed
    current_regime_reversed = False 

    for i in range(len(prices)):
        if i < window-1: # Skip initial period where SMA is not defined
            continue

        # Check for regime change
        if dc_events.iloc[i] != 0: # A DC event signals a potential regime change
            current_regime_reversed = not current_regime_reversed

        # Apply strategy based on current regime
        if current_regime_reversed:
            # Reversed logic: Go long when price > SMA, short when price < SMA
            if prices.iloc[i] > sma.iloc[i]:
                signals.iloc[i] = 1
            elif prices.iloc[i] < sma.iloc[i]:
                signals.iloc[i] = -1
        else:
            # Normal logic: Go long when price < SMA, short when price > SMA
            if prices.iloc[i] < sma.iloc[i]:
                signals.iloc[i] = 1
            elif prices.iloc[i] > sma.iloc[i]:
                signals.iloc[i] = -1
    
    return signals


if __name__ == '__main__':
    try:
        # Load sample data (e.g., AAPL last year's close prices)
        df = pd.read_csv('AAPL_last_year.csv', index_col=0, parse_dates=True) # Changed index_col='Date' to index_col=0
        close_prices = df['Close']

        print("--- Running Simple Mean-Reversion Strategy ---")
        simple_signals = simple_mean_reversion_strategy(close_prices)
        simple_returns = calculate_returns(close_prices, simple_signals)
        simple_profitability = calculate_profitability(simple_returns)
        simple_sharpe = calculate_sharpe_ratio(simple_returns)

        print(f"Simple Strategy - Cumulative Profitability: {simple_profitability.iloc[-1]:.4f}")
        print(f"Simple Strategy - Sharpe Ratio: {simple_sharpe:.4f}")

        print("\n--- Running Regime-Aware Mean-Reversion Strategy ---")
        regime_aware_signals = regime_aware_mean_reversion_strategy(close_prices, dc_threshold=0.01)
        regime_aware_returns = calculate_returns(close_prices, regime_aware_signals)
        regime_aware_profitability = calculate_profitability(regime_aware_returns)
        regime_aware_sharpe = calculate_sharpe_ratio(regime_aware_returns)

        print(f"Regime-Aware Strategy - Cumulative Profitability: {regime_aware_profitability.iloc[-1]:.4f}")
        print(f"Regime-Aware Strategy - Sharpe Ratio: {regime_aware_sharpe:.4f}")

        # Optional: Plot cumulative returns
        plt.figure(figsize=(12, 6))
        plt.plot(simple_profitability.index, simple_profitability, label='Simple Mean-Reversion')
        plt.plot(regime_aware_profitability.index, regime_aware_profitability, label='Regime-Aware Mean-Reversion')
        plt.title('Cumulative Returns of Mean-Reversion Strategies')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('mean_reversion_strategy_returns.png')
        print("\nCumulative returns plot saved to mean_reversion_strategy_returns.png")

    except FileNotFoundError:
        print("Error: 'AAPL_last_year.csv' not found. Please ensure it exists.")
    except Exception as e:
        print(f"An error occurred: {e}")
