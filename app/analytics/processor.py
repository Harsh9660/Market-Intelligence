import pandas as pd
import numpy as np
import os
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'pipeline_config.yaml')
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Data', 'data')

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def calculate_features(df):
    """
    Calculates robust technical indicators and features for ML.
    """
    if df is None or df.empty:
        return None
    
    config = load_config()
    features = config['pipeline']['features']
    
    # Ensure we are working with a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # 1. Technical Indicators
    # -----------------------------------------
    
    # SMA
    for window in [20, 50, 200]:
        df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
        
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    window = 20
    std_dev = 2
    df['BB_Middle'] = df['Close'].rolling(window=window).mean()
    df['BB_Std'] = df['Close'].rolling(window=window).std()
    df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * std_dev)
    df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * std_dev)
    
    # Volatility (Rolling Std Dev)
    df['Volatility'] = df['Close'].rolling(window=20).std()

    # 2. Transformations (ML Features)
    # -----------------------------------------
    
    # Log Returns
    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # Lagged Features (for time-series prediction)
    for lag in [1, 2, 3]:
        df[f'Close_Lag_{lag}'] = df['Close'].shift(lag)
        df[f'Vol_Lag_{lag}'] = df['Volume'].shift(lag)

    # Momentum
    df['Momentum_1d'] = df['Close'].pct_change(1)
    df['Momentum_5d'] = df['Close'].pct_change(5)

    # Drop NaN values created by rolling windows/lags
    # For large datasets, we might want to impute, but for finance, dropping valid is often safer
    df_clean = df.dropna()
    
    return df_clean

def process_file(ticker):
    """
    Reads raw data, calculates advanced features, and saves.
    """
    raw_path = os.path.join(DATA_DIR, f"{ticker}_raw.csv")
    if not os.path.exists(raw_path):
        print(f"Raw data for {ticker} not found.")
        return False
        
    try:
        df = pd.read_csv(raw_path, index_col=0, parse_dates=True)
        
        # Check if enough data exists for feature calculation
        if len(df) < 50: # Minimal buffer
            print(f"Not enough data to process {ticker} (need > 50 rows)")
            return False

        df_processed = calculate_features(df)
        
        processed_path = os.path.join(DATA_DIR, f"{ticker}_processed.csv")
        df_processed.to_csv(processed_path)
        print(f"Feature engineering complete for {ticker}. Saved to {processed_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return False

if __name__ == "__main__":
    process_file("AAPL")
