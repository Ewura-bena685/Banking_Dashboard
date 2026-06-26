import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import json
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Banking Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme configuration
DEFAULT_THEME = {
    "primary": "#1f77b4",
    "secondary": "#0d47a1",
    "accent": "#42a5f5",
    "template": "plotly",
    "light_bg": "#e3f2fd",
}

with st.sidebar:
    st.header("Report controls")
    selected_theme = DEFAULT_THEME
    st.divider()
    
    name = st.text_input("Your name", placeholder="E.g. Ewurabena Esther")
    role = st.selectbox(
        "Professional focus",
        ["Retail Banking", "Corporate Banking", "Risk & Compliance", "Data Analytics"],
    )
    office = st.selectbox(
        "Office location",
        ["Accra", "Tema", "Kumasi", "Takoradi", "Tamale"],
    )
    st.divider()

    st.subheader("Data source")
    data_source = st.radio(
        "Choose data source",
        ["Random demo data", "Upload CSV"],
        index=0,
    )
    n_points = st.slider("Reporting months", min_value=6, max_value=24, value=12, step=1)
    chart_type = st.radio(
        "Chart focus",
        ["Revenue & Balance", "Loan/Deposit Growth", "Transaction Volume"],
        index=0,
        horizontal=True,
    )
    st.divider()
    st.caption("Leave data source as 'Random demo data' to see a sample banking performance dashboard. Upload your own CSV with the required columns to visualize your specific data.")

# Apply theme CSS to entire dashboard
theme_css = f"""
<style>
    :root {{
        --primary-color: {selected_theme['primary']};
        --secondary-color: {selected_theme['secondary']};
        --accent-color: {selected_theme['accent']};
        --light-bg: {selected_theme['light_bg']};
    }}
    
    h1 {{
        color: {selected_theme['primary']} !important;
        border-bottom: 3px solid {selected_theme['accent']} !important;
        padding-bottom: 10px !important;
    }}
    
    h2, h3 {{
        color: {selected_theme['secondary']} !important;
    }}
    
    hr {{
        border-color: {selected_theme['accent']} !important;
        border-width: 2px !important;
    }}
    
    [data-testid="stMetricValue"] {{
        color: {selected_theme['primary']} !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {selected_theme['secondary']} !important;
    }}
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

st.markdown(f"<h1 style='color: {selected_theme['primary']};'> Banking Performance Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    f"<p style='color: {selected_theme['secondary']}; font-size: 16px;'>A dashboard for banking analytics, revenue performance, deposits, loan book quality, and customer satisfaction.</p>",
    unsafe_allow_html=True,
)
st.markdown(f"<hr style='border-color: {selected_theme['accent']}; border-width: 2px;'>", unsafe_allow_html=True)
# Responsive adjustments: media queries to improve layout on small screens
responsive_css = f"""
<style>
    @media (max-width: 800px) {{
        .stMetric {{
            display: block !important;
            width: 100% !important;
        }}
        .css-1gkcyyc .block-container {{
            padding-left: 8px !important;
            padding-right: 8px !important;
        }}
    }}
</style>
"""
st.markdown(responsive_css, unsafe_allow_html=True)

uploaded_file = None
if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader(
        "Upload banking CSV",
        type=["csv"],
        help="Include Month, Revenue, Transactions, Balance, Deposits, Loans, and NPS columns.",
    )


@st.cache_data(ttl=3600)
def generate_demo_data(n_points: int) -> pd.DataFrame:
    np.random.seed(42)
    # use monthly date labels to enable stable, consistent time-series behavior
    end_date = pd.Timestamp.today()
    dates = pd.to_datetime(
        [end_date - pd.DateOffset(months=i) for i in reversed(range(int(n_points)))]
    )
    df = pd.DataFrame(
        {
            "Month": dates.strftime("%Y-%m"),
            "Revenue": np.random.randint(120_000, 320_000, size=int(n_points)),
            "Transactions": np.random.randint(1_200, 4_500, size=int(n_points)),
            "Balance": np.random.randint(500_000, 1_200_000, size=int(n_points)),
            "Deposits": np.random.randint(200_000, 450_000, size=int(n_points)),
            "Loans": np.random.randint(100_000, 300_000, size=int(n_points)),
            "NPS": np.random.randint(20, 80, size=int(n_points)),
        }
    )
    return df


def load_uploaded_csv(uploaded) -> pd.DataFrame | None:
    try:
        df_local = pd.read_csv(uploaded)
        # normalize Month column if present
        if "Month" in df_local.columns:
            try:
                df_local["Month"] = pd.to_datetime(df_local["Month"]).dt.strftime("%Y-%m")
            except Exception:
                df_local["Month"] = df_local["Month"].astype(str)
        return df_local
    except Exception as exc:
        st.sidebar.warning(f"Upload failed: {exc}. Using demo data instead.")
        return None


@st.cache_data(ttl=600)
def make_plot(df: pd.DataFrame, chart_type: str, selected_theme: dict):
    if chart_type == "Revenue & Balance":
        fig = px.line(
            df,
            x="Month",
            y=["Revenue", "Balance"],
            labels={"value": "Amount (GHS)", "variable": "Metric"},
            title="Revenue and Balance Trend",
        )
    elif chart_type == "Transaction Volume":
        fig = px.bar(
            df,
            x="Month",
            y="Transactions",
            title="Monthly Transaction Volume",
            labels={"Transactions": "Transactions"},
            color_discrete_sequence=[selected_theme["primary"]],
        )
    else:
        fig = px.line(
            df,
            x="Month",
            y=["Loans", "Deposits"],
            labels={"value": "Amount (GHS)", "variable": "Metric"},
            title="Loan and Deposit Growth",
        )
    fig.update_traces(line=dict(color=selected_theme["primary"]), selector=dict(mode="lines"))
    fig.update_layout(
        height=520,
        margin=dict(l=10, r=10, t=45, b=10),
        template=selected_theme["template"],
    )
    return fig


df = None
if uploaded_file is not None:
    df = load_uploaded_csv(uploaded_file)

if df is None:
    df = generate_demo_data(n_points)

if name:
    st.success(
        f"Welcome, **{name}** — reviewing banking performance for **{role}** in **{office}**."
    )

revenue_total = int(df["Revenue"].sum())
avg_transactions = int(df["Transactions"].mean())
peak_revenue = int(df["Revenue"].max())
peak_month = df.loc[df["Revenue"].idxmax(), "Month"]
deposit_total = int(df["Deposits"].sum())
loan_total = int(df["Loans"].sum())
avg_nps = df["NPS"].mean().round(1)
loan_deposit_ratio = loan_total / deposit_total if deposit_total else 0
revenue_growth = ((df["Revenue"].iloc[-1] - df["Revenue"].iloc[-2]) / df["Revenue"].iloc[-2]) * 100 if len(df) > 1 else 0
deposit_growth = ((df["Deposits"].iloc[-1] - df["Deposits"].iloc[-2]) / df["Deposits"].iloc[-2]) * 100 if len(df) > 1 else 0
nps_trend = df["NPS"].iloc[-1] - df["NPS"].iloc[-2] if len(df) > 1 else 0

st.markdown(f"<h3 style='color: {selected_theme['primary']}; border-left: 5px solid {selected_theme['accent']}; padding-left: 10px;'>Executive Snapshot</h3>", unsafe_allow_html=True)
metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
metric_col1.metric("Total Revenue", f"GHS {revenue_total:,}", delta=f"{revenue_growth:.1f}%")
metric_col2.metric("Total Deposits", f"GHS {deposit_total:,}", delta=f"{deposit_growth:.1f}%")
metric_col3.metric("Total Loans", f"GHS {loan_total:,}")
metric_col4.metric("Avg NPS", f"{avg_nps}", delta=f"{nps_trend:+}")
metric_col5.metric("Loan/Deposit Ratio", f"{loan_deposit_ratio:.2f}")

# small tooltip icons (hover shows explanation)
metric_col1.markdown("<span title='Sum of Revenue for the selected reporting period'>ℹ️</span>", unsafe_allow_html=True)
metric_col2.markdown("<span title='Sum of all customer deposits recorded in the period'>ℹ️</span>", unsafe_allow_html=True)
metric_col3.markdown("<span title='Sum of loans outstanding in the reporting period'>ℹ️</span>", unsafe_allow_html=True)
metric_col4.markdown("<span title='Average Net Promoter Score (NPS) across reporting months'>ℹ️</span>", unsafe_allow_html=True)
metric_col5.markdown("<span title='Loan to deposit ratio (Loans / Deposits) — liquidity indicator'>ℹ️</span>", unsafe_allow_html=True)

st.markdown(f"<hr style='border-color: {selected_theme['accent']}; border-width: 2px;'>", unsafe_allow_html=True)

performance_tab, portfolio_tab, insights_tab = st.tabs([
    "Performance",
    "Portfolio",
    "Insights",
])

with performance_tab:
    st.markdown(f"<h3 style='color: {selected_theme['primary']}; border-left: 5px solid {selected_theme['accent']}; padding-left: 10px;'>Key Banking Performance</h3>", unsafe_allow_html=True)
    if chart_type == "Revenue & Balance":
        fig = px.line(
            df,
            x="Month",
            y=["Revenue", "Balance"],
            labels={"value": "Amount (GHS)", "variable": "Metric"},
            title="Revenue and Balance Trend",
        )
    elif chart_type == "Transaction Volume":
        fig = px.bar(
            df,
            x="Month",
            y="Transactions",
            title="Monthly Transaction Volume",
            labels={"Transactions": "Transactions"},
            color_discrete_sequence=[selected_theme["primary"]],
        )
    else:
        fig = px.line(
            df,
            x="Month",
            y=["Loans", "Deposits"],
            labels={"value": "Amount (GHS)", "variable": "Metric"},
            title="Loan and Deposit Growth",
        )
    fig.update_traces(line=dict(color=selected_theme["primary"]), selector=dict(mode="lines"))
    fig.update_layout(
        height=520,
        margin=dict(l=10, r=10, t=45, b=10),
        template=selected_theme["template"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"<h3 style='color: {selected_theme['primary']}; border-left: 5px solid {selected_theme['accent']}; padding-left: 10px;'>Balance and Customer Sentiment</h3>", unsafe_allow_html=True)
    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown(f"<p style='color: {selected_theme['secondary']}; font-weight: bold;'>Balance trend</p>", unsafe_allow_html=True)
        st.area_chart(df.set_index("Month")["Balance"])
    with right_col:
        st.markdown(f"<p style='color: {selected_theme['secondary']}; font-weight: bold;'>Customer satisfaction (NPS)</p>", unsafe_allow_html=True)
        st.line_chart(df.set_index("Month")["NPS"])

with portfolio_tab:
    st.markdown(f"<h3 style='color: {selected_theme['primary']}; border-left: 5px solid {selected_theme['accent']}; padding-left: 10px;'>Portfolio Health</h3>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color: {selected_theme['secondary']};'>This view demonstrates credit portfolio and deposit base performance — critical for bankers, risk managers, and analytics teams.</p>",
        unsafe_allow_html=True,
    )
    portfolio_col1, portfolio_col2 = st.columns(2)
    with portfolio_col1:
        st.metric("Average Loan Balance", f"GHS {int(df['Loans'].mean()):,}")
        st.metric("Average Deposit Balance", f"GHS {int(df['Deposits'].mean()):,}")
    with portfolio_col2:
        st.metric("Revenue per Transaction", f"GHS {int(df['Revenue'].sum() / df['Transactions'].sum()):,}")
        st.metric("Customer retention proxy", f"{avg_nps}%")

    st.markdown(f"<h3 style='color: {selected_theme['primary']}; border-left: 5px solid {selected_theme['accent']}; padding-left: 10px;'>Portfolio Charts</h3>", unsafe_allow_html=True)
    portfolio_chart = px.area(
        df,
        x="Month",
        y=["Deposits", "Loans"],
        labels={"value": "Amount (GHS)", "variable": "Portfolio"},
        title="Deposit vs Loan Book Evolution",
    )
    portfolio_chart.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=45, b=10),
        template=selected_theme["template"],
    )
    st.plotly_chart(portfolio_chart, use_container_width=True)

with insights_tab:
    st.markdown(f"<h3 style='color: {selected_theme['primary']}; border-left: 5px solid {selected_theme['accent']}; padding-left: 10px;'>Banking Insights</h3>", unsafe_allow_html=True)
    transaction_correlation = df["Revenue"].corr(df["Transactions"])
    deposit_growth_trend = df["Deposits"].pct_change().fillna(0).mean()
    loan_deposit_ratio_avg = df["Loans"].sum() / df["Deposits"].sum() if df["Deposits"].sum() else 0
    st.markdown(
        f"<p style='color: {selected_theme['secondary']};'>"
        f"- <b>Reporting months:</b> {len(df)}  <br>"
        f"- <b>Revenue range:</b> GHS {int(df['Revenue'].min()):,} to GHS {int(df['Revenue'].max()):,}  <br>"
        f"- <b>Deposit range:</b> GHS {int(df['Deposits'].min()):,} to GHS {int(df['Deposits'].max()):,}  <br>"
        f"- <b>Loan range:</b> GHS {int(df['Loans'].min()):,} to GHS {int(df['Loans'].max()):,}  <br>"
        f"- <b>Avg NPS:</b> {avg_nps}  <br>"
        f"- <b>Loan/Deposit ratio:</b> {loan_deposit_ratio_avg:.2f}  <br>"
        f"- <b>Revenue vs Transaction correlation:</b> {transaction_correlation:.2f}"
        f"</p>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<h3 style='color: {selected_theme['primary']}; border-left: 5px solid {selected_theme['accent']}; padding-left: 10px;'>Actionable Recommendations</h3>", unsafe_allow_html=True)
    st.markdown(
        f"<ul style='color: {selected_theme['secondary']};'>"
        f"<li>Ensure loan growth stays aligned with deposit growth to preserve liquidity.</li>"
        f"<li>Leverage NPS trends to improve digital banking and customer experience.</li>"
        f"<li>Highlight improvements in revenue efficiency and transaction performance for stakeholders.</li>"
        f"</ul>",
        unsafe_allow_html=True,
    )

st.markdown(f"<hr style='border-color: {selected_theme['accent']}; border-width: 2px;'>", unsafe_allow_html=True)
# Export buttons: CSV and dashboard snapshot (JSON)
csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
csv_bytes = csv_buffer.getvalue().encode('utf-8')

snapshot = {
    "exported_at": datetime.utcnow().isoformat() + "Z",
    "theme": "Default",
    "user": {"name": name, "role": role, "office": office},
    "data_preview": df.tail(10).to_dict(orient="records"),
}
snapshot_str = json.dumps(snapshot, indent=2, default=str)

export_col_l, export_col_m, export_col_r = st.columns([1, 2, 1])
with export_col_m:
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name=f"banking_data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download Snapshot (JSON)",
        data=snapshot_str,
        file_name=f"dashboard_snapshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
    )

st.markdown(f"<p style='text-align: center; color: {selected_theme['secondary']}; font-size: 12px;'>Built by Esther Ewurabena Appiah | appiahewurabena685@gmail.com | github.com/Ewura-bena685</p>", unsafe_allow_html=True)