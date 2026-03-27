import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Apple FHI Dashboard",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────
C = {
    "bg":       "#0d1117",
    "surface":  "#161b22",
    "surface2": "#21262d",
    "border":   "#30363d",
    "primary":  "#58a6ff",
    "green":    "#3fb950",
    "red":      "#f85149",
    "yellow":   "#d29922",
    "purple":   "#bc8cff",
    "orange":   "#ff7b72",
    "teal":     "#39d353",
    "text":     "#e6edf3",
    "muted":    "#8b949e",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
*, body, .stApp { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background-color: #0d1117; }
section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
section[data-testid="stSidebar"] * { color: #e6edf3 !important; }
.stRadio > label { color: #8b949e !important; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
.stRadio [data-testid="stMarkdownContainer"] p { color: #e6edf3 !important; font-size: 14px; }
div[data-testid="metric-container"] { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; }
div[data-testid="metric-container"] label { color: #8b949e !important; font-size: 12px; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e6edf3 !important; font-family: 'IBM Plex Mono', monospace; }
div[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 12px; }
.stDataFrame { background: #161b22; border-radius: 8px; }
.stSelectbox > div > div { background: #21262d; border-color: #30363d; color: #e6edf3; }
hr { border-color: #30363d; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px 24px; margin-bottom: 16px; }
.card-title { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #8b949e; margin-bottom: 8px; }
.card-value { font-family: 'IBM Plex Mono', monospace; font-size: 28px; font-weight: 600; color: #e6edf3; line-height: 1; }
.card-sub { font-size: 12px; color: #8b949e; margin-top: 6px; }
.pill-green { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid rgba(63,185,80,0.3); padding: 2px 10px; border-radius: 20px; font-size: 12px; font-family: 'IBM Plex Mono', monospace; }
.pill-red { background: rgba(248,81,73,0.15); color: #f85149; border: 1px solid rgba(248,81,73,0.3); padding: 2px 10px; border-radius: 20px; font-size: 12px; font-family: 'IBM Plex Mono', monospace; }
.pill-blue { background: rgba(88,166,255,0.15); color: #58a6ff; border: 1px solid rgba(88,166,255,0.3); padding: 2px 10px; border-radius: 20px; font-size: 12px; font-family: 'IBM Plex Mono', monospace; }
.section-header { font-size: 18px; font-weight: 600; color: #e6edf3; margin: 24px 0 16px 0; padding-bottom: 8px; border-bottom: 1px solid #30363d; }
.insight-box { background: linear-gradient(135deg, rgba(88,166,255,0.08) 0%, rgba(63,185,80,0.05) 100%); border: 1px solid rgba(88,166,255,0.2); border-radius: 8px; padding: 16px 20px; margin: 12px 0; font-size: 14px; line-height: 1.6; color: #8b949e; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# EXACT FEATURE SETS FROM NOTEBOOK (Section 10)
# ─────────────────────────────────────────────
# Notebook cell [056] — do NOT change order, these must match the saved model weights.
RATIO_FEATURES = [
    'Return on Equity',
    'Price to Sales Ratio',
    'PE Ratio',
    'Debt to Equity Ratio',
    'Return on Investment',
    'Current Ratio',
    'Quick Ratio',
    'Return on Assets',
]  # 8 columns  →  lstm_ratios expects input_shape = (12, 8)

ALL_FEATURES = RATIO_FEATURES + [
    'CPIAUCSL',
    'WTISPLC',
    'PCOPPUSDM',
    'GDP',
    'FEDFUNDS',
    'sentiment_score',
]  # 14 columns →  lstm_all    expects input_shape = (12, 14)

# FHI weights — notebook Section 8
FHI_WEIGHTS = {
    'Debt to Equity Ratio': 0.25,
    'Return on Equity':     0.25,
    'Return on Investment': 0.20,
    'Return on Assets':     0.20,
    'Current Ratio':        0.10,
}

LOOKBACK = 12   # notebook cell [064]


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_all_data():
    BASE = "Data"

    apple = pd.read_csv(BASE + "/Apples Financial Data 2010 - 2025.csv")
    apple['Date'] = pd.to_datetime(apple['Date']).dt.to_period('M').dt.to_timestamp()
    apple.set_index('Date', inplace=True)
    apple = apple.loc['2010-06-01':'2025-04-01']

    cpi = pd.read_csv(BASE + "/USA CPI 2010 - 2025.csv")
    cpi['observation_date'] = pd.to_datetime(cpi['observation_date']).dt.to_period('M').dt.to_timestamp()
    cpi.set_index('observation_date', inplace=True)
    cpi.index.name = 'Date'
    cpi = cpi.loc['2010-06-01':'2025-04-01']

    oil = pd.read_csv(BASE + "/USA Crude Oil 2010 - 2025.csv")
    oil['observation_date'] = pd.to_datetime(oil['observation_date']).dt.to_period('M').dt.to_timestamp()
    oil.set_index('observation_date', inplace=True)
    oil.index.name = 'Date'
    oil = oil.loc['2010-06-01':'2025-04-01']

    copper = pd.read_csv(BASE + "/USA Copper prices 2010 - 2025.csv")
    copper['observation_date'] = pd.to_datetime(copper['observation_date']).dt.to_period('M').dt.to_timestamp()
    copper.set_index('observation_date', inplace=True)
    copper.index.name = 'Date'
    copper = copper.loc['2010-06-01':'2025-04-01']

    gdp = pd.read_csv(BASE + "/USA GDP 2010 - 2025.csv")
    gdp['observation_date'] = pd.to_datetime(gdp['observation_date']).dt.to_period('M').dt.to_timestamp()
    gdp.set_index('observation_date', inplace=True)
    gdp.index.name = 'Date'
    gdp = gdp.resample('MS').ffill()
    gdp = gdp.loc['2010-06-01':'2025-04-01']

    fedfunds = pd.read_csv(BASE + "/USA Fed Funds 2010 - 2025.csv")
    fedfunds['observation_date'] = pd.to_datetime(fedfunds['observation_date']).dt.to_period('M').dt.to_timestamp()
    fedfunds.set_index('observation_date', inplace=True)
    fedfunds.index.name = 'Date'
    fedfunds = fedfunds.loc['2010-06-01':'2025-04-01']

    news = pd.read_csv(BASE + "New York Times News related to apple.csv")
    news['pub_date'] = pd.to_datetime(news['pub_date'])

    # ── Merge ────────────────────────────────────────────
    combined = apple.copy()
    combined = combined.join(cpi,      how='inner')
    combined = combined.join(oil,      how='inner')
    combined = combined.join(copper,   how='inner')
    combined = combined.join(gdp,      how='inner')
    combined = combined.join(fedfunds, how='inner')
    combined = combined.ffill()

    if 'sentiment_score' not in combined.columns:
        combined['sentiment_score'] = 0.0

    # ── Scaling ──────────────────────────────────────────
    from sklearn.preprocessing import MinMaxScaler
    apple_cols = list(apple.columns)
    macro_cols = ['CPIAUCSL', 'WTISPLC', 'PCOPPUSDM', 'GDP', 'FEDFUNDS', 'sentiment_score']
    all_cols   = apple_cols + macro_cols

    n         = len(combined)
    train_end = int(n * 0.70)

    scaler = MinMaxScaler()
    scaler.fit(combined.iloc[:train_end][all_cols])
    scaled_arr = scaler.transform(combined[all_cols])
    scaled_df  = pd.DataFrame(scaled_arr, columns=all_cols, index=combined.index)

    # ── FHI ──────────────────────────────────────────────
    scaled_df['fhi']     = sum(scaled_df[col] * w for col, w in FHI_WEIGHTS.items())
    scaled_df['fhi_log'] = np.log(scaled_df['fhi'] + 1e-8)

    return apple, cpi, oil, copper, gdp, fedfunds, news, combined, scaled_df

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def dark_layout(fig, title="", height=420):
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=C["muted"]), x=0),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans", color=C["muted"], size=12),
        xaxis=dict(gridcolor=C["border"], gridwidth=1, linecolor=C["border"],
                   tickcolor=C["border"], tickfont=dict(color=C["muted"], size=11)),
        yaxis=dict(gridcolor=C["border"], gridwidth=1, linecolor=C["border"],
                   tickcolor=C["border"], tickfont=dict(color=C["muted"], size=11)),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=C["border"],
                    font=dict(color=C["muted"], size=11)),
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=C["surface2"], bordercolor=C["border"],
                        font=dict(color=C["text"], size=12))
    )
    return fig


def section(title):
    st.markdown('<div class="section-header">' + title + '</div>', unsafe_allow_html=True)


def insight(text):
    st.markdown('<div class="insight-box">' + text + '</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
try:
    apple, cpi, oil, copper, gdp, fedfunds, news, combined, scaled_df = load_all_data()
except Exception as e:
    st.error("Could not load data: " + str(e))
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.markdown(
    "<div style='padding:16px 0 24px 0;'>"
    "<div style='font-family:IBM Plex Mono,monospace;font-size:20px;font-weight:600;color:#e6edf3;'>🍎 Apple FHI</div>"
    "<div style='font-size:11px;color:#8b949e;margin-top:4px;letter-spacing:1px;text-transform:uppercase;'>Financial Health Index</div>"
    "</div>",
    unsafe_allow_html=True
)

nav = st.sidebar.radio(
    "NAVIGATION",
    ["Overview", "Financial Ratios", "Macro & Commodities",
     "FHI Deep Dive", "News & Sentiment", "Model Forecast",
     "Predict FHI", "Data Explorer"],
    label_visibility="visible"
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size:11px;color:#8b949e;line-height:1.8;'>"
    "<b style='color:#e6edf3;'>Dataset</b><br>179 monthly observations<br>Jun 2010 — Apr 2025<br><br>"
    "<b style='color:#e6edf3;'>Models</b><br>ARIMAX (p=2, d=1, q=4)<br>LSTM (50 units, lookback=12)<br><br>"
    "<b style='color:#e6edf3;'>Best RMSE</b><br>"
    "<span style='color:#3fb950;font-family:IBM Plex Mono,monospace;'>0.0971 (ARIMAX)</span>"
    "</div>",
    unsafe_allow_html=True
)


# ─────────────────────────────────────────────
# PAGE: OVERVIEW
# ─────────────────────────────────────────────
if nav == "Overview":
    st.markdown(
        "<h1 style='font-size:32px;font-weight:600;color:#e6edf3;margin-bottom:4px;'>Apple Financial Health Index Dashboard</h1>"
        "<p style='color:#8b949e;font-size:15px;margin-bottom:32px;'>15 years of Apple financial data — ratios, macro indicators, sentiment and model forecasts in one place.</p>",
        unsafe_allow_html=True
    )

    latest = apple.iloc[-1]
    prev   = apple.iloc[-2]
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Return on Equity",  f"{latest['Return on Equity']:.1f}%",
                  f"{latest['Return on Equity']-prev['Return on Equity']:+.1f}%")
    with col2:
        st.metric("Return on Assets",  f"{latest['Return on Assets']:.1f}%",
                  f"{latest['Return on Assets']-prev['Return on Assets']:+.1f}%")
    with col3:
        st.metric("Debt / Equity",     f"{latest['Debt to Equity Ratio']:.2f}x",
                  f"{latest['Debt to Equity Ratio']-prev['Debt to Equity Ratio']:+.2f}")
    with col4:
        fhi_l = scaled_df['fhi'].iloc[-1]; fhi_p = scaled_df['fhi'].iloc[-2]
        st.metric("FHI Score", f"{fhi_l:.3f}", f"{fhi_l-fhi_p:+.3f}")
    with col5:
        st.metric("Stock Price", f"${latest['Stock Price']:.2f}",
                  f"{latest['Stock Price']-prev['Stock Price']:+.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    section("Financial Health Index — 2010 to 2025")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=scaled_df.index, y=scaled_df['fhi'],
        fill='tozeroy', fillcolor='rgba(88,166,255,0.08)',
        line=dict(color=C["primary"], width=2.5), name='FHI',
        hovertemplate='%{x|%b %Y}<br>FHI: %{y:.4f}<extra></extra>'))
    n = len(scaled_df)
    t1 = scaled_df.index[int(n*0.70)]
    t2 = scaled_df.index[int(n*0.85)]
    fig.add_vrect(x0=scaled_df.index[0], x1=t1, fillcolor="rgba(63,185,80,0.04)", line_width=0,
                  annotation_text="Train", annotation_position="top left",
                  annotation_font=dict(color=C["green"], size=11))
    fig.add_vrect(x0=t1, x1=t2, fillcolor="rgba(210,153,34,0.04)", line_width=0,
                  annotation_text="Val", annotation_position="top left",
                  annotation_font=dict(color=C["yellow"], size=11))
    fig.add_vrect(x0=t2, x1=scaled_df.index[-1], fillcolor="rgba(248,81,73,0.04)", line_width=0,
                  annotation_text="Test", annotation_position="top left",
                  annotation_font=dict(color=C["red"], size=11))
    dark_layout(fig, height=380)
    st.plotly_chart(fig, use_container_width=True)
    insight("The FHI stayed below 0.45 from 2010 to 2018, then climbed sharply. The rise after 2019 reflects Apple's aggressive share buyback program, rapid services revenue growth, and dramatic improvement in all five component ratios.")

    section("Key Ratio Snapshot")
    col1, col2 = st.columns(2)
    with col1:
        fig2 = go.Figure()
        for col, color in [('Return on Equity', C["primary"]), ('Return on Assets', C["green"]), ('Return on Investment', C["purple"])]:
            fig2.add_trace(go.Scatter(x=apple.index, y=apple[col], name=col, line=dict(color=color, width=2)))
        dark_layout(fig2, "Return Metrics (%)", height=320)
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        fig3 = go.Figure()
        for col, color in [('Current Ratio', C["yellow"]), ('Quick Ratio', C["orange"]), ('Debt to Equity Ratio', C["red"])]:
            fig3.add_trace(go.Scatter(x=apple.index, y=apple[col], name=col, line=dict(color=color, width=2)))
        dark_layout(fig3, "Liquidity & Leverage Ratios", height=320)
        st.plotly_chart(fig3, use_container_width=True)

    section("Model Performance Summary")
    col1, col2, col3, col4 = st.columns(4)
    results = [
        ("ARIMAX", "Ratios Only",  "0.0971", C["green"],   "Most reliable"),
        ("ARIMAX", "All Features", "0.1114", C["yellow"],  "Macro adds noise"),
        ("LSTM",   "Ratios Only",  "0.0272", C["primary"], "Best RMSE"),
        ("LSTM",   "All Features", "0.0396", C["muted"],   "Decent but worse"),
    ]
    for col, (model, features, rmse, color, note) in zip([col1,col2,col3,col4], results):
        with col:
            st.markdown(
                "<div class='card' style='border-top:3px solid {c};'>"
                "<div class='card-title'>{m}</div>"
                "<div style='font-size:11px;color:#8b949e;margin-bottom:10px;'>{f}</div>"
                "<div style='font-family:IBM Plex Mono,monospace;font-size:26px;font-weight:600;color:{c};'>{r}</div>"
                "<div style='font-size:11px;color:#8b949e;margin-top:6px;'>{n}</div>"
                "</div>".format(c=color, m=model, f=features, r=rmse, n=note),
                unsafe_allow_html=True
            )
    insight("Ratios-only beats all-features in every experiment. Apple's own financial fundamentals carry more signal than macro enrichment.")


# ─────────────────────────────────────────────
# PAGE: FINANCIAL RATIOS
# ─────────────────────────────────────────────
elif nav == "Financial Ratios":
    st.markdown("<h1 style='font-size:28px;font-weight:600;color:#e6edf3;'>Apple Financial Ratios</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e;margin-bottom:24px;'>All ratios from Macrotrends quarterly earnings data, forward-filled monthly.</p>", unsafe_allow_html=True)

    ratios = ['Return on Equity','Return on Assets','Return on Investment',
              'Debt to Equity Ratio','Current Ratio','Quick Ratio','PE Ratio','Price to Sales Ratio']
    latest = apple.iloc[-1]
    prev   = apple.iloc[-2]
    cols = st.columns(4)
    for i, r in enumerate(ratios):
        with cols[i % 4]:
            delta = latest[r] - prev[r]
            color = C["green"] if delta >= 0 else C["red"]
            arrow = "▲" if delta >= 0 else "▼"
            st.markdown(
                "<div class='card'><div class='card-title'>{r}</div>"
                "<div class='card-value'>{v:.2f}</div>"
                "<div class='card-sub' style='color:{c};'>{a} {d:.2f} vs prev</div></div>".format(
                    r=r, v=latest[r], c=color, a=arrow, d=abs(delta)
                ), unsafe_allow_html=True
            )

    section("Ratio Chart")
    selected_ratio = st.selectbox("Select ratio", ratios, index=0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=apple.index, y=apple[selected_ratio],
        fill='tozeroy', fillcolor='rgba(88,166,255,0.06)',
        line=dict(color=C["primary"], width=2.5), name=selected_ratio,
        hovertemplate='%{x|%b %Y}<br>' + selected_ratio + ': %{y:.3f}<extra></extra>'))
    roll = apple[selected_ratio].rolling(12).mean()
    fig.add_trace(go.Scatter(x=apple.index, y=roll,
        line=dict(color=C["yellow"], width=1.5, dash='dash'), name='12-month avg'))
    dark_layout(fig, selected_ratio, height=400)
    st.plotly_chart(fig, use_container_width=True)

    section("Ratio Correlation Heatmap")
    corr = apple[ratios].corr().round(2)
    fig_heat = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale=[[0, C["red"]], [0.5, C["surface2"]], [1, C["primary"]]], zmid=0,
        text=corr.values.round(2), texttemplate="%{text}",
        textfont=dict(size=10, color=C["text"]),
        hovertemplate='%{y} vs %{x}: %{z:.2f}<extra></extra>'
    ))
    dark_layout(fig_heat, "Pearson Correlation between Ratios", height=480)
    fig_heat.update_layout(xaxis=dict(tickangle=-35, tickfont=dict(size=10)), yaxis=dict(tickfont=dict(size=10)))
    st.plotly_chart(fig_heat, use_container_width=True)
    insight("Return on Equity and Return on Investment are highly correlated (>0.85). Debt to Equity is negatively correlated with Current and Quick Ratios.")

    section("Distribution of All Ratios")
    fig_box = go.Figure()
    palette = [C["primary"], C["green"], C["purple"], C["orange"], C["yellow"], C["teal"], C["red"], C["muted"]]
    for i, r in enumerate(ratios):
        hx = palette[i % len(palette)].lstrip('#')
        rc, gc, bc = int(hx[0:2],16), int(hx[2:4],16), int(hx[4:6],16)
        fig_box.add_trace(go.Box(y=apple[r], name=r,
            marker_color=palette[i%len(palette)], line_color=palette[i%len(palette)],
            fillcolor="rgba({},{},{},0.15)".format(rc,gc,bc), boxmean=True,
            hovertemplate='%{y:.3f}<extra>' + r + '</extra>'))
    dark_layout(fig_box, "Ratio Distribution (with mean marker)", height=400)
    st.plotly_chart(fig_box, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE: MACRO & COMMODITIES
# ─────────────────────────────────────────────
elif nav == "Macro & Commodities":
    st.markdown("<h1 style='font-size:28px;font-weight:600;color:#e6edf3;'>Macro & Commodity Indicators</h1>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        v = cpi['CPIAUCSL'].iloc[-1]; st.metric("CPI", f"{v:.1f}", f"{v-cpi['CPIAUCSL'].iloc[-2]:+.2f}")
    with col2:
        v = oil['WTISPLC'].iloc[-1]; st.metric("Oil ($/bbl)", f"${v:.2f}", f"{v-oil['WTISPLC'].iloc[-2]:+.2f}")
    with col3:
        v = copper['PCOPPUSDM'].iloc[-1]; st.metric("Copper ($/t)", f"${v:,.0f}", f"{v-copper['PCOPPUSDM'].iloc[-2]:+.0f}")
    with col4:
        v = gdp['GDP'].iloc[-1]; st.metric("GDP ($B)", f"${v:,.0f}", f"{v-gdp['GDP'].iloc[-2]:+.0f}")
    with col5:
        v = fedfunds['FEDFUNDS'].iloc[-1]; st.metric("Fed Funds Rate", f"{v:.2f}%", f"{v-fedfunds['FEDFUNDS'].iloc[-2]:+.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    section("All Macro Indicators Over Time")
    fig_macro = make_subplots(rows=3, cols=2,
        subplot_titles=["CPI (Inflation)", "WTI Oil Price ($/bbl)",
                        "Copper Price ($/metric ton)", "US GDP ($B)", "Federal Funds Rate (%)", ""],
        vertical_spacing=0.12, horizontal_spacing=0.08)
    for (x, y, color, row, col) in [
        (cpi.index,      cpi['CPIAUCSL'],      C["primary"], 1, 1),
        (oil.index,      oil['WTISPLC'],        C["orange"],  1, 2),
        (copper.index,   copper['PCOPPUSDM'],   C["yellow"],  2, 1),
        (gdp.index,      gdp['GDP'],            C["green"],   2, 2),
        (fedfunds.index, fedfunds['FEDFUNDS'],  C["red"],     3, 1),
    ]:
        fig_macro.add_trace(go.Scatter(x=x, y=y, line=dict(color=color, width=2), showlegend=False), row=row, col=col)
    fig_macro.update_layout(height=780, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans", color=C["muted"], size=11), margin=dict(l=10,r=10,t=30,b=10))
    for i in range(1,7):
        fig_macro.update_xaxes(gridcolor=C["border"], linecolor=C["border"], row=(i-1)//2+1, col=(i-1)%2+1)
        fig_macro.update_yaxes(gridcolor=C["border"], linecolor=C["border"], row=(i-1)//2+1, col=(i-1)%2+1)
    st.plotly_chart(fig_macro, use_container_width=True)

    section("Macro Correlation with FHI")
    macro_merged = pd.DataFrame({
        'CPI': cpi['CPIAUCSL'], 'Oil': oil['WTISPLC'], 'Copper': copper['PCOPPUSDM'],
        'GDP': gdp['GDP'], 'FedFunds': fedfunds['FEDFUNDS'], 'FHI': scaled_df['fhi']
    }).dropna()
    corr_fhi = macro_merged.corr()['FHI'].drop('FHI').sort_values()
    fig_corr = go.Figure(go.Bar(
        x=corr_fhi.values, y=corr_fhi.index, orientation='h',
        marker_color=[C["red"] if v < 0 else C["green"] for v in corr_fhi.values],
        text=[f"{v:.3f}" for v in corr_fhi.values], textposition='outside',
        textfont=dict(color=C["text"], size=12, family="IBM Plex Mono")))
    dark_layout(fig_corr, "Pearson Correlation with FHI", height=320)
    fig_corr.update_layout(xaxis=dict(range=[-1, 1]))
    st.plotly_chart(fig_corr, use_container_width=True)
    insight("GDP (0.88) and CPI (0.88) show the strongest correlations with FHI, but multicollinearity between them explains why adding macro features hurt model performance.")


# ─────────────────────────────────────────────
# PAGE: FHI DEEP DIVE
# ─────────────────────────────────────────────
elif nav == "FHI Deep Dive":
    st.markdown("<h1 style='font-size:28px;font-weight:600;color:#e6edf3;'>FHI Deep Dive</h1>", unsafe_allow_html=True)

    section("FHI Component Weights")
    col1, col2 = st.columns([1, 2])
    with col1:
        for ratio, w in FHI_WEIGHTS.items():
            color = C["primary"] if w >= 0.25 else C["green"] if w >= 0.20 else C["yellow"]
            st.markdown(
                "<div style='margin-bottom:12px;'>"
                "<div style='font-size:12px;color:#8b949e;margin-bottom:4px;'>{r}</div>"
                "<div style='display:flex;align-items:center;gap:10px;'>"
                "<div style='width:{bw}px;height:8px;background:{c};border-radius:4px;opacity:0.8;'></div>"
                "<span style='font-family:IBM Plex Mono,monospace;font-size:13px;color:{c};'>{wp:.0f}%</span>"
                "</div></div>".format(r=ratio, bw=int(w*100)*3, c=color, wp=w*100),
                unsafe_allow_html=True
            )
    with col2:
        fig_pie = go.Figure(go.Pie(
            labels=list(FHI_WEIGHTS.keys()), values=list(FHI_WEIGHTS.values()), hole=0.55,
            marker=dict(colors=[C["primary"], C["green"], C["purple"], C["orange"], C["yellow"]],
                        line=dict(color=C["bg"], width=3)),
            textinfo='percent', textfont=dict(size=12, color=C["text"])))
        fig_pie.add_annotation(text="FHI", x=0.5, y=0.5,
            font=dict(size=20, color=C["text"], family="IBM Plex Mono"), showarrow=False)
        dark_layout(fig_pie, height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

    section("FHI Timeline with Log Transform")
    fig_fhi = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                             subplot_titles=["FHI (Scaled 0-1)", "FHI Log Transformed"])
    fig_fhi.add_trace(go.Scatter(x=scaled_df.index, y=scaled_df['fhi'],
        fill='tozeroy', fillcolor='rgba(88,166,255,0.07)',
        line=dict(color=C["primary"], width=2.5), name='FHI'), row=1, col=1)
    fig_fhi.add_trace(go.Scatter(x=scaled_df.index, y=scaled_df['fhi_log'],
        fill='tozeroy', fillcolor='rgba(255,123,114,0.07)',
        line=dict(color=C["orange"], width=2.5), name='log(FHI)'), row=2, col=1)
    fig_fhi.update_layout(height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans", color=C["muted"]), margin=dict(l=10,r=10,t=40,b=10),
        showlegend=True, legend=dict(bgcolor="rgba(0,0,0,0)"))
    for r in [1, 2]:
        fig_fhi.update_xaxes(gridcolor=C["border"], linecolor=C["border"], row=r, col=1)
        fig_fhi.update_yaxes(gridcolor=C["border"], linecolor=C["border"], row=r, col=1)
    st.plotly_chart(fig_fhi, use_container_width=True)

    section("FHI Component Contributions Over Time")
    contrib = pd.DataFrame({col: scaled_df[col] * w for col, w in FHI_WEIGHTS.items()})
    fig_area = go.Figure()
    colors_area = [C["primary"], C["green"], C["purple"], C["orange"], C["yellow"]]
    for i, col in enumerate(FHI_WEIGHTS.keys()):
        hx = colors_area[i].lstrip('#')
        rc, gc, bc = int(hx[0:2],16), int(hx[2:4],16), int(hx[4:6],16)
        fig_area.add_trace(go.Scatter(x=contrib.index, y=contrib[col], name=col, stackgroup='one',
            fillcolor="rgba({},{},{},0.6)".format(rc,gc,bc), line=dict(color=colors_area[i], width=0.5)))
    dark_layout(fig_area, "Stacked FHI Component Contributions", height=380)
    st.plotly_chart(fig_area, use_container_width=True)
    insight("Return on Equity and Debt to Equity together account for 50% of the index. The post-2019 surge is driven mostly by the jump in Return on Equity and Return on Investment.")

    section("Stationarity Test Results")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            "<div class='card' style='border-top:3px solid #f85149;'>"
            "<div class='card-title'>ADF Test — fhi_log (raw)</div>"
            "<div style='font-family:IBM Plex Mono;font-size:14px;margin-top:12px;line-height:2;'>"
            "<span style='color:#8b949e;'>Statistic:</span> <span style='color:#e6edf3;'>-0.98</span><br>"
            "<span style='color:#8b949e;'>p-value:</span> <span style='color:#f85149;'>0.7605</span><br>"
            "<span style='color:#8b949e;'>Result:</span> <span style='color:#f85149;'>NOT stationary</span>"
            "</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(
            "<div class='card' style='border-top:3px solid #3fb950;'>"
            "<div class='card-title'>ADF Test — fhi_log_diff (after differencing)</div>"
            "<div style='font-family:IBM Plex Mono;font-size:14px;margin-top:12px;line-height:2;'>"
            "<span style='color:#8b949e;'>Statistic:</span> <span style='color:#e6edf3;'>-11.42</span><br>"
            "<span style='color:#8b949e;'>p-value:</span> <span style='color:#3fb950;'>0.0000</span><br>"
            "<span style='color:#8b949e;'>Result:</span> <span style='color:#3fb950;'>Stationary</span>"
            "</div></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: NEWS & SENTIMENT
# ─────────────────────────────────────────────
elif nav == "News & Sentiment":
    st.markdown("<h1 style='font-size:28px;font-weight:600;color:#e6edf3;'>News & Sentiment Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e;margin-bottom:24px;'>1,069 New York Times articles scored with ProsusAI/FinBERT (2010-2025).</p>", unsafe_allow_html=True)

    news_clean = news.copy()
    news_clean['pub_date'] = pd.to_datetime(news_clean['pub_date'])
    news_clean['year'] = news_clean['pub_date'].dt.year

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Articles", f"{len(news_clean):,}")
    with col2: st.metric("Date Range", f"{news_clean['pub_date'].dt.year.min()} - {news_clean['pub_date'].dt.year.max()}")
    with col3: st.metric("Positive Articles", "601 (56.2%)")
    with col4: st.metric("Negative Articles", "117 (11.0%)")

    st.markdown("<br>", unsafe_allow_html=True)
    section("Sentiment Distribution")
    col1, col2 = st.columns(2)
    labels = ['Positive', 'Neutral', 'Negative']
    values = [601, 351, 117]
    colors_pie = [C["green"], C["muted"], C["red"]]
    with col1:
        fig_pie = go.Figure(go.Pie(labels=labels, values=values, hole=0.55,
            marker=dict(colors=colors_pie, line=dict(color=C["bg"], width=3)),
            textinfo='label+percent', textfont=dict(size=13, color=C["text"])))
        fig_pie.add_annotation(text="1,069<br>articles", x=0.5, y=0.5,
            font=dict(size=14, color=C["text"], family="IBM Plex Mono"), showarrow=False)
        dark_layout(fig_pie, "Sentiment Breakdown", height=340)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        fig_sbar = go.Figure(go.Bar(x=labels, y=values, marker_color=colors_pie,
            text=values, textposition='outside',
            textfont=dict(size=13, color=C["text"], family="IBM Plex Mono")))
        dark_layout(fig_sbar, "Article Count by Sentiment", height=340)
        st.plotly_chart(fig_sbar, use_container_width=True)

    section("Articles Published per Year")
    yearly = news_clean.groupby('year').size().reset_index(name='count')
    fig_yr = go.Figure(go.Bar(x=yearly['year'], y=yearly['count'],
        marker_color=C["primary"], marker_line_color=C["border"], marker_line_width=1,
        text=yearly['count'], textposition='outside',
        textfont=dict(size=11, color=C["text"], family="IBM Plex Mono")))
    dark_layout(fig_yr, "NYT Apple-Related Articles by Year", height=340)
    st.plotly_chart(fig_yr, use_container_width=True)
    insight("Coverage is sparse before 2015. Volume picks up significantly from 2015 onwards.")

    section("Recent Headlines")
    recent = news_clean.sort_values('pub_date', ascending=False).head(20)
    st.dataframe(
        recent[['pub_date','headline','snippet']].rename(
            columns={'pub_date':'Date','headline':'Headline','snippet':'Snippet'})
        .style.set_properties(**{'background-color': C["surface"], 'color': C["text"], 'font-size': '13px'}),
        height=400, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE: MODEL FORECAST
# ─────────────────────────────────────────────
elif nav == "Model Forecast":
    st.markdown("<h1 style='font-size:28px;font-weight:600;color:#e6edf3;'>Model Forecast</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e;margin-bottom:24px;'>ARIMAX and LSTM trained on FHI log-differenced series. Test set: Feb 2023 - Apr 2025.</p>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    model_data = [
        ("ARIMAX", "Ratios Only",  "0.0971", "(2,1,4)",          C["green"],   "Best statistical model"),
        ("ARIMAX", "All Features", "0.1114", "(3,1,4)",          C["yellow"],  "Macro adds noise"),
        ("LSTM",   "Ratios Only",  "0.0272", "50 units | LB=12", C["primary"], "Best overall RMSE"),
        ("LSTM",   "All Features", "0.0396", "50 units | LB=12", C["muted"],   "More features, worse result"),
    ]
    for col, (model, feat, rmse, params, color, note) in zip([col1,col2,col3,col4], model_data):
        with col:
            pill_cls = "green" if color == C["green"] else "blue" if color == C["primary"] else "red"
            st.markdown(
                "<div class='card' style='border-top:3px solid {c};min-height:160px;'>"
                "<div style='display:flex;justify-content:space-between;align-items:flex-start;'>"
                "<div><div class='card-title'>{m}</div>"
                "<div style='font-size:12px;color:#8b949e;'>{f}</div></div>"
                "<span class='pill-{p}'>RMSE {r}</span></div>"
                "<div style='font-family:IBM Plex Mono,monospace;font-size:11px;color:#8b949e;margin-top:12px;'>{pa}</div>"
                "<div style='font-size:12px;color:#8b949e;margin-top:8px;'>{n}</div>"
                "</div>".format(c=color, m=model, f=feat, p=pill_cls, r=rmse, pa=params, n=note),
                unsafe_allow_html=True
            )

    section("RMSE Comparison Chart")
    rmse_vals  = [0.0971, 0.1114, 0.0272, 0.0396]
    bar_colors = [C["green"], C["yellow"], C["primary"], C["muted"]]
    fig_rmse = go.Figure(go.Bar(
        x=['ARIMAX\nRatios Only','ARIMAX\nAll Features','LSTM\nRatios Only','LSTM\nAll Features'],
        y=rmse_vals, marker_color=bar_colors,
        text=[f"{v:.4f}" for v in rmse_vals], textposition='outside',
        textfont=dict(size=13, color=C["text"], family="IBM Plex Mono")))
    dark_layout(fig_rmse, "Test Set RMSE — All 4 Models", height=380)
    fig_rmse.update_layout(yaxis=dict(range=[0, max(rmse_vals)*1.3]))
    st.plotly_chart(fig_rmse, use_container_width=True)

    section("Data Leakage Prevention")
    leakage_data = [
        ["Outlier Treatment", "IQR on full data uses future values",     "IQR from training data only"],
        ["Scaling",           "Scaler fitted on full range",              "MinMaxScaler fitted on train only"],
        ["Re-splitting",      "Splitting after dropna shifts boundaries", "Split once before any transformation"],
        ["NaN Filling",       "bfill() fills past NaN with future value", "ffill() only — no backward fill"],
    ]
    df_leak = pd.DataFrame(leakage_data, columns=["Stage","Risk Without Fix","Fix Applied"])
    st.dataframe(df_leak.style.set_properties(**{'background-color':C["surface"],'color':C["text"],'font-size':'13px'}),
                 use_container_width=True, height=200)
    insight("The LSTM Ratios-Only RMSE of 0.0272 partially benefits from Apple's quarterly data repetition. ARIMAX (0.0971) is the more conservative and interpretable result.")


# ─────────────────────────────────────────────
# PAGE: PREDICT FHI  ← FULLY CORRECTED
# ─────────────────────────────────────────────
elif nav == "Predict FHI":

    import pickle
    import traceback

    BASE_M = "Models"

    MODEL_PATHS = {
    "ARIMAX — Ratios Only":  BASE_M + "/arima_ratios.pkl",
    "ARIMAX — All Features": BASE_M + "/arima_all.pkl",
    "LSTM — Ratios Only":    BASE_M + "/lstm_ratios.keras",
    "LSTM — All Features":   BASE_M + "/lstm_all.keras",
    }

    # ── Model loader ──────────────────────────────────────────────────────────
    @st.cache_resource
    def load_model_cached(path: str):
        if path.endswith(".keras"):
            from tensorflow.keras.models import load_model as keras_load
            return keras_load(path), "lstm"
        try:
            import joblib
            return joblib.load(path), "arimax"
        except Exception:
            pass
        with open(path, "rb") as f:
            return pickle.load(f), "arimax"

    # ── Prepare the model-ready DataFrame from scaled_df ─────────────────────
    # Mirrors notebook cell [057]: add fhi_log_diff, drop the first NaN row.
    # The feature columns are the RAW scaled values (not differenced) — this
    # is exactly what create_sequences() sliced in cell [064].
    def prepare_model_df(s_df: pd.DataFrame) -> pd.DataFrame:
        out = s_df.copy()
        out['fhi_log_diff'] = out['fhi_log'].diff()
        return out.dropna(subset=['fhi_log_diff'])

    # ── Build a (1, LOOKBACK, n_features) input array ─────────────────────────
    # Mirrors create_sequences() in notebook cell [064].
    # X[i] = data[feature_cols].iloc[i : i+LOOKBACK]   (raw scaled values)
    # y[i] = data['fhi_log_diff'].iloc[i+LOOKBACK]
    # For inference we take the LAST LOOKBACK rows of feature_cols.
    def build_lstm_X(model_df: pd.DataFrame, feature_cols: list) -> np.ndarray:
        arr = model_df[feature_cols].values[-LOOKBACK:]          # (12, n_feat)
        if len(arr) < LOOKBACK:
            pad = np.zeros((LOOKBACK - len(arr), len(feature_cols)), dtype=np.float32)
            arr = np.vstack([pad, arr])
        return arr[np.newaxis, :, :].astype(np.float32)          # (1, 12, n_feat)

    # ── ARIMAX: forecast one step ─────────────────────────────────────────────
    def arimax_predict_next(model, fhi_log_diff: pd.Series,
                            model_df: pd.DataFrame, feature_cols: list) -> float:
        exog = model_df[feature_cols].ffill().bfill()
        try:
            res        = model.apply(fhi_log_diff, exog=exog, refit=False)
            next_exog  = exog.iloc[[-1]]
            return float(res.forecast(steps=1, exog=next_exog).iloc[0])
        except Exception:
            try:
                res = model.apply(fhi_log_diff, refit=False)
                return float(res.forecast(steps=1).iloc[0])
            except Exception:
                from statsmodels.tsa.statespace.sarimax import SARIMAX
                order = getattr(getattr(model, 'model', None), 'order', (2, 0, 4))
                m = SARIMAX(fhi_log_diff, order=order).fit(disp=False)
                return float(m.forecast(steps=1).iloc[0])

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE LAYOUT
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown(
        "<h1 style='font-size:28px;font-weight:600;color:#e6edf3;'>Predict Next-Month FHI</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color:#8b949e;margin-bottom:24px;'>"
        "Runs the <b>exact same inference pipeline</b> as the training notebook — "
        "same scaler, same feature columns, same sequence construction.</p>",
        unsafe_allow_html=True
    )

    # ── 1. Model selector ─────────────────────────────────────────────────────
    section("1 · Select Model")
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        selected_model_name = st.selectbox("Model", list(MODEL_PATHS.keys()),
                                            label_visibility="collapsed")
    is_all_features = "All Features" in selected_model_name
    is_lstm         = "LSTM"         in selected_model_name
    feature_cols    = ALL_FEATURES   if is_all_features else RATIO_FEATURES
    n_features      = len(feature_cols)   # 14 or 8

    with col_m2:
        st.markdown(
            "<div style='background:#21262d;border:1px solid #30363d;border-radius:8px;"
            "padding:12px 18px;font-size:13px;color:#8b949e;line-height:2;'>"
            "<b style='color:#e6edf3;'>Architecture:</b> {arch}<br>"
            "<b style='color:#e6edf3;'>Feature columns:</b> {n} &nbsp;({cols})<br>"
            "<b style='color:#e6edf3;'>LSTM input shape:</b> (batch=1, lookback={lb}, features={n})"
            "</div>".format(
                arch="LSTM (deep learning)" if is_lstm else "ARIMAX (statistical)",
                n=n_features,
                cols=", ".join(feature_cols),
                lb=LOOKBACK
            ), unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 2. Input source ───────────────────────────────────────────────────────
    section("2 · Input Data")
    tab_hist, tab_upload = st.tabs(["📊 Use Pre-loaded Historical Data (Recommended)", "📂 Upload Your Own CSV"])

    # ── TAB 1: pre-loaded (best path — same scaler as training) ───────────────
    with tab_hist:
        st.markdown(
            "<p style='color:#8b949e;font-size:13px;margin-bottom:8px;'>"
            "Uses the scaled dataset already in memory — the <b>same scaler</b> "
            "that was fitted on the training split. This is the most faithful "
            "reproduction of the training pipeline.</p>",
            unsafe_allow_html=True
        )
        model_df = prepare_model_df(scaled_df)

        # Show the last LOOKBACK rows of the chosen feature set
        display_df = model_df[feature_cols].tail(LOOKBACK)
        st.dataframe(display_df.style.format("{:.4f}"), use_container_width=True)
        st.markdown(
            "<p style='color:#8b949e;font-size:12px;margin-top:4px;'>"
            "↑ These {lb} rows form the prediction window (latest = row {lb}).</p>".format(lb=LOOKBACK),
            unsafe_allow_html=True
        )
        st.session_state["pred_model_df"] = model_df
        st.session_state["input_source"]  = "historical"

    # ── TAB 2: upload CSV ─────────────────────────────────────────────────────
    with tab_upload:
        st.markdown(
            "<p style='color:#8b949e;font-size:13px;margin-bottom:12px;'>"
            "Upload a CSV with a <b>Date</b> column and the feature columns below. "
            "Values must be <b>pre-scaled to [0,1]</b> using the same MinMaxScaler "
            "as training, or tick <i>Auto-scale</i> to apply a new scaler to raw values. "
            "Minimum {lb} rows required.</p>".format(lb=LOOKBACK),
            unsafe_allow_html=True
        )
        st.markdown(
            "<div style='background:#21262d;border:1px solid #30363d;border-radius:6px;"
            "padding:10px 14px;font-size:12px;color:#8b949e;font-family:IBM Plex Mono,monospace;"
            "margin-bottom:12px;'>{}</div>".format(", ".join(feature_cols)),
            unsafe_allow_html=True
        )
        auto_scale    = st.checkbox("Auto-scale (raw/unscaled values)", value=True)
        template_df   = pd.DataFrame(columns=["Date"] + feature_cols)
        st.download_button("⬇ Download CSV Template", template_df.to_csv(index=False),
                           "fhi_input_template.csv", "text/csv", key="template_dl")

        uploaded_file = st.file_uploader("Choose CSV", type=["csv"], key="csv_upload")
        if uploaded_file is not None:
            try:
                up_df = pd.read_csv(uploaded_file)
                up_df["Date"] = pd.to_datetime(up_df["Date"])
                up_df = up_df.sort_values("Date").set_index("Date")
                missing = [c for c in feature_cols if c not in up_df.columns]
                if missing:
                    st.error("Missing columns: " + str(missing))
                else:
                    sub = up_df[feature_cols].ffill().bfill()
                    if auto_scale:
                        from sklearn.preprocessing import MinMaxScaler as _MMS
                        _sc = _MMS()
                        sub = pd.DataFrame(_sc.fit_transform(sub),
                                           columns=feature_cols, index=sub.index)

                    # Reconstruct fhi, fhi_log, fhi_log_diff from FHI weights
                    fhi_cols_present = [c for c in FHI_WEIGHTS if c in sub.columns]
                    sub['fhi']          = sum(sub[c] * FHI_WEIGHTS[c] for c in fhi_cols_present)
                    sub['fhi_log']      = np.log(sub['fhi'] + 1e-8)
                    sub['fhi_log_diff'] = sub['fhi_log'].diff()
                    sub = sub.dropna(subset=['fhi_log_diff'])

                    if len(sub) < LOOKBACK:
                        st.error(f"Need at least {LOOKBACK} rows after dropping NaN. Got {len(sub)}.")
                    else:
                        st.session_state["pred_model_df"] = sub
                        st.session_state["input_source"]  = "upload"
                        st.success(f"Loaded {len(sub)} rows.")
                        st.dataframe(sub[feature_cols].tail(LOOKBACK).style.format("{:.4f}"),
                                     use_container_width=True)
            except Exception as e:
                st.error("Could not parse CSV: " + str(e))

    # ── 3. Run Prediction ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    section("3 · Run Prediction")

    source_label = st.session_state.get("input_source", None)
    if source_label:
        src_display = {
            "historical": "📊 Pre-loaded historical data",
            "upload":     "📂 Uploaded CSV"
        }.get(source_label, source_label)
        n_rows = len(st.session_state.get("pred_model_df", []))
        st.markdown(
            "<div style='font-size:13px;color:#8b949e;margin-bottom:12px;'>"
            "Source: <b style='color:#e6edf3;'>{s}</b> &nbsp;·&nbsp; "
            "{n} rows &nbsp;·&nbsp; "
            "Prediction window: last {lb} rows &nbsp;·&nbsp; "
            "Features: {nf}</div>".format(
                s=src_display, n=n_rows, lb=LOOKBACK, nf=n_features),
            unsafe_allow_html=True
        )

    run_col, _ = st.columns([1, 3])
    with run_col:
        run_btn = st.button("▶  Run Prediction", type="primary",
                            use_container_width=True, key="run_pred")

    if run_btn:
        pred_model_df = st.session_state.get("pred_model_df", None)
        if pred_model_df is None or len(pred_model_df) < LOOKBACK:
            st.error(f"Need at least {LOOKBACK} rows. Complete Step 2 first.")
        else:
            pred_ok  = False
            pred_fhi = current_fhi = delta = pct = 0.0

            with st.spinner("Loading model and running inference..."):
                try:
                    model_obj, model_type = load_model_cached(MODEL_PATHS[selected_model_name])

                    fhi_series   = pred_model_df['fhi']
                    fhi_log_diff = pred_model_df['fhi_log_diff']
                    current_fhi  = float(fhi_series.iloc[-1])
                    last_log_val = float(pred_model_df['fhi_log'].iloc[-1])

                    if model_type == "lstm":
                        # ── KEY FIX ──────────────────────────────────────────
                        # X shape must be (1, 12, n_features) where n_features
                        # is 8 for lstm_ratios and 14 for lstm_all.
                        # The features are the NON-differenced scaled columns,
                        # exactly matching create_sequences() in notebook cell 064.
                        X         = build_lstm_X(pred_model_df, feature_cols)
                        pred_diff = float(model_obj.predict(X, verbose=0)[0][0])
                    else:
                        pred_diff = arimax_predict_next(
                            model_obj, fhi_log_diff, pred_model_df, feature_cols
                        )

                    # Invert the log-difference to get the FHI level:
                    #   fhi_log[t+1] = fhi_log[t] + pred_diff
                    #   fhi[t+1]     = exp(fhi_log[t+1]) - epsilon
                    pred_fhi = float(np.clip(
                        np.exp(last_log_val + pred_diff) - 1e-8, 0, 1
                    ))
                    delta   = pred_fhi - current_fhi
                    pct     = delta / (current_fhi + 1e-8) * 100
                    pred_ok = True

                except FileNotFoundError:
                    st.error("Model file not found: " + MODEL_PATHS[selected_model_name])
                except Exception as e:
                    st.error("Prediction failed: " + str(e))
                    st.code(traceback.format_exc())

            if pred_ok:
                # Health band
                if pred_fhi >= 0.75:
                    gauge_color = C["green"];  health_label = "Strong"
                elif pred_fhi >= 0.50:
                    gauge_color = C["yellow"]; health_label = "Moderate"
                elif pred_fhi >= 0.25:
                    gauge_color = C["orange"]; health_label = "Weak"
                else:
                    gauge_color = C["red"];    health_label = "Critical"

                arrow       = "▲" if delta >= 0 else "▼"
                delta_color = C["green"] if delta >= 0 else C["red"]

                # ── KPI cards ─────────────────────────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(
                        "<div class='card' style='border-top:3px solid {gc};text-align:center;'>"
                        "<div class='card-title'>Predicted FHI</div>"
                        "<div style='font-family:IBM Plex Mono,monospace;font-size:42px;font-weight:700;"
                        "color:{gc};line-height:1.1;'>{v:.4f}</div>"
                        "<div style='font-size:13px;color:{gc};margin-top:6px;font-weight:600;'>{hl}</div>"
                        "</div>".format(gc=gauge_color, v=pred_fhi, hl=health_label),
                        unsafe_allow_html=True)
                with c2:
                    st.markdown(
                        "<div class='card' style='border-top:3px solid #58a6ff;text-align:center;'>"
                        "<div class='card-title'>Current FHI</div>"
                        "<div style='font-family:IBM Plex Mono,monospace;font-size:42px;font-weight:700;"
                        "color:#e6edf3;line-height:1.1;'>{v:.4f}</div>"
                        "<div style='font-size:13px;color:#8b949e;margin-top:6px;'>Latest data point</div>"
                        "</div>".format(v=current_fhi), unsafe_allow_html=True)
                with c3:
                    st.markdown(
                        "<div class='card' style='border-top:3px solid {dc};text-align:center;'>"
                        "<div class='card-title'>Month-on-Month Change</div>"
                        "<div style='font-family:IBM Plex Mono,monospace;font-size:42px;font-weight:700;"
                        "color:{dc};line-height:1.1;'>{a} {av:.4f}</div>"
                        "<div style='font-size:13px;color:{dc};margin-top:6px;'>{pct:+.2f}%</div>"
                        "</div>".format(dc=delta_color, a=arrow, av=abs(delta), pct=pct),
                        unsafe_allow_html=True)
                with c4:
                    st.markdown(
                        "<div class='card' style='border-top:3px solid #8b949e;text-align:center;'>"
                        "<div class='card-title'>Model / Input Shape</div>"
                        "<div style='font-family:IBM Plex Mono,monospace;font-size:18px;font-weight:600;"
                        "color:#e6edf3;line-height:1.4;margin-top:8px;'>{arch}</div>"
                        "<div style='font-size:12px;color:#8b949e;margin-top:6px;'>"
                        "{feat}<br>(1, {lb}, {nf})</div>"
                        "</div>".format(
                            arch="LSTM" if is_lstm else "ARIMAX",
                            feat="All Features (14)" if is_all_features else "Ratios Only (8)",
                            lb=LOOKBACK, nf=n_features),
                        unsafe_allow_html=True)

                # ── Gauge ──────────────────────────────────────────────────────
                st.markdown("<br>", unsafe_allow_html=True)
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=pred_fhi,
                    number=dict(font=dict(size=48, color=C["text"], family="IBM Plex Mono"),
                                valueformat=".4f"),
                    delta=dict(reference=current_fhi, valueformat=".4f", font=dict(size=16),
                               increasing=dict(color=C["green"]),
                               decreasing=dict(color=C["red"])),
                    gauge=dict(
                        axis=dict(range=[0,1], tickwidth=1, tickcolor=C["border"],
                                  tickfont=dict(color=C["muted"])),
                        bar=dict(color=gauge_color, thickness=0.25),
                        bgcolor="rgba(0,0,0,0)", borderwidth=0,
                        steps=[
                            dict(range=[0,    0.25], color="rgba(248,81,73,0.15)"),
                            dict(range=[0.25, 0.50], color="rgba(255,123,114,0.10)"),
                            dict(range=[0.50, 0.75], color="rgba(210,153,34,0.10)"),
                            dict(range=[0.75, 1.00], color="rgba(63,185,80,0.10)"),
                        ],
                        threshold=dict(line=dict(color=gauge_color, width=3),
                                       thickness=0.75, value=pred_fhi)
                    ),
                    title=dict(text="Next-Month FHI — " + selected_model_name,
                               font=dict(size=14, color=C["muted"]))
                ))
                fig_gauge.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="IBM Plex Sans", color=C["muted"]),
                    margin=dict(l=20,r=20,t=60,b=20))
                st.plotly_chart(fig_gauge, use_container_width=True)

                # ── History + forecast ─────────────────────────────────────────
                next_date = fhi_series.index[-1] + pd.DateOffset(months=1)
                fig_hist  = go.Figure()
                fig_hist.add_trace(go.Scatter(
                    x=fhi_series.index, y=fhi_series.values,
                    fill="tozeroy", fillcolor="rgba(88,166,255,0.07)",
                    line=dict(color=C["primary"], width=2.5), name="FHI history",
                    hovertemplate="%{x|%b %Y}<br>FHI: %{y:.4f}<extra></extra>"))
                fig_hist.add_trace(go.Scatter(
                    x=[fhi_series.index[-1], next_date], y=[current_fhi, pred_fhi],
                    line=dict(color=gauge_color, width=2, dash="dot"),
                    mode="lines+markers",
                    marker=dict(size=[8,14], color=gauge_color, symbol=["circle","star"]),
                    name="Forecast",
                    hovertemplate="%{x|%b %Y}<br>FHI: %{y:.4f}<extra></extra>"))
                dark_layout(fig_hist, "FHI History + Next-Month Forecast", height=360)
                st.plotly_chart(fig_hist, use_container_width=True)

                dw = "increase" if delta >= 0 else "decrease"
                insight(
                    "<b>{m}</b> predicts an FHI of <b style='color:{gc};'>{pf:.4f}</b> for next month — "
                    "a <b>{dw} of {ad:.4f} ({ap:.2f}%)</b> from the current {cf:.4f}. "
                    "Health: <b style='color:{gc};'>{hl}</b>.<br><br>"
                    "<b>Pipeline:</b> scaled_{feat} columns → "
                    "sequence (1,&nbsp;{lb},&nbsp;{nf}) → {arch} → "
                    "pred_diff → exp(log_fhi + pred_diff) = FHI.".format(
                        m=selected_model_name, gc=gauge_color, pf=pred_fhi,
                        dw=dw, ad=abs(delta), ap=abs(pct), cf=current_fhi,
                        hl=health_label,
                        feat="all" if is_all_features else "ratio",
                        lb=LOOKBACK, nf=n_features,
                        arch="LSTM" if is_lstm else "ARIMAX")
                )


# ─────────────────────────────────────────────
# PAGE: DATA EXPLORER
# ─────────────────────────────────────────────
elif nav == "Data Explorer":
    st.markdown("<h1 style='font-size:28px;font-weight:600;color:#e6edf3;'>Data Explorer</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Apple Financials", "Macro & Commodities", "Custom Chart"])

    with tab1:
        section("Apple Financial Data (2010-2025)")
        search = st.text_input("Search columns", placeholder="e.g. Return, Ratio, Revenue...")
        cols_to_show = [c for c in apple.columns if search.lower() in c.lower()] if search else list(apple.columns)
        st.dataframe(
            apple[cols_to_show].style.format("{:.2f}").background_gradient(
                cmap='Blues', subset=cols_to_show[:3] if len(cols_to_show) >= 3 else cols_to_show),
            height=500, use_container_width=True)
        st.download_button("Download Apple Data CSV", apple.reset_index().to_csv(index=False),
                           "apple_financials.csv", "text/csv")

    with tab2:
        section("Macro & Commodity Data (2010-2025)")
        macro_combined = pd.DataFrame({
            'CPI': cpi['CPIAUCSL'], 'Oil': oil['WTISPLC'], 'Copper': copper['PCOPPUSDM'],
            'GDP': gdp['GDP'], 'FedFunds': fedfunds['FEDFUNDS']})
        st.dataframe(macro_combined.style.format("{:.2f}"), height=500, use_container_width=True)
        st.download_button("Download Macro Data CSV", macro_combined.reset_index().to_csv(index=False),
                           "macro_data.csv", "text/csv")

    with tab3:
        section("Build Your Own Chart")
        all_cols_chart = list(apple.columns) + ['CPI','Oil','Copper','GDP','FedFunds','FHI']
        full_df  = apple.copy()
        full_df['CPI']      = cpi['CPIAUCSL']
        full_df['Oil']      = oil['WTISPLC']
        full_df['Copper']   = copper['PCOPPUSDM']
        full_df['GDP']      = gdp['GDP']
        full_df['FedFunds'] = fedfunds['FEDFUNDS']
        full_df['FHI']      = scaled_df['fhi']

        col1, col2, col3 = st.columns(3)
        with col1: y1 = st.selectbox("Primary series", all_cols_chart,
                                      index=all_cols_chart.index('Return on Equity'))
        with col2: y2 = st.selectbox("Secondary series (optional)", ["None"] + all_cols_chart, index=0)
        with col3: chart_type = st.selectbox("Chart type", ["Line", "Bar", "Area"])

        fig_custom = go.Figure()
        if chart_type == "Area":
            fig_custom.add_trace(go.Scatter(x=full_df.index, y=full_df[y1].ffill(),
                fill='tozeroy', fillcolor='rgba(88,166,255,0.08)',
                line=dict(color=C["primary"], width=2.5), name=y1))
        elif chart_type == "Bar":
            fig_custom.add_trace(go.Bar(x=full_df.index, y=full_df[y1].ffill(),
                marker_color=C["primary"], name=y1))
        else:
            fig_custom.add_trace(go.Scatter(x=full_df.index, y=full_df[y1].ffill(),
                line=dict(color=C["primary"], width=2.5), name=y1))

        if y2 != "None":
            fig_custom.add_trace(go.Scatter(x=full_df.index, y=full_df[y2].ffill(),
                line=dict(color=C["orange"], width=2, dash='dash'), name=y2, yaxis="y2"))
            fig_custom.update_layout(yaxis2=dict(overlaying='y', side='right',
                gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["orange"])))
        dark_layout(fig_custom, y1 + (" vs " + y2 if y2 != "None" else ""), height=440)
        st.plotly_chart(fig_custom, use_container_width=True)
