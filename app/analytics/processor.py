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

    df_clean = df.dropna().copy()
    
    # 3. Predictive Signal Engine (Heuristic)
    # -----------------------------------------
    def get_signal(row):
        score = 0
        
        # RSI Logic
        if row['RSI'] < 30: score += 2      # Oversold -> Bullish
        elif row['RSI'] > 70: score -= 2    # Overbought -> Bearish
        elif row['RSI'] < 45: score += 0.5  # Slight Bullish bias
        elif row['RSI'] > 55: score -= 0.5  # Slight Bearish bias
        
        # MACD Logic
        if row['MACD'] > row['MACD_Signal']: score += 1.5
        else: score -= 1.5
        
        # SMA Trend Logic
        if row['Close'] > row['SMA_50']: score += 1
        else: score -= 1
        
        if row['SMA_20'] > row['SMA_50']: score += 1
        else: score -= 1
        
        # Bollinger Bands Logic
        if row['Close'] < row['BB_Lower']: score += 2      # Price below lower band -> Bounce likely
        elif row['Close'] > row['BB_Upper']: score -= 2    # Price above upper band -> Pullback likely
        
        return score

    df_clean['Signal_Score'] = df_clean.apply(get_signal, axis=1)
    
    # Determine Label
    def get_label(score):
        if score >= 3: return "STRONG BUY"
        elif score >= 1: return "BUY"
        elif score <= -3: return "STRONG SELL"
        elif score <= -1: return "SELL"
        else: return "NEUTRAL"
        
    df_clean['Signal_Label'] = df_clean['Signal_Score'].apply(get_label)
    
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
        
        if len(df) < 50: 
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
