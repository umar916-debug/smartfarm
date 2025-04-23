import streamlit as st
import pandas as pd
import datetime
from utils.sheets_integration import get_sheet_data

# Set page configuration
st.set_page_config(
    page_title="Live Farm Data | Smart Farming",
    page_icon="📊",
    layout="wide"
)

# Inject custom CSS for styling
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        font-family: 'Segoe UI', sans-serif;
    }
    .metric-box {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
        text-align: center;
    }
    .metric-label {
        font-size: 1rem;
        font-weight: 600;
        color: #444;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: bold;
        color: #222;
    }
    .metric-delta {
        font-size: 0.9rem;
        color: #888;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Page title
st.title("📊 Live Farm Data Monitoring")

# Check if Google Sheets is configured
if 'google_sheets_configured' not in st.session_state or not st.session_state.google_sheets_configured:
    st.warning("⚠️ Google Sheets connection not configured. Please go to the home page to set up your connection.")
    st.page_link("app.py", label="Go to Home Page", icon="🏠")
else:
    try:
        with st.spinner("Fetching latest data from Google Sheets..."):
            df = get_sheet_data(
                st.session_state.spreadsheet_id,
                st.session_state.sheet_name,
                st.session_state.credentials_json
            )

            if df is not None and not df.empty:
                latest_data = df.iloc[-1].to_dict()

                # Timestamp
                timestamp = latest_data.get('timestamp', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                st.subheader(f"🕒 Last Updated: {timestamp}")

                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                if 'timestamp' in numeric_cols:
                    numeric_cols.remove('timestamp')

                metric_info = {
                    'temperature': {'unit': '°C', 'good_range': (15, 30), 'icon': '🌡️'},
                    'humidity': {'unit': '%', 'good_range': (40, 80), 'icon': '💧'},
                    'soil_moisture': {'unit': '%', 'good_range': (30, 70), 'icon': '🌱'},
                    'light_intensity': {'unit': 'lux', 'good_range': (10000, 50000), 'icon': '☀️'},
                    'ph': {'unit': 'pH', 'good_range': (5.5, 7.5), 'icon': '⚗️'},
                    'nitrogen': {'unit': 'mg/kg', 'good_range': (150, 300), 'icon': 'N'},
                    'phosphorus': {'unit': 'mg/kg', 'good_range': (25, 50), 'icon': 'P'},
                    'potassium': {'unit': 'mg/kg', 'good_range': (150, 300), 'icon': 'K'},
                }

                column_display_map = {
                    'temp': 'temperature',
                    'hum': 'humidity',
                    'soil_moist': 'soil_moisture',
                    'light': 'light_intensity',
                    'n': 'nitrogen',
                    'p': 'phosphorus',
                    'k': 'potassium'
                }

                metric_cols = st.columns(min(4, len(numeric_cols)))
                for i, col_name in enumerate(numeric_cols):
                    display_name = column_display_map.get(col_name, col_name)
                    info = metric_info.get(display_name, {'unit': '', 'good_range': (0, 100), 'icon': '📊'})
                    value = latest_data.get(col_name, 'N/A')

                    if isinstance(value, (int, float)):
                        formatted_value = f"{value} {info['unit']}"
                        if value < info['good_range'][0] or value > info['good_range'][1]:
                            delta_color = "inverse"
                            delta_desc = "Out of range"
                        else:
                            delta_color = "normal"
                            delta_desc = "Optimal range"
                        if len(df) > 1:
                            prev_value = df.iloc[-2][col_name]
                            delta = f"{value - prev_value:+.2f} {info['unit']}"
                        else:
                            delta = None
                    else:
                        formatted_value = str(value)
                        delta = None
                        delta_color = "off"
                        delta_desc = ""

                    with metric_cols[i % len(metric_cols)]:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="metric-label">{info['icon']} {display_name.replace('_', ' ').title()}</div>
                            <div class="metric-value">{formatted_value}</div>
                            <div class="metric-delta">{delta or ''} <span style='color: gray;'>({delta_desc})</span></div>
                        </div>
                        """, unsafe_allow_html=True)

                # Refresh button
                if st.button("🔄 Refresh Data"):
                    st.rerun()

            else:
                st.error("No data found. Please check your Google Sheet configuration.")

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
