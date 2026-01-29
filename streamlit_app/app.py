import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime

API_BASE_URL = "http://localhost:8001/api/v1"

st.set_page_config(
    page_title="Market Analysis Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 🎨 ULTRA-PREMIUM CSS STYLING ---
st.markdown("""
<style>
    /* VARIABLES */
    :root {
        --bg-color: #050505;
        --card-bg: #111111;
        --accent: #00f2ea;
        --accent-glow: rgba(0, 242, 234, 0.4);
        --text-primary: #ffffff;
        --text-secondary: #888888;
        --pos-green: #00ff7f;
        --neg-red: #ff3333;
    }

    /* GLOBAL RESET */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-primary);
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* HIDE STREAMLIT CHROME */
    header, footer, #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #000; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

    /* TYPOGRAPHY */
    h1, h2, h3 { font-family: 'Outfit', sans-serif; letter-spacing: -0.5px; }
    h1 { font-weight: 800; background: linear-gradient(to right, #fff, #888); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

    /* CARDS & CONTAINERS */
    .st-emotion-cache-1r6slb0 {  /* Streamlit container padding fix */
        padding: 1rem;
    }

    .fin-card {
        background: linear-gradient(145deg, #151515, #0a0a0a);
        border: 1px solid #222;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        position: relative;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .fin-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
        opacity: 0.5;
    }

    .fin-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 242, 234, 0.1);
        border-color: #333;
    }

    /* METRICS */
    .metric-label { font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #fff; margin: 8px 0; letter-spacing: -1px; }
    .metric-delta { font-size: 0.9rem; font-weight: 500; display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; border-radius: 6px; }
    .delta-pos { background: rgba(0, 255, 127, 0.1); color: var(--pos-green); }
    .delta-neg { background: rgba(255, 51, 51, 0.1); color: var(--neg-red); }

    /* ASSET GRID */
    .asset-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 16px; margin: 8px 0;
        background: #0f0f0f; border-radius: 12px;
        border-left: 3px solid transparent;
        transition: 0.2s;
    }
    .asset-row:hover { background: #1a1a1a; border-left-color: var(--accent); cursor: pointer; }
    .symbol-text { font-weight: 800; font-size: 1.1rem; color: #fff; }
    .price-text { font-family: 'JetBrains Mono', monospace; color: var(--accent); }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 40px; white-space: pre-wrap;
        background-color: #111; border-radius: 8px;
        color: #888; border: 1px solid #222; font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #222; color: var(--accent); border-color: var(--accent);
    }

    /* PLOTLY FIXES */
    .js-plotly-plot .plotly .modebar { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- DATA LAYER ---
# @st.cache_data(ttl=60) # Disabled for debugging live updates
def fetch_tickers():
    try:
        response = requests.get(f"{API_BASE_URL}/tickers/", timeout=2)
        return response.json().get('tickers', []) if response.status_code == 200 else []
    except: return []

# @st.cache_data(ttl=60)
def fetch_market_summary():
    try:
        response = requests.get(f"{API_BASE_URL}/summary/", timeout=2)
        return response.json().get('summary', []) if response.status_code == 200 else []
    except: return []

def fetch_data(ticker):
    try:
        response = requests.get(f"{API_BASE_URL}/data/{ticker}/", timeout=2)
        return pd.DataFrame(response.json().get('data', [])) if response.status_code == 200 else None
    except: return None

# --- COMPONENTS ---

def card_metric(label, value, delta=None, prefix="", suffix="", col=None):
    delta_html = ""
    if delta is not None:
        color_cls = "delta-pos" if delta >= 0 else "delta-neg"
        icon = "▲" if delta >= 0 else "▼"
        delta_html = f'<span class="metric-delta {color_cls}">{icon} {abs(delta):.2f}%</span>'
    else:
        # Add a non-visible placeholder to maintain space and alignment
        delta_html = '<span class="metric-delta" style="visibility: hidden;">&nbsp;</span>'
    
    html = f"""
    <div class="fin-card">
        <div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{prefix}{value}{suffix}</div>
        </div>
        {delta_html}
    </div>
    """
    if col: col.markdown(html, unsafe_allow_html=True)
    else: st.markdown(html, unsafe_allow_html=True)

def main():
    """The main function that runs the Streamlit application."""
    tickers = fetch_tickers()

    # SESSION STATE INIT
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "Market Pulse"
    if 'selected_ticker' not in st.session_state:
        st.session_state.selected_ticker = tickers[0] if tickers else ""

    # SIDEBAR
    with st.sidebar:
        st.markdown("## ⚡ RevenueIQ")
        st.caption("INTELLIGENCE TERMINAL")
        st.markdown("---")
        
        # NAVIGATION
        # We use a callback or just update state on change
        mode = st.radio("VIEW MODE", ["Market Pulse", "Asset Analysis"], 
                        index=0 if st.session_state.view_mode == "Market Pulse" else 1,
                        key="nav_radio",
                        on_change=lambda: st.session_state.update(view_mode=st.session_state.nav_radio))
        
        st.markdown("---")
        
        if not tickers:
            st.error("OFFLINE: Run pipeline")
            return
            
        if st.session_state.view_mode == "Asset Analysis":
            idx = tickers.index(st.session_state.selected_ticker) if st.session_state.selected_ticker in tickers else 0
            st.session_state.selected_ticker = st.selectbox("ACTIVE ASSET", tickers, index=idx)
        
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        with button_col2:
            if st.button("🚀 Pipeline", use_container_width=True):
                 st.toast("Triggering Pipeline... (feature coming soon)")

        st.markdown("---")
        st.info(f"Connected: {len(tickers)} Assets")

    # --- VIEW: MARKET PULSE (Dashboard) ---
    if st.session_state.view_mode == "Market Pulse":
        st.title("Market Pulse")
        st.caption("GLOBAL MARKET OVERVIEW")
        
        summary = fetch_market_summary()
        
        if summary:
            # --- QUICK SELECTOR ---
            col_search, col_stats = st.columns([2, 1])
            with col_search:
                quick_ticker = st.selectbox("🔍 QUICK JUMP TO ASSET", ["Select an asset..."] + [item['ticker'] for item in summary])
                
                if quick_ticker != "Select an asset...":
                    st.session_state.selected_ticker = quick_ticker
                    st.session_state.view_mode = "Asset Analysis"
                    st.rerun()
            
            st.markdown("###")
            
            # Create a 3-column grid
            cols = st.columns(3)
            for i, item in enumerate(summary):
                with cols[i % 3]:
                    # Determine color based on RSI or price
                    trend_color = "var(--pos-green)" if item['last_rsi'] > 50 else "var(--neg-red)"
                    
                    st.markdown(f"""
                    <div class="fin-card" style="margin-bottom: 20px; cursor: pointer;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="symbol-text">{item['ticker']}</span>
                            <span class="price-text" style="color:{trend_color}">${item['last_close']:,.2f}</span>
                        </div>
                        <hr style="border-color:#222; margin: 10px 0;">
                        <div style="display:flex; justify-content:space-between; font-size: 0.8rem; color: #888;">
                            <span>RSI: <strong style="color:#fff">{item['last_rsi']:.1f}</strong></span>
                            <span>VOL: <strong style="color:#fff">{item.get('last_volatility', 'N/A')}</strong></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # --- VIEW: ASSET ANALYSIS ---
    elif st.session_state.view_mode == "Asset Analysis":
        ticker = st.session_state.selected_ticker
        
        # Header
        st.title(f"{ticker} Analysis")
        
        # Fetch Data
        df = fetch_data(ticker)
        
        if df is not None and not df.empty:
            # Preprocessing
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
            
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # Metrics
            m1, m2, m3, m4 = st.columns(4)
            
            price_delta = ((latest['close'] - prev['close']) / prev['close']) * 100
            card_metric("Price", f"{latest['close']:,.2f}", price_delta, prefix="$", col=m1)
            
            vol_delta = ((latest['volume'] - prev['volume']) / prev['volume']) * 100 if prev['volume'] > 0 else 0
            card_metric("Volume", f"{latest['volume']:,.0f}", vol_delta, col=m2)
            
            rsi_val = latest.get('rsi', 0)
            card_metric("RSI (14)", f"{rsi_val:.2f}", None, col=m3)
            
            vol_val = latest.get('volatility', 0)
            card_metric("Volatility", f"{vol_val:.4f}", None, col=m4)
            
            st.markdown("###")
            
            # Charts
            tab1, tab2 = st.tabs(["Price Action", "Raw Data"])
            
            with tab1:
                # Candlestick
                fig = go.Figure(data=[go.Candlestick(x=df['date'],
                    open=df['open'], high=df['high'],
                    low=df['low'], close=df['close'], name=ticker)])
                
                fig.update_layout(height=500, template='plotly_dark', 
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                  xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                # RSI Chart if available
                if 'rsi' in df.columns:
                    fig_rsi = px.line(df, x='date', y='rsi', title="RSI Trend")
                    fig_rsi.update_layout(height=250, template='plotly_dark',
                                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                    st.plotly_chart(fig_rsi, use_container_width=True)
            
            with tab2:
                st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)
        else:
            st.warning(f"No data available for {ticker}")

if __name__ == "__main__":
    main()
