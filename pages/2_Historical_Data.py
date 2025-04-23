import streamlit as st
import pandas as pd
import plotly.express as px
from utils.sheets_integration import get_sheet_data
from utils.data_processing import process_historical_data
from assets.images import farm_crop_images

# Page setup
st.set_page_config(page_title="Farm Data Graph | Smart Farming", page_icon="📈", layout="wide")
st.title("📈 Farm Data Visualization")

if st.button("🔄 Refresh Data"):
    st.experimental_rerun()

# Google Sheets check
if 'google_sheets_configured' not in st.session_state or not st.session_state.google_sheets_configured:
    st.warning("⚠️ Google Sheets not configured. Go to home to set it up.")
    st.page_link("app.py", label="Go to Home Page", icon="🏠")
else:
    df = get_sheet_data(
        st.session_state.spreadsheet_id,
        st.session_state.sheet_name,
        st.session_state.credentials_json
    )
    hist_df = process_historical_data(df)
    hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'], utc=True).dt.tz_convert('Asia/Kolkata')

    st.subheader("Filter Data")
    min_date = hist_df['timestamp'].min().date()
    max_date = hist_df['timestamp'].max().date()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

    filtered_df = hist_df[
        (hist_df['timestamp'].dt.date >= start_date) & 
        (hist_df['timestamp'].dt.date <= end_date)
    ]

    st.success(f"{len(filtered_df)} records from {start_date} to {end_date}")

    numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    selected_metrics = st.multiselect("Select metrics to plot", numeric_cols, default=numeric_cols[:3])

    if selected_metrics:
        fig = px.line(
            filtered_df,
            x='timestamp',
            y=selected_metrics,
            title="Time Series of Selected Farm Metrics",
            labels={"timestamp": "Time", "value": "Value", "variable": "Metric"}
        )
        st.plotly_chart(fig, use_container_width=True)

        st.download_button(
            "Download Selected Data as CSV",
            data=filtered_df[selected_metrics].to_csv(index=False),
            file_name="selected_metrics.csv",
            mime="text/csv"
        )
    else:
        st.info("Select at least one metric to display.")
