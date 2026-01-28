import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Data', 'data')

def fetch_stock_data(ticker, period='1y', interval='1d'):
    """
    Fetches historical stock data using yfinance.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        
        if df.empty:
            print(f"No data found for {ticker}")
            return None
            
        # Ensure the DATA_DIR exists
        os.makedirs(DATA_DIR, exist_ok=True)
        
        file_path = os.path.join(DATA_DIR, f"{ticker}_raw.csv")
        df.to_csv(file_path)
        print(f"Successfully fetched data for {ticker} and saved to {file_path}")
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

if __name__ == "__main__":
    # Test fetch
    fetch_stock_data("AAPL")
