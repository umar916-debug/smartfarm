import streamlit as st
import pandas as pd
import plotly.express as px
from utils.sheets_integration import get_sheet_data
from io import StringIO
import datetime

# Set Streamlit page configuration
st.set_page_config(
    page_title="Historical Farm Data",
    page_icon="📈",
    layout="wide"
)

# Page Title
st.title("📈 Historical Farm Data Explorer")

# Google Sheets Connection Check
if 'google_sheets_configured' not in st.session_state or not st.session_state.google_sheets_configured:
    st.warning("⚠️ Google Sheets is not configured. Please return to the Home page and set it up.")
    st.page_link("app.py", label="⬅ Go to Home Page", icon="🏠")
    st.stop()

# Load data
try:
    with st.spinner("Loading data from Google Sheets..."):
        df = get_sheet_data(
            st.session_state.spreadsheet_id,
            st.session_state.sheet_name,
            st.session_state.credentials_json
        )

    if df is None or df.empty:
        st.error("No data available in your sheet.")
        st.stop()

    # Ensure 'timestamp' column exists and convert to datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
        df['timestamp'] = pd.date_range(end=pd.Timestamp.now(), periods=len(df), freq='H')

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filter Data")

        # Date range filter
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()

        date_range = st.date_input("Select Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        start_date, end_date = date_range if isinstance(date_range, tuple) else (min_date, max_date)

        # Sensor filter
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        selected_metrics = st.multiselect("Select Sensors", options=numeric_columns, default=numeric_columns[:3])

    # Filter data
    filtered_df = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]

    st.subheader("📊 Sensor Trend Visualization")

    if selected_metrics and not filtered_df.empty:
        fig = px.line(
            filtered_df,
            x='timestamp',
            y=selected_metrics,
            labels={'timestamp': 'Time', 'value': 'Reading', 'variable': 'Sensor'},
            title="Sensor Trends Over Time",
            markers=True
        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select sensors and a valid date range.")

    # Data Table
    st.subheader("📋 Filtered Raw Data")
    st.dataframe(filtered_df, use_container_width=True)

    # CSV Export
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"historical_data_{start_date}_to_{end_date}.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
