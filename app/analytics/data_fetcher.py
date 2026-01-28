import yfinance as yf
from datetime import datetime

def fetch_data(ticker, start_date, end_date):
    """
    Fetches historical market data from Yahoo Finance.
    """
    return yf.download(ticker, start=start_date, end=end_date)