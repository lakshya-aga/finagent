
import pandas as pd
import numpy as np
from hmmlearn import hmm
from sklearn.model_selection import ParameterGrid
from directional_change import detect_directional_changes
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def train_and_evaluate_hmm(data: np.ndarray, n_components: int = 2, n_iter: int = 100) -> tuple:
    """
    Trains a Gaussian Hidden Markov Model and returns the model and its log-likelihood.

    Args:
        data: The input data for the HMM (e.g., price changes or directional change indicators).
        n_components: The number of hidden states for the HMM.
        n_iter: The number of iterations for the HMM training.

    Returns:
        A tuple containing the trained HMM model and its log-likelihood.
    """
    # Reshape data for HMM: (n_samples, n_features). Here, n_features is 1.
    if data.ndim == 1:
        data = data.reshape(-1, 1)

    model = hmm.GaussianHMM(n_components=n_components, covariance_type="full", n_iter=n_iter, random_state=42)
    try:
        model.fit(data)
        log_likelihood = model.score(data)
        return model, log_likelihood
    except Exception as e:
        # print(f"Error training HMM: {e}")
        return None, -np.inf # Return negative infinity for log-likelihood on error

def main():
    try:
        nifty_data = pd.read_parquet('data/nifty50_prices.parquet') # Changed path
        close_prices = nifty_data['Close'] # Changed to 'Close'
    except FileNotFoundError:
        print("Error: 'data/nifty50_prices.parquet' not found.")
        print("Please run 'fetch_and_save_data.py' first to download the NIFTY 50 data.")
        return
    except Exception as e:
        print(f"An error occurred while loading data: {e}")
        return

    # Define the parameter grid for threshold
    param_grid = {'threshold': np.arange(0.005, 0.05, 0.005)}  # Thresholds from 0.5% to 4.5% in 0.5% steps
    best_threshold = None
    best_log_likelihood = -np.inf
    best_model = None
    best_dc_events_for_best_threshold = None # Store DC events for the best threshold

    print("Starting Grid Search for optimal threshold...")
    for params in ParameterGrid(param_grid):
        threshold = params['threshold']
        print(f"Testing threshold: {threshold*100:.2f}%")

        # Detect directional changes. dc_events will have the same index as close_prices.
        dc_events = detect_directional_changes(close_prices, threshold)

        # Prepare returns for HMM. returns will be shorter than close_prices by 1.
        returns = close_prices.pct_change().dropna()
        if len(returns) == 0:
            print(f"Not enough data for threshold {threshold*100:.2f}%. Skipping.")
            continue

        # Using raw returns as observations for the HMM
        model, log_likelihood = train_and_evaluate_hmm(returns.values) # Pass numpy array
        
        if model is not None and log_likelihood > best_log_likelihood:
            best_log_likelihood = log_likelihood
            best_threshold = threshold
            best_model = model
            # Store the DC events that align with the returns used for HMM training
            best_dc_events_for_best_threshold = dc_events.loc[returns.index] 
    
    print("\nGrid Search Complete.")
    if best_threshold is not None:
        print(f"Optimal Threshold: {best_threshold*100:.2f}%")
        print(f"Best Log-Likelihood: {best_log_likelihood:.2f}")

        # Now, use the best_model to predict states and analyze them with DC events
        print("\nAnalyzing Hidden States with Optimal Threshold...")
        
        # Use the returns data that corresponds to the best_threshold
        optimal_returns = close_prices.pct_change().dropna()
        
        if best_model and len(optimal_returns) > 0:
            hidden_states = best_model.predict(optimal_returns.values.reshape(-1, 1))
            
            # Align hidden states with the index of optimal_returns and best_dc_events
            state_series = pd.Series(hidden_states, index=optimal_returns.index)
            
            print("\nCorrelation between Hidden States and Directional Changes (first 20 events with optimal threshold):")
            
            # Create a combined DataFrame for easier inspection
            analysis_df = pd.DataFrame({
                'Close': close_prices.loc[optimal_returns.index],
                'Returns': optimal_returns,
                'Hidden_State': state_series,
                'DC_Event': best_dc_events_for_best_threshold  # This is already aligned with optimal_returns.index
            })

            # Display some events where DC occurred and their corresponding state
            print(analysis_df[analysis_df['DC_Event'] != 0].head(20))

            print("\nSummary of Hidden States and Directional Changes:")
            for state in sorted(analysis_df['Hidden_State'].unique()):
                state_df = analysis_df[analysis_df['Hidden_State'] == state]
                total_dc_in_state = state_df['DC_Event'].abs().sum()
                up_dc_in_state = (state_df['DC_Event'] == 1).sum()
                down_dc_in_state = (state_df['DC_Event'] == -1).sum()
                print(f"State {state}:")
                print(f"  Total DC events: {total_dc_in_state}")
                print(f"  Up DC events: {up_dc_in_state}")
                print(f"  Down DC events: {down_dc_in_state}")
                if not state_df.empty:
                    print(f"  Mean Return: {state_df['Returns'].mean():.4f}")
                    print(f"  Std Dev Return: {state_df['Returns'].std():.4f}")
                print("\n")

    else:
        print("Could not find an optimal threshold.")

if __name__ == '__main__':
    main()
