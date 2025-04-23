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

# Page title
st.markdown("""
    <h1 style='font-size: 2.8rem;'>🌿 Live Farm Sensor Dashboard</h1>
    <p style='font-size: 1.1rem; color: gray;'>Real-time sensor readings from your smart farm</p>
""", unsafe_allow_html=True)

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
        timestamp_str = latest_data.get('timestamp')
        if timestamp_str:
            try:
                parsed_timestamp = pd.to_datetime(timestamp_str, utc=True)
                timestamp = parsed_timestamp.tz_convert("Asia/Kolkata").strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp = timestamp_str
        else:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        st.markdown(f"""
            <div style='font-size: 1.2rem; margin-top: 1rem;'>
                🕒 <strong>Last Updated:</strong>
                <code style='background-color: #f0f0f0; padding: 4px 8px; border-radius: 5px;'>{timestamp}</code>
            </div>
        """, unsafe_allow_html=True)

        # Display metrics in a grid layout
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

        st.markdown("""<hr style='margin-top: 1rem; margin-bottom: 1.5rem;'>""", unsafe_allow_html=True)

        col_chunks = [numeric_cols[i:i + 3] for i in range(0, len(numeric_cols), 3)]
        for chunk in col_chunks:
            cols = st.columns(len(chunk))
            for i, col_name in enumerate(chunk):
                name = alias_map.get(col_name, col_name)
                info = metric_info.get(name, {'unit': '', 'range': (0, 100), 'icon': '📊'})
                value = latest_data.get(col_name, 'N/A')

                if isinstance(value, (int, float)):
                    formatted = f"{value} {info['unit']}"
                    delta = None
                    if len(df) > 1:
                        delta_val = value - df.iloc[-2][col_name]
                        delta = f"{delta_val:+.2f} {info['unit']}"
                else:
                    formatted = str(value)
                    delta = None

                with cols[i]:
                    st.metric(
                        label=f"{info['icon']} {name.replace('_', ' ').title()}",
                        value=formatted,
                        delta=delta,
                        help=f"Optimal: {info['range'][0]} - {info['range'][1]} {info['unit']}"
                    )

        st.markdown("""<hr style='margin-top: 1.5rem;'>""", unsafe_allow_html=True)
        st.button("🔄 Refresh Data", on_click=lambda: st.experimental_rerun())

    else:
        st.error("No data found. Please check your Google Sheet configuration.")

except Exception as e:
    st.error(f"❌ Error fetching data: {str(e)}")

# Footer Info
st.markdown("""<hr style='margin-top: 2rem;'>""", unsafe_allow_html=True)
with st.expander("ℹ️ About This Dashboard"):
    st.markdown("""
    This dashboard displays the most recent sensor data from your connected smart farming system. 

    - 📡 The data is pulled directly from your configured Google Sheet.
    - 📈 Metrics show their optimal ranges to help you interpret the readings.
    - 🔄 Click the refresh button anytime to get the latest updates.
    """)
