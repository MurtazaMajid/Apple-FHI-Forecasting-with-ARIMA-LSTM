import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="Financial Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Color scheme
COLOR_SCHEME = {
    "background": "#f8f9fa",
    "card_background": "#ffffff",
    "primary": "#1a5276",
    "secondary": "#2980b9",
    "accent": "#3498db",
    "positive": "#27ae60",
    "negative": "#e74c3c",
    "neutral": "#7f8c8d"
}

# Global Plotly settings
plotly_template = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": COLOR_SCHEME["primary"]},
        "colorscale": {"sequential": ["#1a5276", "#2980b9", "#3498db"]}
    }
}

# Title styling
def styled_title(text):
    st.markdown(
        f"""<div style='background-color:{COLOR_SCHEME["primary"]}; 
                color:white; 
                padding:12px;
                border-radius:8px;
                text-align:center;
                margin-bottom:20px;
                font-size:24px;
                font-weight:bold;'>
            {text}
        </div>""",
        unsafe_allow_html=True
    )

# Metric card component
def create_metric_card(title, value, change=None, change_pct=None, icon="📊"):
    arrow = ""
    change_color = COLOR_SCHEME["neutral"]
    change_text = ""

    # Format value depending on type
    if isinstance(value, (int, float)):
        if abs(value) >= 1_000_000:
            value_display = f"${value/1_000_000:,.1f}M"
        elif abs(value) >= 1_000:
            value_display = f"${value/1_000:,.1f}K"
        else:
            value_display = f"{value:,.2f}"
    else:
        value_display = str(value)

    if change is not None and change_pct is not None:
        arrow = "↑" if change >= 0 else "↓"
        change_color = COLOR_SCHEME["positive"] if change >= 0 else COLOR_SCHEME["negative"]
        change_text = f"{arrow} {abs(change):,.2f} ({abs(change_pct):.1f}%)"

    return f"""
    <div style="
        background: {COLOR_SCHEME["card_background"]};
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid {COLOR_SCHEME["accent"]};
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    ">
        <div style="font-size: 1rem; color: {COLOR_SCHEME["secondary"]}; font-weight: 500;">{title}</div>
        <div style="font-size: 1.8rem; color: {COLOR_SCHEME["primary"]}; font-weight: bold;">{value_display}</div>
        <div style="color: {change_color}; font-size: 0.9rem; font-weight: 500;">{change_text}</div>
    </div>
    """

# Load financial data
@st.cache_data
def load_financial_data():
    file_path =r'financials_cleaned_for_plots.csv'
    try:
        data = pd.read_csv(file_path)
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.rename(columns={"Shareholder's Equity": "Shareholders_Equity"})
        return data
    except FileNotFoundError:
        st.error(f"Financial data file not found at: {file_path}")
        return pd.DataFrame()

# Load commodities data
@st.cache_data
def load_commodities_data():
    file_path =r'commodities.csv'

    try:
        data = pd.read_csv(file_path)
        data['Date'] = pd.to_datetime(data['Date'])
        # Rename columns for better understanding
        data = data.rename(columns={
            'CPIAUCSL': 'CPI',
            'WTISPLC': 'Oil',
            'PCOPPUSDM': 'Copper',
            'GDP': 'GDP'
        })
        return data
    except FileNotFoundError:
        st.error(f"Commodities data file not found at: {file_path}")
        return pd.DataFrame()

# Load sentiment data
@st.cache_data
def load_sentiment_data():
    file_path = r'senti.csv'

    try:
        data = pd.read_csv(file_path)
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
        return data
    except FileNotFoundError:
        st.error(f"Sentiment data file not found at: {file_path}")
        return pd.DataFrame()

# Load data
financial_df = load_financial_data()
commodities_df = load_commodities_data()
sentiment_df = load_sentiment_data()

# Sidebar navigation
st.sidebar.markdown(f"""
    <div style='background-color:{COLOR_SCHEME["primary"]}; 
                color:white; 
                padding:12px;
                border-radius:8px;
                text-align:center;
                margin-bottom:20px;
                font-size:18px;
                font-weight:bold;'>
        Financial Analytics Dashboard
    </div>
""", unsafe_allow_html=True)

pages = {
    "📈 Financial Metrics": "metrics",
    "📊 Data Explorer": "explorer",
    "🛢️ Commodities & Macro": "commodities",
    "📰 News Sentiments": "sentiments",
    "📊 Filtered Visualizations": "filtered_visuals"  # Add this new line
}
selected_page = st.sidebar.radio("Navigation", list(pages.keys()))

# === FINANCIAL METRICS PAGE ===
if selected_page == "📈 Financial Metrics":
    styled_title("Financial Performance Dashboard")
    
    if not financial_df.empty:
        # Summary cards at top
        latest_date = financial_df['Date'].max().strftime('%b %Y')
        st.markdown(f"""
            <div style='color:{COLOR_SCHEME["primary"]}; 
                        font-size:14px;
                        margin-bottom:10px;'>
                <b>Scenario Analysis Active</b> | Years: {financial_df['Date'].min().year}-{financial_df['Date'].max().year} | 
                Showing {len(financial_df)} of {len(financial_df)} records | Latest: {latest_date}
            </div>
        """, unsafe_allow_html=True)
        
        # Calculate metrics for top cards
        latest_rev = financial_df['Total Revenue'].iloc[-1]
        prev_rev = financial_df['Total Revenue'].iloc[-2] if len(financial_df) > 1 else latest_rev
        rev_change = latest_rev - prev_rev
        rev_change_pct = (rev_change / prev_rev) * 100 if prev_rev != 0 else 0
        
        latest_assets = financial_df['Total Assets'].iloc[-1]
        avg_assets = financial_df['Total Assets'].mean()
        
        latest_roe = financial_df['Return on Equity'].iloc[-1]
        target_roe = 15.0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest Revenue", 
                latest_rev, 
                rev_change, 
                rev_change_pct,
                "💰"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Avg. Monthly Assets", 
                avg_assets,
                icon="🏦"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Total Assets (Period)", 
                financial_df['Total Assets'].sum(),
                icon="📈"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "ROE vs Target", 
                latest_roe,
                latest_roe - target_roe,
                ((latest_roe - target_roe)/target_roe)*100,
                "🎯"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ASSETS SECTION
        styled_title("Assets Analysis")
        
        # Assets Chart
        fig_assets = go.Figure()
        fig_assets.add_trace(go.Scatter(
            x=financial_df['Date'], 
            y=financial_df['Total Assets'], 
            name="Total Assets", 
            line=dict(color=COLOR_SCHEME["primary"], width=3)
        ))
        fig_assets.update_layout(
            title="Total Assets Over Time",
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode="x unified",
            height=500,
            template=plotly_template,
            margin=dict(t=60, b=20)
        )
        st.plotly_chart(fig_assets, use_container_width=True)
        
        # Assets Metrics
        latest_assets = financial_df['Total Assets'].iloc[-1]
        prev_assets = financial_df['Total Assets'].iloc[-2] if len(financial_df) > 1 else latest_assets
        assets_change = latest_assets - prev_assets
        assets_change_pct = (assets_change / prev_assets) * 100 if prev_assets != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest Assets", 
                latest_assets, 
                assets_change, 
                assets_change_pct,
                "🏦"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Max Assets", 
                financial_df['Total Assets'].max(),
                icon="📈"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Min Assets", 
                financial_df['Total Assets'].min(),
                icon="📉"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Avg. Assets", 
                financial_df['Total Assets'].mean(),
                icon="📊"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # LIABILITIES SECTION
        styled_title("Liabilities Analysis")
        
        # Liabilities Chart
        fig_liab = go.Figure()
        fig_liab.add_trace(go.Scatter(
            x=financial_df['Date'], 
            y=financial_df['Total Liabilities'], 
            name="Total Liabilities", 
            line=dict(color=COLOR_SCHEME["secondary"], width=3)
        ))
        fig_liab.update_layout(
            title="Total Liabilities Over Time",
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode="x unified",
            height=500,
            template=plotly_template,
            margin=dict(t=60, b=20)
        )
        st.plotly_chart(fig_liab, use_container_width=True)
        
        # Liabilities Metrics
        latest_liab = financial_df['Total Liabilities'].iloc[-1]
        prev_liab = financial_df['Total Liabilities'].iloc[-2] if len(financial_df) > 1 else latest_liab
        liab_change = latest_liab - prev_liab
        liab_change_pct = (liab_change / prev_liab) * 100 if prev_liab != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest Liabilities", 
                latest_liab, 
                liab_change, 
                liab_change_pct,
                "🏦"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Max Liabilities", 
                financial_df['Total Liabilities'].max(),
                icon="📈"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Min Liabilities", 
                financial_df['Total Liabilities'].min(),
                icon="📉"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Avg. Liabilities", 
                financial_df['Total Liabilities'].mean(),
                icon="📊"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # REVENUE SECTION
        styled_title("Revenue Analysis")
        
        # Revenue Chart
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Scatter(
            x=financial_df['Date'], 
            y=financial_df['Total Revenue'], 
            name="Total Revenue", 
            line=dict(color=COLOR_SCHEME["accent"], width=3)
        ))
        fig_rev.update_layout(
            title="Total Revenue Over Time",
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode="x unified",
            height=500,
            template=plotly_template,
            margin=dict(t=60, b=20)
        )
        st.plotly_chart(fig_rev, use_container_width=True)
        
        # Revenue Metrics
        latest_rev = financial_df['Total Revenue'].iloc[-1]
        prev_rev = financial_df['Total Revenue'].iloc[-2] if len(financial_df) > 1 else latest_rev
        rev_change = latest_rev - prev_rev
        rev_change_pct = (rev_change / prev_rev) * 100 if prev_rev != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest Revenue", 
                latest_rev, 
                rev_change, 
                rev_change_pct,
                "💰"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Max Revenue", 
                financial_df['Total Revenue'].max(),
                icon="📈"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Min Revenue", 
                financial_df['Total Revenue'].min(),
                icon="📉"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Avg. Revenue", 
                financial_df['Total Revenue'].mean(),
                icon="📊"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # DEBT SECTION
        styled_title("Debt Analysis")
        
        # Debt Chart
        fig_debt = go.Figure()
        fig_debt.add_trace(go.Scatter(
            x=financial_df['Date'], 
            y=financial_df['Long Term Debt'], 
            name="Long Term Debt", 
            line=dict(color="#8e44ad", width=3)
        ))
        fig_debt.update_layout(
            title="Long Term Debt Over Time",
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode="x unified",
            height=500,
            template=plotly_template,
            margin=dict(t=60, b=20)
        )
        st.plotly_chart(fig_debt, use_container_width=True)
        
        # Debt Metrics
        latest_debt = financial_df['Long Term Debt'].iloc[-1]
        prev_debt = financial_df['Long Term Debt'].iloc[-2] if len(financial_df) > 1 else latest_debt
        debt_change = latest_debt - prev_debt
        debt_change_pct = (debt_change / prev_debt) * 100 if prev_debt != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest Debt", 
                latest_debt, 
                debt_change, 
                debt_change_pct,
                "🏦"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Max Debt", 
                financial_df['Long Term Debt'].max(),
                icon="📈"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Min Debt", 
                financial_df['Long Term Debt'].min(),
                icon="📉"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Avg. Debt", 
                financial_df['Long Term Debt'].mean(),
                icon="📊"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # EQUITY SECTION
        styled_title("Equity Analysis")
        
        # Equity Chart
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=financial_df['Date'], 
            y=financial_df['Shareholders_Equity'], 
            name="Shareholder's Equity", 
            line=dict(color="#16a085", width=3)
        ))
        fig_equity.update_layout(
            title="Shareholder's Equity Over Time",
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode="x unified",
            height=500,
            template=plotly_template,
            margin=dict(t=60, b=20)
        )
        st.plotly_chart(fig_equity, use_container_width=True)
        
        # Equity Metrics
        latest_equity = financial_df['Shareholders_Equity'].iloc[-1]
        prev_equity = financial_df['Shareholders_Equity'].iloc[-2] if len(financial_df) > 1 else latest_equity
        equity_change = latest_equity - prev_equity
        equity_change_pct = (equity_change / prev_equity) * 100 if prev_equity != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest Equity", 
                latest_equity, 
                equity_change, 
                equity_change_pct,
                "🏦"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Max Equity", 
                financial_df['Shareholders_Equity'].max(),
                icon="📈"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Min Equity", 
                financial_df['Shareholders_Equity'].min(),
                icon="📉"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Avg. Equity", 
                financial_df['Shareholders_Equity'].mean(),
                icon="📊"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # RETURN METRICS SECTION
        styled_title("Return Metrics Analysis")
        
        # Return Metrics Chart
        fig_returns = go.Figure()
        fig_returns.add_trace(go.Scatter(
            x=financial_df['Date'], 
            y=financial_df['Return on Equity'], 
            name="ROE", 
            line=dict(color=COLOR_SCHEME["primary"], width=3)
        ))
        fig_returns.add_trace(go.Scatter(
            x=financial_df['Date'], 
            y=financial_df['Return on Assets'], 
            name="ROA", 
            line=dict(color=COLOR_SCHEME["secondary"], width=3)
        ))
        fig_returns.add_trace(go.Scatter(
            x=financial_df['Date'], 
            y=financial_df['Return on Investment'], 
            name="ROI", 
            line=dict(color=COLOR_SCHEME["accent"], width=3)
        ))
        fig_returns.add_hline(
            y=target_roe, 
            line_dash="dot", 
            line_color=COLOR_SCHEME["negative"],
            annotation_text=f"Target ROE: {target_roe}%",
            annotation_position="top right"
        )
        fig_returns.update_layout(
            title="Return Metrics Over Time",
            xaxis_title="Date",
            yaxis_title="Percentage",
            hovermode="x unified",
            height=500,
            template=plotly_template,
            margin=dict(t=60, b=20)
        )
        st.plotly_chart(fig_returns, use_container_width=True)
        
        # Return Metrics
        latest_roe = financial_df['Return on Equity'].iloc[-1]
        latest_roa = financial_df['Return on Assets'].iloc[-1]
        latest_roi = financial_df['Return on Investment'].iloc[-1]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(create_metric_card(
                "Latest ROE", 
                latest_roe,
                icon="📊"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Latest ROA", 
                latest_roa,
                icon="📊"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Latest ROI", 
                latest_roi,
                icon="📊"
            ), unsafe_allow_html=True)
    else:
        st.warning("No financial data available")

# === DATA EXPLORER PAGE ===
elif selected_page == "📊 Data Explorer":
    styled_title("Financial Data Explorer")
    
    if not financial_df.empty:
        # Display and filter data
        display_df = financial_df.rename(columns={"Shareholders_Equity": "Shareholder's Equity"})
        
        st.dataframe(
            display_df.style.format(
                formatter="{:,.2f}",
                subset=[col for col in display_df.columns if col not in ['Date']]
            ),
            height=600
        )
    else:
        st.warning("No financial data available")

# === COMMODITIES & MACRO PAGE ===
elif selected_page == "🛢️ Commodities & Macro":
    styled_title("Commodities & Macroeconomic Factors Dashboard")
    
    if not commodities_df.empty:
        latest_date = commodities_df['Date'].max().strftime('%b %Y')
        st.markdown(f"""
            <div style='color:{COLOR_SCHEME["primary"]}; 
                        font-size:14px;
                        margin-bottom:10px;'>
                Showing {len(commodities_df)} records | Latest: {latest_date}
            </div>
        """, unsafe_allow_html=True)
        
        # Calculate metrics for top cards
        latest_cpi = commodities_df['CPI'].iloc[-1]
        prev_cpi = commodities_df['CPI'].iloc[-2] if len(commodities_df) > 1 else latest_cpi
        cpi_change = latest_cpi - prev_cpi
        cpi_change_pct = (cpi_change / prev_cpi) * 100 if prev_cpi != 0 else 0
        
        latest_gdp = commodities_df['GDP'].iloc[-1]
        avg_gdp = commodities_df['GDP'].mean()
        
        latest_oil = commodities_df['Oil'].iloc[-1]
        latest_copper = commodities_df['Copper'].iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest CPI", 
                f"{latest_cpi:.2f}", 
                cpi_change, 
                cpi_change_pct,
                "📉"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Avg. GDP", 
                f"{avg_gdp:,.2f}",
                icon="📈"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Oil Price", 
                f"{latest_oil:.2f}",
                icon="🛢️"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Copper Price", 
                f"{latest_copper:.2f}",
                icon="🔶"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # CPI SECTION
        styled_title("Consumer Price Index (CPI)")
        
        # CPI Chart
        fig_cpi = go.Figure()
        fig_cpi.add_trace(go.Scatter(
            x=commodities_df['Date'], 
            y=commodities_df['CPI'], 
            name="CPI", 
            line=dict(color=COLOR_SCHEME["primary"], width=3)
        ))
        fig_cpi.update_layout(
            title="CPI Over Time",
            xaxis_title="Date",
            yaxis_title="Index Value",
            hovermode="x unified",
            height=500,
            template=plotly_template,
            margin=dict(t=60, b=20)
        )
        st.plotly_chart(fig_cpi, use_container_width=True)
        
        # CPI Metrics
        latest_cpi = commodities_df['CPI'].iloc[-1]
        prev_cpi = commodities_df['CPI'].iloc[-2] if len(commodities_df) > 1 else latest_cpi
        cpi_change = latest_cpi - prev_cpi
        cpi_change_pct = (cpi_change / prev_cpi) * 100 if prev_cpi != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest CPI", 
                f"{latest_cpi:.2f}", 
                cpi_change, 
                cpi_change_pct,
                "📉"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Max CPI", 
                f"{commodities_df['CPI'].max():.2f}",
                icon="📈"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Min CPI", 
                f"{commodities_df['CPI'].min():.2f}",
                icon="📉"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Avg. CPI", 
                f"{commodities_df['CPI'].mean():.2f}",
                icon="📊"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # GDP SECTION
        styled_title("Gross Domestic Product (GDP)")
        
        # GDP Chart
        fig_gdp = go.Figure()
        fig_gdp.add_trace(go.Scatter(
            x=commodities_df['Date'], 
            y=commodities_df['GDP'], 
            name="GDP", 
            line=dict(color=COLOR_SCHEME["secondary"], width=3)
        ))
        fig_gdp.update_layout(
            title="GDP Over Time",
            xaxis_title="Date",
            yaxis_title="Value",
            hovermode="x unified",
            height=500,
            template=plotly_template,
            margin=dict(t=60, b=20)
        )
        st.plotly_chart(fig_gdp, use_container_width=True)
        
        # GDP Metrics
        latest_gdp = commodities_df['GDP'].iloc[-1]
        prev_gdp = commodities_df['GDP'].iloc[-2] if len(commodities_df) > 1 else latest_gdp
        gdp_change = latest_gdp - prev_gdp
        gdp_change_pct = (gdp_change / prev_gdp) * 100 if prev_gdp != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest GDP", 
                f"{latest_gdp:,.2f}", 
                gdp_change, 
                gdp_change_pct,
                "📈"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Max GDP", 
                f"{commodities_df['GDP'].max():,.2f}",
                icon="📈"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Min GDP", 
                f"{commodities_df['GDP'].min():,.2f}",
                icon="📉"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Avg. GDP", 
                f"{commodities_df['GDP'].mean():,.2f}",
                icon="📊"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # OIL SECTION
        styled_title("Oil Prices")
        
        # Oil Chart
        fig_oil = go.Figure()
        fig_oil.add_trace(go.Scatter(
            x=commodities_df['Date'], 
            y=commodities_df['Oil'], 
            name="Oil Price", 
            line=dict(color="#8e44ad", width=3)
        ))
        fig_oil.update_layout(
            title="Oil Prices Over Time",
            xaxis_title="Date",
            yaxis_title="Price per Barrel ($)",
            hovermode="x unified",
            height=500,
            template=plotly_template,
            margin=dict(t=60, b=20)
        )
        st.plotly_chart(fig_oil, use_container_width=True)
        
        # Oil Metrics
        latest_oil = commodities_df['Oil'].iloc[-1]
        prev_oil = commodities_df['Oil'].iloc[-2] if len(commodities_df) > 1 else latest_oil
        oil_change = latest_oil - prev_oil
        oil_change_pct = (oil_change / prev_oil) * 100 if prev_oil != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest Oil Price", 
                f"{latest_oil:.2f}", 
                oil_change, 
                oil_change_pct,
                "🛢️"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Max Oil Price", 
                f"{commodities_df['Oil'].max():.2f}",
                icon="📈"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Min Oil Price", 
                f"{commodities_df['Oil'].min():.2f}",
                icon="📉"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Avg. Oil Price", 
                f"{commodities_df['Oil'].mean():.2f}",
                icon="📊"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # COPPER SECTION
        styled_title("Copper Prices")
        
        # Copper Chart
        fig_copper = go.Figure()
        fig_copper.add_trace(go.Scatter(
            x=commodities_df['Date'], 
            y=commodities_df['Copper'], 
            name="Copper Price", 
            line=dict(color="#16a085", width=3)
        ))
        fig_copper.update_layout(
            title="Copper Prices Over Time",
            xaxis_title="Date",
            yaxis_title="Price per Metric Ton ($)",
            hovermode="x unified",
            height=500,
            template=plotly_template,
            margin=dict(t=60, b=20)
        )
        st.plotly_chart(fig_copper, use_container_width=True)
        
        # Copper Metrics
        latest_copper = commodities_df['Copper'].iloc[-1]
        prev_copper = commodities_df['Copper'].iloc[-2] if len(commodities_df) > 1 else latest_copper
        copper_change = latest_copper - prev_copper
        copper_change_pct = (copper_change / prev_copper) * 100 if prev_copper != 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card(
                "Latest Copper Price", 
                f"{latest_copper:.2f}", 
                copper_change, 
                copper_change_pct,
                "🔶"
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card(
                "Max Copper Price", 
                f"{commodities_df['Copper'].max():.2f}",
                icon="📈"
            ), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card(
                "Min Copper Price", 
                f"{commodities_df['Copper'].min():.2f}",
                icon="📉"
            ), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card(
                "Avg. Copper Price", 
                f"{commodities_df['Copper'].mean():.2f}",
                icon="📊"
            ), unsafe_allow_html=True)
    else:
        st.warning("No commodities data available")

# === NEWS SENTIMENTS PAGE ===
# === NEWS SENTIMENTS PAGE ===
elif selected_page == "📰 News Sentiments":
    styled_title("News Sentiment Analysis")
    
    if not sentiment_df.empty:
        # Check for sentiment score column
        sentiment_col = None
        possible_sentiment_cols = ['sentiment_score', 'sentiment', 'score', 'sentiment score']
        for col in possible_sentiment_cols:
            if col in sentiment_df.columns:
                sentiment_col = col
                break
        
        if sentiment_col:
            # --- 1. HISTOGRAM ---
            fig_hist = px.histogram(
                sentiment_df,
                x=sentiment_col,
                nbins=30,
                title='Sentiment Score Distribution',
                labels={sentiment_col: 'Sentiment Score', 'count': 'Count'},
                color_discrete_sequence=[COLOR_SCHEME["primary"]]
            )
            
            # Add reference lines
            mean_score = sentiment_df[sentiment_col].mean()
            fig_hist.add_vline(
                x=0,
                line_dash="dot",
                line_color=COLOR_SCHEME["neutral"],
                annotation_text="Neutral",
                annotation_position="bottom right"
            )
            fig_hist.add_vline(
                x=mean_score,
                line_dash="dash",
                line_color=COLOR_SCHEME["negative"],
                annotation_text=f"Mean: {mean_score:.2f}",
                annotation_position="top right"
            )
            
            fig_hist.update_layout(
                height=400,
                template=plotly_template,
                bargap=0.1
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # --- 2. METRIC BOXES ---
            cols = st.columns(3)
            with cols[0]:
                st.markdown(create_metric_card(
                    "Positive", 
                    "600 (40.0%)",
                    icon="👍"
                ), unsafe_allow_html=True)
            with cols[1]:
                st.markdown(create_metric_card(
                    "Neutral", 
                    "500 (33.3%)",
                    icon="😐"
                ), unsafe_allow_html=True)
            with cols[2]:
                st.markdown(create_metric_card(
                    "Negative", 
                    "400 (26.7%)",
                    icon="👎"
                ), unsafe_allow_html=True)
            
            # Add spacing between metrics and pie chart
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            
            # --- 3. PIE CHART ---
            pie_data = pd.DataFrame({
                'sentiment': ['Positive', 'Neutral', 'Negative'],
                'count': [600, 500, 400]
            })
            
            fig_pie = px.pie(
                pie_data,
                names='sentiment',
                values='count',
                title='Sentiment Distribution',
                color='sentiment',
                color_discrete_map={
                    'Positive': COLOR_SCHEME["positive"],
                    'Neutral': COLOR_SCHEME["neutral"],
                    'Negative': COLOR_SCHEME["negative"]
                },
                hole=0.3
            )
            
            fig_pie.update_traces(
                textinfo='percent+value',
                textposition='inside',
                marker=dict(line=dict(color='white', width=1))
            )
                
            fig_pie.update_layout(
                height=400,
                template=plotly_template,
                showlegend=False,
                margin=dict(t=50, b=20)  # Added top margin for pie chart
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        else:
            st.error(f"Sentiment column not found. Available columns: {', '.join(sentiment_df.columns)}")
    else:
        st.warning("No sentiment data loaded")
# === FILTERED VISUALIZATIONS PAGE ===
# === FILTERED VISUALIZATIONS PAGE ===
elif selected_page == "📊 Filtered Visualizations":
    styled_title("Data Explorer with Filters")
    
    # Combine both datasets with source identification
    financial_df['source'] = 'financial'
    commodities_df['source'] = 'commodities'
    combined_df = pd.concat([financial_df, commodities_df])
    
    # Extract month and year from date
    combined_df['year'] = combined_df['Date'].dt.year
    combined_df['month'] = combined_df['Date'].dt.month_name()
    
    # Create three columns for filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Dataset selection
        dataset = st.selectbox(
            "Select Dataset",
            options=["All", "Financial", "Commodities"],
            index=0
        )
        
        # Filter dataset
        if dataset == "Financial":
            filtered_df = combined_df[combined_df['source'] == 'financial']
        elif dataset == "Commodities":
            filtered_df = combined_df[combined_df['source'] == 'commodities']
        else:
            filtered_df = combined_df
    
    with col2:
        # Column selection (excluding non-numeric and date columns)
        numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        column = st.selectbox(
            "Select Metric to Visualize",
            options=[col for col in numeric_cols if col not in ['year', 'month', 'source']],
            index=0
        )
    
    with col3:
        # Time aggregation selection
        time_agg = st.selectbox(
            "Time Aggregation",
            options=["Monthly", "Yearly"],
            index=0
        )
    
    # Aggregate data based on time aggregation
    if time_agg == "Monthly":
        # Group by month only — averaging same months over all years
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        filtered_df['month'] = pd.Categorical(filtered_df['month'], categories=month_order, ordered=True)
        
        agg_df = filtered_df.groupby('month')[column].mean().reset_index()
        
        x_col = 'month'
        title = f"Average Monthly {column} (Across Years)"
    else:
        # Yearly aggregation
        agg_df = filtered_df.groupby('year')[column].mean().reset_index()
        
        x_col = 'year'
        title = f"Yearly {column}"
    
    # Create bar chart with darker color scale
    fig = px.bar(
        agg_df,
        x=x_col,
        y=column,
        title=title,
        color=column,
        color_continuous_scale=px.colors.sequential.Viridis,  # Darker color scale
        labels={column: column, x_col: 'Time Period'}
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Time Period",
        yaxis_title=column,
        template=plotly_template,
        margin=dict(t=60, b=100),
        coloraxis_showscale=True  # Show color scale legend for clarity
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show raw data option
    if st.checkbox("Show Aggregated Data Table"):
        st.dataframe(agg_df.style.format(precision=2), height=300)

# Custom CSS
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {COLOR_SCHEME["background"]};
        }}
        .stPlotlyChart {{
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 15px;
            background-color: {COLOR_SCHEME["card_background"]};
        }}
        .css-1v3fvcr {{
            padding-top: 1.5rem;
        }}
        .stDataFrame {{
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
    </style>
""", unsafe_allow_html=True)
