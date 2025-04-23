import streamlit as st
import pandas as pd
from utils.sheets_integration import get_sheet_data

# Page config
st.set_page_config(
    page_title="Live Farm Data | Smart Farming",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<h1 style='font-size: 3rem; font-weight: 700; color: #2e7d32;'>🌿 Live Farm Sensor Dashboard</h1>
<p style='font-size: 1.1rem; color: #ccc;'>Real-time sensor readings from your smart farm</p>
""", unsafe_allow_html=True)

# Google Sheets connection check
if not all(k in st.session_state for k in ("spreadsheet_id", "sheet_name", "credentials_json")):
    st.warning("⚠️ Google Sheets connection not configured. Please go to the home page to set up your connection.")
    st.page_link("app.py", label="🏠 Go to Home Page")
    st.stop()

# Try fetching and displaying data
try:
    with st.spinner("Fetching the latest farm data..."):
        df = get_sheet_data(
            st.session_state["spreadsheet_id"],
            st.session_state["sheet_name"],
            st.session_state["credentials_json"]
        )

    if df is not None and not df.empty:
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()

        latest = df.iloc[-1]

        # --- TIMESTAMP display ---
        timestamp_str = latest.get("timestamp", "Unknown")
        try:
            parsed_timestamp = pd.to_datetime(timestamp_str)
            timestamp = parsed_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except:
            timestamp = "Unknown (timestamp format error)"

        st.markdown(f"""
            <div style='display: flex; align-items: center; margin-top: 1.5rem; padding: 1rem 1.5rem; border-left: 5px solid #4CAF50; background-color: #f0f4f0; border-radius: 8px;'>
                <span style='font-size: 1.5rem; margin-right: 0.75rem;'>🕒</span>
                <span style='font-size: 1.2rem; font-weight: 600; color: #2e7d32;'>Last Updated:</span>
                <span style='margin-left: 1rem; font-size: 1.1rem; font-family: monospace; background-color: #e0f2e9; padding: 4px 10px; border-radius: 6px; color: #2e7d32;'>{timestamp}</span>
            </div>
        """, unsafe_allow_html=True)

        # --- METRICS display ---
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

        # --- REFRESH BUTTON ---
        if st.button("🔄 Refresh Data"):
            st.experimental_rerun()  # safe to use for now, works until st.rerun is public

    else:
        st.error("No data found in your Google Sheet.")

except Exception as e:
    st.error(f"❌ Error fetching data: {str(e)}")
