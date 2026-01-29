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
                    
    main()
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

API_BASE_URL = "http://localhost:8001/api/v1"

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Market Analysis Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# DATA LAYER
# --------------------------------------------------
@st.cache_data(ttl=60)
def fetch_tickers():
    try:
        r = requests.get(f"{API_BASE_URL}/tickers/", timeout=3)
        return r.json().get("tickers", [])
    except:
        return []

@st.cache_data(ttl=60)
def fetch_market_summary():
    try:
        r = requests.get(f"{API_BASE_URL}/summary/", timeout=3)
        return r.json().get("summary", [])
    except:
        return []

@st.cache_data(ttl=60)
def fetch_data(ticker):
    try:
        r = requests.get(f"{API_BASE_URL}/data/{ticker}/", timeout=3)
        df = pd.DataFrame(r.json().get("data", []))
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])
        return df
    except:
        return pd.DataFrame()

# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
def init_state():
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "Market Pulse"
    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = None

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
def sidebar(tickers):
    with st.sidebar:
        st.markdown("## ⚡ RevenueIQ")
        st.caption("INTELLIGENCE TERMINAL")
        st.markdown("---")

        st.radio(
            "VIEW MODE",
            ["Market Pulse", "Asset Analysis"],
            key="view_mode"
        )

        if st.session_state.view_mode == "Asset Analysis":
            st.session_state.selected_ticker = st.selectbox(
                "ACTIVE ASSET",
                tickers,
                index=0 if not st.session_state.selected_ticker else tickers.index(st.session_state.selected_ticker)
            )

        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

# --------------------------------------------------
# MARKET PULSE VIEW
# --------------------------------------------------
def market_pulse():
    st.title("Market Pulse")
    summary = fetch_market_summary()

    if not summary:
        st.warning("No market data available")
        return

    cols = st.columns(3)
    for i, item in enumerate(summary):
        with cols[i % 3]:
            if st.button(
                f"{item['ticker']}  |  ${item['last_close']:.2f}",
                use_container_width=True
            ):
                st.session_state.selected_ticker = item["ticker"]
                st.session_state.view_mode = "Asset Analysis"
                st.rerun()

# --------------------------------------------------
# ASSET ANALYSIS VIEW
# --------------------------------------------------
def asset_analysis():
    ticker = st.session_state.selected_ticker
    st.title(ticker)

    df = fetch_data(ticker)
    if df.empty:
        st.error("No data for selected asset")
        return

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Price", f"${latest['Close']:.2f}", f"{(latest['Close']/prev['Close']-1)*100:.2f}%")
    c2.metric("RSI", f"{latest.get('RSI',0):.1f}")
    c3.metric("Volatility", f"{latest.get('Volatility',0):.2f}")
    c4.metric("MACD", f"{latest.get('MACD_Signal',0):.3f}")

    # Forecast
    signal = latest.get("Signal_Label", "NEUTRAL")
    score = latest.get("Signal_Score", 0)

    st.subheader("🤖 Forecast")
    st.info(f"Signal: **{signal}** | Confidence: **{score:.2f}/10**")

    # Price Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Price"))
    fig.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig, use_container_width=True)

    # Tabs
    t1, t2 = st.tabs(["Raw Data", "Correlation"])

    with t1:
        st.dataframe(df, use_container_width=True)

    with t2:
        numeric = df.select_dtypes("number")
        corr = numeric.corr()
        fig_corr = px.imshow(corr, aspect="auto", color_continuous_scale="teal")
        st.plotly_chart(fig_corr, use_container_width=True)

# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    init_state()

    tickers = fetch_tickers()
    if not tickers:
        st.error("API Offline")
        return

    sidebar(tickers)

    if st.session_state.view_mode == "Market Pulse":
        market_pulse()
    else:
        asset_analysis()

# --------------------------------------------------
if __name__ == "__main__":
    main()
