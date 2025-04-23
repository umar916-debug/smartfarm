import streamlit as st
import pandas as pd
from utils.sheets_integration import get_sheet_data

# Page config
st.set_page_config(
    page_title="Live Farm Data | Smart Farming",
    page_icon="📊",
    layout="wide"
)

# Title
st.markdown("""
<h1 style='font-size: 3rem; font-weight: 700; color: #2e7d32;'>🌿 Live Farm Sensor Dashboard</h1>
<p style='font-size: 1.1rem; color: #ccc;'>Real-time sensor readings from your smart farm</p>
""", unsafe_allow_html=True)

# Check session state
if not all(k in st.session_state for k in ("spreadsheet_id", "sheet_name", "credentials_json")):
    st.warning("⚠️ Google Sheets connection not configured. Please go to the home page to set up your connection.")
    st.page_link("app.py", label="🏠 Go to Home Page")
    st.stop()

# Fetch data
try:
    with st.spinner("Fetching the latest farm data..."):
        df = get_sheet_data(
            st.session_state["spreadsheet_id"],
            st.session_state["sheet_name"],
            st.session_state["credentials_json"]
        )

    if df is not None and not df.empty:
        # Normalize columns
        df.columns = df.columns.str.strip().str.lower()
        latest = df.iloc[-1]

        # Get timestamp (optional)
        timestamp_str = latest.get("timestamp", "Unknown")
        try:
            timestamp = pd.to_datetime(timestamp_str).strftime('%Y-%m-%d %H:%M:%S')
        except:
            timestamp = timestamp_str

        # Timestamp display
        st.markdown(f"""
            <div style='font-size: 1.2rem; margin-top: 1rem; background-color: #f9f9f9; padding: 0.8rem 1rem; border-left: 5px solid #388e3c;'>
                🕒 <strong>Last Updated:</strong>
                <code style='background-color: #eef6f0; padding: 4px 8px; border-radius: 5px;'>{timestamp}</code>
            </div>
        """, unsafe_allow_html=True)

        # Metrics
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("🌡️ Temperature", f"{latest.get('temperature', 'N/A')} °C")
        col2.metric("💧 Humidity", f"{latest.get('humidity', 'N/A')} %")
        col3.metric("🧪 pH Level", latest.get('ph', 'N/A'))

        col4, col5, col6 = st.columns(3)
        col4.metric("🌿 Nitrogen (N)", latest.get('n', 'N/A'))
        col5.metric("🌿 Phosphorus (P)", latest.get('p', 'N/A'))
        col6.metric("🌿 Potassium (K)", latest.get('k', 'N/A'))
        st.markdown("</div>", unsafe_allow_html=True)

        # Refresh
        if st.button("🔄 Refresh Data"):
            st.rerun()

    else:
        st.error("No data found in your Google Sheet.")

except Exception as e:
    st.error(f"❌ Error fetching data: {str(e)}")
