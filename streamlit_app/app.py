import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime

# --- CONFIGURATION & PAGE SETUP ---
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
@st.cache_data(ttl=60)
def fetch_tickers():
    try:
        response = requests.get(f"{API_BASE_URL}/tickers/", timeout=2)
        return response.json().get('tickers', []) if response.status_code == 200 else []
    except: return []

@st.cache_data(ttl=60)
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

# --- MAIN APP ---

def main():
    # SIDEBAR
    with st.sidebar:
        st.markdown("## ⚡ RevenueIQ")
        st.caption("INTELLIGENCE TERMINAL")
        st.markdown("---")
        
        tickers = fetch_tickers()
        if not tickers:
            st.error("OFFLINE: Run pipeline")
            return
            
        selected_ticker = st.selectbox("ACTIVE ASSET", tickers, index=0)
        
        st.markdown("### ⚙️ CONTROLS")
        refresh = st.button("Reconnect Stream", use_container_width=True)
        if refresh: st.cache_data.clear()

        st.markdown("---")
        st.info(f"Connected: {len(tickers)} Assets")

    # HEADER AREA
    col_logo, col_kpi = st.columns([1, 3])
    with col_logo:
        st.title(selected_ticker)
        st.caption("REAL-TIME MARKET DATA")
    
    # DATA LOADING
    df = fetch_data(selected_ticker)
    
    if df is not None:
        # Standardize Date Column
        if 'Datetime' in df.columns:
            df.rename(columns={'Datetime': 'Date'}, inplace=True)
        
        # Ensure Date is datetime object
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        price_ret = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
        
        # --- TOP METRIC ROW ---
        m1, m2, m3, m4 = st.columns(4)
        card_metric("Market Price", f"{latest['Close']:,.2f}", price_ret, "$", "", m1)
        card_metric("RSI Momentum", f"{latest['RSI']:.1f}", (latest['RSI']-prev['RSI']), "", "", m2)
        card_metric("Volatility (Std)", f"{latest['Volatility']:.2f}", None, "", "", m3)
        card_metric("MACD Signal", f"{latest['MACD_Signal']:.3f}", None, "", "", m4)
        
        st.markdown("###") 
        
        c_main, c_side = st.columns([3, 1])
        
        with c_main:
            st.markdown('<div class="fin-card">', unsafe_allow_html=True)
            
            # Sophisticated Chart
            fig = go.Figure()
            
            # Gradient Fill for Price
            fig.add_trace(go.Scatter(
                x=df['Date'], y=df['Close'],
                mode='lines',
                line=dict(color='#00f2ea', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 242, 234, 0.05)',
                name='Price'
            ))
            
            # BB Bands with subtle style
            fig.add_trace(go.Scatter(
                x=df['Date'], y=df['BB_Upper'],
                line=dict(color='rgba(255,255,255,0.1)', width=1),
                name='Upper BB', hoverinfo='skip'
            ))
            fig.add_trace(go.Scatter(
                x=df['Date'], y=df['BB_Lower'],
                line=dict(color='rgba(255,255,255,0.1)', width=1),
                fill='tonexty', fillcolor='rgba(255,255,255,0.02)',
                name='Lower BB', hoverinfo='skip'
            ))
            
            # Layout Polish
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=450,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(showgrid=False, showline=False, zeroline=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c_side:
            # RSI Gauge
            st.markdown('<div class="fin-card" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown(f"**RSI STRENGTH**")
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = latest['RSI'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [0, 100], 'tickcolor': "#333"},
                    'bar': {'color': "#00f2ea"},
                    'bgcolor': "#111",
                    'steps': [
                        {'range': [0, 30], 'color': "rgba(0, 255, 127, 0.2)"},
                        {'range': [70, 100], 'color': "rgba(255, 51, 51, 0.2)"}
                    ],
                }
            ))
            fig_gauge.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#fff"})
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Trend Text
            trend = "BULLISH" if latest['Close'] > latest['SMA_50'] else "BEARISH"
            trend_col = "#00ff7f" if trend == "BULLISH" else "#ff3333"
            
            st.markdown(f"""
            <div style="text-align: center; margin-top: 10px;">
                <div style="font-size: 12px; color: #888;">MARKET REGIME</div>
                <div style="font-size: 24px; font-weight: 800; color: {trend_col}; letter-spacing: 2px;">{trend}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        # --- TABS SECTION ---
        st.markdown("###")
        t1, t2, t3 = st.tabs(["📊 RAW DATA LAKE", "🌊 FEATURE CORRELATION", "📡 MARKET PULSE"])
        
        with t1:
            st.markdown('<div class="fin-card">', unsafe_allow_html=True)
            st.dataframe(
                df.sort_values('Date', ascending=False), 
                use_container_width=True, 
                height=300,
                column_config={
                    "Date": st.column_config.DatetimeColumn("Timestamp", format="D MMM, HH:mm"),
                    "Close": st.column_config.NumberColumn("Price", format="$%.2f"),
                    "Volume": st.column_config.NumberColumn("Vol", format="%d")
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with t2:
            st.markdown('<div class="fin-card">', unsafe_allow_html=True)
            numeric = df.select_dtypes(include=['float64']).drop(columns=['Open','High','Low','Close'], errors='ignore')
            corr = numeric.corr()
            fig_corr = px.imshow(corr, color_continuous_scale='Tealgrn', aspect="auto")
            fig_corr.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_corr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with t3:
             # Simulated Pulse/News
             st.markdown("""
             <div class="fin-card">
                 <div style="font-family: monospace; color: #00f2ea;"> SYSTEM STATUS: ONLINE 🟢</div>
                 <br>
                 <div class="asset-row">
                    <span class="symbol-text">DATA PIPELINE</span>
                    <span class="price-text" style="color:#00ff7f">ACTIVE (1m LATENCY)</span>
                 </div>
                 <div class="asset-row">
                    <span class="symbol-text">API GATEWAY</span>
                    <span class="price-text" style="color:#00ff7f">HEALTHY (2ms)</span>
                 </div>
                 <div class="asset-row">
                    <span class="symbol-text">ML INFERENCE</span>
                    <span class="price-text" style="color:#ffcc00">STANDBY</span>
                 </div>
             </div>
             """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
