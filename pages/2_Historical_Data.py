import streamlit as st
import pandas as pd
import plotly.express as px
from utils.sheets_integration import get_sheet_data

st.set_page_config(page_title="Historical Data", layout="wide")
st.title("📈 Historical Farm Data Trends")

if 'google_sheets_configured' not in st.session_state or not st.session_state.google_sheets_configured:
    st.warning("⚠️ Google Sheets connection not configured. Please go to the home page to set up your connection.")
    st.page_link("app.py", label="Go to Home Page", icon="🏠")
else:
    try:
        with st.spinner("Loading historical data..."):
            df = get_sheet_data(
                st.session_state.spreadsheet_id,
                st.session_state.sheet_name,
                st.session_state.credentials_json
            )

            if df is not None and not df.empty:
                # Handle timestamp
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                    df = df.dropna(subset=['timestamp'])
                    df.set_index('timestamp', inplace=True)
                else:
                    df.index = pd.date_range(end=pd.Timestamp.now(), periods=len(df), freq='h')

                # Only numeric columns
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

                # Trend Chart
                st.subheader("📊 Sensor Trend Over Time")
                selected = st.multiselect("Select metrics to plot", options=numeric_cols, default=numeric_cols[:3])
                if selected:
                    fig = px.line(df, y=selected, markers=True)
                    fig.update_layout(
                        title="Sensor Data Over Time",
                        xaxis_title="Time",
                        yaxis_title="Measurement",
                        legend_title="Metric",
                        height=450
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Please select one or more metrics to display the graph.")
            else:
                st.error("No historical data available.")
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
