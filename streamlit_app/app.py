import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="RevenueIQ Market Intelligence",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def fetch_tickers():
    try:
        response = requests.get(f"{API_BASE_URL}/tickers/")
        if response.status_code == 200:
            return response.json().get('tickers', [])
    except:
        return []
    return []

def fetch_data(ticker):
    try:
        response = requests.get(f"{API_BASE_URL}/data/{ticker}/")
        if response.status_code == 200:
            return pd.DataFrame(response.json().get('data', []))
    except:
        return None
    return None

def main():
    st.title("💹 Market Intelligence Dashboard")
    st.markdown("---")

    # Sidebar for control
    st.sidebar.header("Navigation")
    tickers = fetch_tickers()
    
    if not tickers:
        st.sidebar.warning("No data found. Please run the pipeline first.")
        if st.sidebar.button("Refresh Data"):
            st.rerun()
        
        st.info("👋 Welcome! It seems the data pipeline hasn't been run yet.")
        st.code("python pipeline.py")
        return

    selected_ticker = st.sidebar.selectbox("Select Asset", tickers)
    
    # Load Data
    with st.spinner(f"Loading data for {selected_ticker}..."):
        df = fetch_data(selected_ticker)

    if df is not None and not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Metrics Row
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2] if len(df) > 1 else last_row
        
        price_diff = last_row['Close'] - prev_row['Close']
        price_pct = (price_diff / prev_row['Close']) * 100
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Last Close", f"${last_row['Close']:,.2f}", f"{price_pct:+.2f}%")
        m2.metric("SMA 20", f"${last_row['SMA_20']:,.2f}")
        m3.metric("RSI (14)", f"{last_row['RSI']:,.1f}")
        m4.metric("Volatility", f"{last_row['Volatility']:,.2f}")

        st.markdown("---")

        # Main Price Chart
        st.subheader(f"{selected_ticker} Price Movement & Indicators")
        
        fig = go.Figure()
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ))
        
        # SMA 20
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['SMA_20'],
            mode='lines', name='SMA 20',
            line=dict(color='orange', width=1.5)
        ))
        
        # SMA 50
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['SMA_50'],
            mode='lines', name='SMA 50',
            line=dict(color='cyan', width=1.5)
        ))

        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=600,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Secondary Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("RSI (Relative Strength Index)")
            fig_rsi = px.line(df, x='Date', y='RSI', title="RSI Trend")
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(template='plotly_dark', height=400)
            st.plotly_chart(fig_rsi, use_container_width=True)
            
        with col2:
            st.subheader("Volatility Trend")
            fig_vol = px.area(df, x='Date', y='Volatility', title="Rolling Volatility")
            fig_vol.update_layout(template='plotly_dark', height=400)
            st.plotly_chart(fig_vol, use_container_width=True)

        # Data Table
        with st.expander("View Raw Analysis Data"):
            st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)

    else:
        st.error(f"Failed to load data for {selected_ticker}")

if __name__ == "__main__":
    main()
