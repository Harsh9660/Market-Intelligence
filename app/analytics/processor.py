import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Data', 'data')

def calculate_indicators(df):
    """
    Calculates technical indicators: SMA, RSI, and Volatility.
    """
    if df is None or df.empty:
        return None
    
    # Simple Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Relative Strength Index (RSI)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Volatility (20-day rolling standard deviation)
    df['Volatility'] = df['Close'].rolling(window=20).std()
    
    return df

def process_file(ticker):
    """
    Reads raw data, calculates indicators, and saves processed data.
    """
    raw_path = os.path.join(DATA_DIR, f"{ticker}_raw.csv")
    if not os.path.exists(raw_path):
        print(f"Raw data for {ticker} not found at {raw_path}")
        return False
        
    df = pd.read_csv(raw_path, index_col=0, parse_dates=True)
    df = calculate_indicators(df)
    
    processed_path = os.path.join(DATA_DIR, f"{ticker}_processed.csv")
    df.to_csv(processed_path)
    print(f"Processed data for {ticker} saved to {processed_path}")
    return True

if __name__ == "__main__":
    # Test process
    process_file("AAPL")
