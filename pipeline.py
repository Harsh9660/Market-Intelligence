import sys
import os
import yaml
import time 
from app.analytics.data_fetcher import fetch_data
from app.analytics.processor import process_file

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config', 'pipeline_config.yaml')

def load_config():  # Load configuration from YAML file
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def run_pipeline():
    """
    Executes the advanced finance data pipeline.
    """
    print("\nStarting Market Intelligence Pipeline...")
    config = load_config()
    tickers = config['pipeline']['tickers']
    
    print(f"Configuration: {len(tickers)} Assets | Interval: {config['pipeline']['data']['interval']}")
    
    results = {'success': [], 'failed': []}
    
    for ticker in tickers:
        print(f"\n🔹 Processing {ticker}...")
        try:
            # 1. Fetch
            df = fetch_data(ticker)
            if df is not None:
                # 2. Process
                if process_file(ticker):
                    results['success'].append(ticker)
                else:
                    results['failed'].append(ticker)
            else:
                results['failed'].append(ticker)
                
        except Exception as e:
            print(f"Critical failure on {ticker}: {e}")
            results['failed'].append(ticker)
            
    print("\nPipeline Execution Completed")
    print(f"Success: {len(results['success'])} | Failed: {len(results['failed'])}")
    
    if results['failed']:
        print(f"Failed Assets: {', '.join(results['failed'])}")

if __name__ == "__main__":
    run_pipeline()
