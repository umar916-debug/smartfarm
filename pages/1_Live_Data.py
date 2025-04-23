import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from utils.sheets_integration import get_sheet_data
from assets.images import agricultural_sensor_images, farming_tech_images

# Set page configuration
st.set_page_config(
    page_title="Live Farm Data | Smart Farming",
    page_icon="📊",
    layout="wide"
)

# Page title
st.title("🌿 Live Farm Sensor Dashboard")
st.caption("Real-time sensor readings from your smart farm")

# Check Google Sheets config
if 'google_sheets_configured' not in st.session_state or not st.session_state.google_sheets_configured:
    st.warning("⚠️ Google Sheets connection not configured. Please go to the home page to set up your connection.")
    st.page_link("app.py", label="🏠 Go to Home Page")
    st.stop()

# Fetch data from Google Sheets
try:
    with st.spinner("Fetching the latest farm data..."):
        df = get_sheet_data(
            st.session_state.spreadsheet_id,
            st.session_state.sheet_name,
            st.session_state.credentials_json
        )

    if df is not None and not df.empty:
        latest_data = df.iloc[-1].to_dict()

        # Display last updated timestamp
        timestamp = latest_data.get('timestamp', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        st.markdown(f"#### 🕒 Last Updated: `{timestamp}`")

        # Display layout: sensor image + metrics
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(agricultural_sensor_images[0], use_container_width=True, caption="Farm Sensor Overview")

        with col2:
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            if 'timestamp' in numeric_cols:
                numeric_cols.remove('timestamp')

            metric_info = {
                'temperature': {'unit': '°C', 'range': (15, 30), 'icon': '🌡️'},
                'humidity': {'unit': '%', 'range': (40, 80), 'icon': '💧'},
                'soil_moisture': {'unit': '%', 'range': (30, 70), 'icon': '🌱'},
                'light_intensity': {'unit': 'lux', 'range': (10000, 50000), 'icon': '☀️'},
                'ph': {'unit': 'pH', 'range': (5.5, 7.5), 'icon': '⚗️'},
                'nitrogen': {'unit': 'mg/kg', 'range': (150, 300), 'icon': '🅝'},
                'phosphorus': {'unit': 'mg/kg', 'range': (25, 50), 'icon': '🅟'},
                'potassium': {'unit': 'mg/kg', 'range': (150, 300), 'icon': '🅚'},
                'rainfall': {'unit': 'mm', 'range': (900, 1400), 'icon': '🌧️'},
            }

            alias_map = {
                'temp': 'temperature',
                'hum': 'humidity',
                'soil_moist': 'soil_moisture',
                'light': 'light_intensity',
                'n': 'nitrogen',
                'p': 'phosphorus',
                'k': 'potassium',
                'rain': 'rainfall'
            }

            metric_cols = st.columns(min(4, len(numeric_cols)))
            for i, col_name in enumerate(numeric_cols):
                name = alias_map.get(col_name, col_name)
                info = metric_info.get(name, {'unit': '', 'range': (0, 100), 'icon': '📊'})
                value = latest_data.get(col_name, 'N/A')

                if isinstance(value, (int, float)):
                    formatted = f"{value} {info['unit']}"
                    optimal = info['range'][0] <= value <= info['range'][1]
                    delta = None
                    if len(df) > 1:
                        delta_val = value - df.iloc[-2][col_name]
                        delta = f"{delta_val:+.2f} {info['unit']}"
                else:
                    formatted = str(value)
                    delta = None

                with metric_cols[i % len(metric_cols)]:
                    st.metric(
                        label=f"{info['icon']} {name.replace('_', ' ').title()}",
                        value=formatted,
                        delta=delta,
                        help=f"Optimal: {info['range'][0]} - {info['range'][1]} {info['unit']}"
                    )

        # Refresh Button
        st.divider()
        st.button("🔄 Refresh Data", on_click=st.rerun)

    else:
        st.error("No data found. Please check your Google Sheet configuration.")
        st.image(farming_tech_images[1], caption="Smart Farming System", use_container_width=True)

except Exception as e:
    st.error(f"❌ Error fetching data: {str(e)}")
    st.image(farming_tech_images[1], caption="Smart Farming System", use_container_width=True)

# Footer Info
st.divider()
with st.expander("ℹ️ About This Dashboard"):
    st.markdown("""
    This dashboard displays the most recent sensor data from your connected smart farming system. 

    - 📡 The data is pulled directly from your configured Google Sheet.
    - 📈 Metrics show their optimal ranges to help you interpret the readings.
    - 🔄 Click the refresh button anytime to get the latest updates.
    """)
