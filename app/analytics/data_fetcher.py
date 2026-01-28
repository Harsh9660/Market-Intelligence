import yfinance as yf
import pandas as pd
import os
import yaml
from pathlib import Path

# Load Configuration
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'pipeline_config.yaml')
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Data', 'data')

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def fetch_data(ticker, period=None, interval=None):
    """
    Fetches historical market data from Yahoo Finance.
    Supports config-driven defaults.
    """
    config = load_config()
    period = period or config['pipeline']['data']['period']
    interval = interval or config['pipeline']['data']['interval']
    
    print(f"Fetching {ticker} (Period: {period}, Interval: {interval})...")
    
    try:
        # yfinance download for better control
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        
        if df.empty:
            print(f"Warning: No data found for {ticker}")
            return None

        # Flatten MultiIndex columns if present (common in new yfinance)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Ensure DATA_DIR exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Save raw data
        file_path = os.path.join(DATA_DIR, f"{ticker}_raw.csv")
        df.to_csv(file_path)
        return df
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

if __name__ == "__main__":
    # Test fetch with config
    fetch_data("AAPL")