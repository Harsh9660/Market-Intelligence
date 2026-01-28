from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Data', 'data')

class TickerListView(APIView):
    """
    Returns a list of available tickers that have processed data.
    """
    def get(self, request):
        if not os.path.exists(DATA_DIR):
            return Response({"tickers": []})
            
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('_processed.csv')]
        tickers = [f.replace('_processed.csv', '') for f in files]
        return Response({"tickers": tickers})

class FinancialDataView(APIView):
    """
    Returns processed financial data for a specific ticker.
    """
    def get(self, request, ticker):
        file_path = os.path.join(DATA_DIR, f"{ticker}_processed.csv")
        
        if not os.path.exists(file_path):
            return Response({"error": f"Data for {ticker} not found."}, status=404)
            
        df = pd.read_csv(file_path)
        # Convert dataframe to JSON
        data = df.to_dict(orient='records')
        return Response({
            "ticker": ticker,
            "count": len(data),
            "data": data
        })

class MarketSummaryView(APIView):
    """
    Returns a brief summary of all available tickers.
    """
    def get(self, request):
        if not os.path.exists(DATA_DIR):
            return Response({"summary": []})
            
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('_processed.csv')]
        summary = []
        
        for f in files:
            ticker = f.replace('_processed.csv', '')
            df = pd.read_csv(os.path.join(DATA_DIR, f))
            if not df.empty:
                last_row = df.iloc[-1]
                summary.append({
                    "ticker": ticker,
                    "last_close": last_row['Close'],
                    "last_rsi": last_row.get('RSI', 'N/A'),
                    "date": str(df.index[-1])
                })
                
        return Response({"summary": summary})

class LiveDataView(APIView):
    """
    Returns the latest available data point for a ticker (Simulation of Live Data).
    """
    def get(self, request, ticker):
        file_path = os.path.join(DATA_DIR, f"{ticker}_processed.csv")
        
        if not os.path.exists(file_path):
            return Response({"error": f"Data for {ticker} not found."}, status=404)
            
        try:
            # Efficiently read just the last few rows
            df = pd.read_csv(file_path)
            if not df.empty:
                latest = df.iloc[-1].to_dict()
                return Response({
                    "ticker": ticker,
                    "timestamp": latest.get('Date', latest.get('Datetime', 'N/A')),
                    "price": latest.get('Close'),
                    "rsi": latest.get('RSI'),
                    "macd": latest.get('MACD'),
                    "signal": latest.get('MACD_Signal'),
                    "bb_upper": latest.get('BB_Upper'),
                    "bb_lower": latest.get('BB_Lower')
                })
        except Exception as e:
            return Response({"error": str(e)}, status=500)
            
        return Response({"error": "No data available"}, status=404)
