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

st.markdown("""
<h1 style='font-size: 3rem; font-weight: 700; color: #2e7d32;'>🌿 Live Farm Sensor Dashboard</h1>
<p style='font-size: 1.1rem; color: #ccc;'>Real-time sensor readings from your smart farm</p>
""", unsafe_allow_html=True)

# ✅ Validate connection state
if not all(k in st.session_state for k in ("spreadsheet_id", "sheet_name", "credentials_json")):
    st.warning("⚠️ Google Sheets connection not configured. Please go to the home page to set up your connection.")
    st.page_link("app.py", label="🏠 Go to Home Page")
    st.stop()

# ✅ Fetch latest data
try:
    with st.spinner("Fetching the latest farm data..."):
        df = get_sheet_data(
            st.session_state["spreadsheet_id"],
            st.session_state["sheet_name"],
            st.session_state["credentials_json"]
        )

    if df is not None and not df.empty:
        latest = df.sort_values("timestamp", ascending=False).iloc[-1]

        # ✅ Extract timestamp from sheet
        timestamp_str = latest.get("timestamp")
        try:
            timestamp = pd.to_datetime(timestamp_str).strftime('%Y-%m-%d %H:%M:%S')
        except:
            timestamp = timestamp_str

        st.markdown(f"""
            <div style='font-size: 1.2rem; margin-top: 1rem; background-color: #f9f9f9; padding: 0.8rem 1rem; border-left: 5px solid #388e3c;'>
                🕒 <strong>Last Updated:</strong>
                <code style='background-color: #eef6f0; padding: 4px 8px; border-radius: 5px;'>{timestamp}</code>
            </div>
        """, unsafe_allow_html=True)

        # ✅ Display key metrics
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("🌡️ Temperature", f"{latest['temperature']} °C")
        col2.metric("💧 Humidity", f"{latest['humidity']} %")
        col3.metric("🧪 pH Level", latest['ph'])

        col4, col5, col6 = st.columns(3)
        col4.metric("🌿 Nitrogen (N)", latest['nitrogen'])
        col5.metric("🌿 Phosphorus (P)", latest['phosphorus'])
        col6.metric("🌿 Potassium (K)", latest['potassium'])
        st.markdown("</div>", unsafe_allow_html=True)

        st.button("🔄 Refresh Data", on_click=st.experimental_rerun)

    else:
        st.error("No data found. Please check your Google Sheet configuration.")

except Exception as e:
    st.error(f"❌ Error fetching data: {str(e)}")
