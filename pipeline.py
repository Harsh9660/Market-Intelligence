import sys
import os
from app.analytics.data_fetcher import fetch_stock_data
from app.analytics.processor import process_file

TICKERS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "BTC-USD"]

def run_pipeline(tickers=None):
    """
    Executes the full data pipeline: Fetching -> Processing.
    """
    if tickers is None:
        tickers = TICKERS
        
    print(f"Starting Finance Data Pipeline for: {', '.join(tickers)}")
    
    for ticker in tickers:
        print(f"\n--- Processing {ticker} ---")
        df = fetch_stock_data(ticker)
        if df is not None:
            process_file(ticker)
            
    print("\nPipeline execution completed.")

if __name__ == "__main__":
    run_pipeline()
