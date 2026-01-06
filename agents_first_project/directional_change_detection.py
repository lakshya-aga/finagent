
import pandas as pd
import numpy as np
from hmmlearn import hmm
import matplotlib.pyplot as plt
from sklearn.model_selection import ParameterGrid
import os

# Function to detect directional changes
def detect_directional_changes(prices, threshold):
    dc_points = []
    last_extreme = prices[0]
    is_uptrend = True  # Assume initial state is an uptrend or looking for a low

    dc_points.append({'price': prices[0], 'type': 'initial', 'index': 0})

    for i in range(1, len(prices)):
        current_price = prices[i]

        if is_uptrend:
            # In an uptrend, we are looking for a downward directional change
            if (last_extreme - current_price) / last_extreme >= threshold:
                dc_points.append({'price': current_price, 'type': 'down_dc', 'index': i})
                last_extreme = current_price
                is_uptrend = False
            elif current_price > last_extreme:
                last_extreme = current_price # Update last high
        else:
            # In a downtrend, we are looking for an upward directional change
            if (current_price - last_extreme) / last_extreme >= threshold:
                dc_points.append({'price': current_price, 'type': 'up_dc', 'index': i})
                last_extreme = current_price
                is_uptrend = True
            elif current_price < last_extreme:
                last_extreme = current_price # Update last low
    return pd.DataFrame(dc_points)

# Function to train HMM
def train_hmm(features, n_components=2, n_iter=100):
    model = hmm.GaussianHMM(n_components=n_components, covariance_type="diag", n_iter=n_iter, random_state=42)
    model.fit(features)
    return model

# Function to evaluate HMM (could be log-likelihood or a custom metric)
def evaluate_hmm(model, features):
    return model.score(features) # Returns the log-likelihood

def main():
    if not os.path.exists('data/nifty50_prices.parquet'):
        print("Error: data/nifty50_prices.parquet not found. Please run fetch_and_save_data.py first.")
        return

    df = pd.read_parquet('data/nifty50_prices.parquet')
    prices = df['Close'].values

    # Grid search for optimal threshold
    param_grid = {'threshold': np.linspace(0.005, 0.05, 10)} # Thresholds from 0.5% to 5%
    best_score = -np.inf
    best_threshold = None
    best_model = None
    best_dc_points = None

    results = []

    for params in ParameterGrid(param_grid):
        threshold = params['threshold']
        print(f"Testing threshold: {threshold:.4f}")

        dc_points_df = detect_directional_changes(prices, threshold)

        if len(dc_points_df) < 2: # Need at least two points to form a meaningful sequence for HMM
            print(f"Skipping threshold {threshold} due to insufficient directional change points.")
            results.append({'threshold': threshold, 'score': -np.inf, 'num_dc_points': len(dc_points_df)})
            continue

        # Prepare features for HMM. A simple feature could be the price change between DC points.
        # Or, the price at the DC point itself. Let's use the price at the DC point as observation.
        # Alternatively, we could use the percentage change between consecutive DC points.
        # For a start, let's use the actual price values at DC points.
        # Another option is the time duration between DC points, or the return.
        # Let's try the returns between consecutive DC points.
        dc_prices = dc_points_df['price'].values
        
        # Ensure enough data points for HMM, at least n_components
        if len(dc_prices) <= 2: # Need at least 2 points to calculate one return, and HMM needs more.
            print(f"Skipping threshold {threshold} due to insufficient DC prices for HMM training.")
            results.append({'threshold': threshold, 'score': -np.inf, 'num_dc_points': len(dc_points_df)})
            continue

        features = np.diff(np.log(dc_prices)).reshape(-1, 1) # Log returns between DC points

        # HMM requires at least as many samples as n_components * n_features
        # For n_components=2 and n_features=1, we need at least 2 samples.
        if len(features) < 2:
            print(f"Skipping threshold {threshold} due to insufficient features for HMM training ({len(features)} features).")
            results.append({'threshold': threshold, 'score': -np.inf, 'num_dc_points': len(dc_points_df)})
            continue


        try:
            model = train_hmm(features, n_components=2)
            score = evaluate_hmm(model, features)
            print(f"Threshold: {threshold:.4f}, HMM Log-Likelihood: {score:.2f}, DC Points: {len(dc_points_df)}")
            results.append({'threshold': threshold, 'score': score, 'num_dc_points': len(dc_points_df)})

            if score > best_score:
                best_score = score
                best_threshold = threshold
                best_model = model
                best_dc_points = dc_points_df

        except Exception as e:
            print(f"Error training HMM for threshold {threshold:.4f}: {e}")
            results.append({'threshold': threshold, 'score': -np.inf, 'num_dc_points': len(dc_points_df)})


    print(f"\nOptimal Threshold: {best_threshold:.4f} with HMM Log-Likelihood: {best_score:.2f}")

    if best_model and best_dc_points is not None:
        print("\nFitting HMM with optimal threshold and plotting results...")
        dc_prices = best_dc_points['price'].values
        features = np.diff(np.log(dc_prices)).reshape(-1, 1)

        hidden_states = best_model.predict(features)

        # Plotting
        plt.figure(figsize=(15, 7))
        plt.plot(df.index, prices, label='NIFTY 50 Close Price', alpha=0.7)

        # Plotting DC points
        up_dc = best_dc_points[best_dc_points['type'] == 'up_dc']
        down_dc = best_dc_points[best_dc_points['type'] == 'down_dc']
        plt.scatter(df.index[up_dc['index']], up_dc['price'], marker='^', color='green', s=100, label='Up DC', zorder=5)
        plt.scatter(df.index[down_dc['index']], down_dc['price'], marker='v', color='red', s=100, label='Down DC', zorder=5)

        # Plotting HMM states (this is tricky with DC points vs original prices)
        # We can color the background based on the detected HMM state at each DC point
        # Or, we can interpolate the states back to the original time series.
        # Let's plot the regimes along the original price series for better visualization.

        # Map HMM states back to the original daily prices
        # The hidden_states array has length len(features), which is len(dc_prices) - 1.
        # Each state corresponds to the period *after* a directional change until the next.
        
        # A simpler visualization for states for now: color the segments between DC points
        
        # We need to map the states (which correspond to transitions between DC points)
        # back to the time series.
        
        state_colors = ['blue', 'orange', 'purple', 'cyan'] # More colors if n_components > 2
        
        # The states correspond to the periods *between* DC points.
        # hidden_states[k] is the state from dc_points_df.index[k] to dc_points_df.index[k+1]
        
        # To visualize, we can draw lines or shaded regions.
        for k in range(len(hidden_states)):
            start_idx_orig = best_dc_points['index'].iloc[k]
            end_idx_orig = best_dc_points['index'].iloc[k+1]
            
            plt.axvspan(df.index[start_idx_orig], df.index[end_idx_orig], 
                        facecolor=state_colors[hidden_states[k]], alpha=0.15)
        
        # Add labels for the regimes (optional, depends on clarity)
        # For simplicity, let's just use the shaded regions for now.

        plt.title(f'NIFTY 50 Price with Directional Changes (Threshold: {best_threshold:.4f}) and HMM Regimes')
        plt.xlabel('Date')
        plt.ylabel('Close Price')
        plt.legend()
        plt.grid(True)
        
        # Create a directory for plots if it doesn't exist
        if not os.path.exists('plots'):
            os.makedirs('plots')
        
        plt.savefig('plots/nifty50_dc_hmm_analysis.png')
        print("Analysis plot saved to plots/nifty50_dc_hmm_analysis.png")
        plt.close()

    else:
        print("Could not find optimal threshold or train HMM successfully.")

if __name__ == "__main__":
    main()
