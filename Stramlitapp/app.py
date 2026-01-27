import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Market Intelligence Dashboard",
    page_icon="📈",
    layout="wide"
)

def main():
    st.title("📈 Market Intelligence Dashboard")
    st.sidebar.title("Configuration")
    
    st.markdown("""
    Welcome to the **Market Intelligence** dashboard. 
    This is a boilerplate application to verify your project setup.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Overview")
        # Sample data
        df = pd.DataFrame({
            'Category': ['Stocks', 'Bonds', 'Crypto', 'Forex'],
            'Value': [45, 30, 15, 10]
        })
        st.dataframe(df, use_container_width=True)
        
    with col2:
        st.subheader("Market Trends")
        fig = px.pie(df, values='Value', names='Category', title='Asset Allocation')
        st.plotly_chart(fig, use_container_width=True)
    
    st.info("To get started, add your analysis logic in the `app/` directory and update this dashboard in `Stramlitapp/app.py`.")

if __name__ == "__main__":
    main()
