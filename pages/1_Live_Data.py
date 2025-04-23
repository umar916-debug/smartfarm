import streamlit as st
import pandas as pd
import datetime
from utils.sheets_integration import get_sheet_data

# Page config
st.set_page_config(page_title="Live Farm Data | Smart Farming", page_icon="📊", layout="wide")

st.markdown("""
<h1 style='font-size: 3rem; font-weight: 700; color: #2e7d32;'>🌿 Live Farm Sensor Dashboard</h1>
<p style='font-size: 1.1rem; color: #ccc;'>Real-time sensor readings from your smart farm</p>
""", unsafe_allow_html=True)

# Check connection
if not all(k in st.session_state for k in ("spreadsheet_id", "sheet_name", "credentials_json")):
    st.warning("⚠️ Google Sheets not connected. Please configure it on the Home page.")
    st.page_link("app.py", label="🏠 Go to Home Page")
    st.stop()

try:
    df = get_sheet_data(
        st.session_state["spreadsheet_id"],
        st.session_state["sheet_name"],
        st.session_state["credentials_json"]
    )

    if df is not None and not df.empty:
        latest_data = df.iloc[-1].to_dict()

        # Timestamp
        timestamp = latest_data.get('Timestamp') or latest_data.get('timestamp') or "Unknown"
        try:
            timestamp = pd.to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass

        st.markdown(f"""
            <div style='margin-top: 1.5rem; padding: 1rem 1.5rem; border-left: 5px solid #4CAF50; background-color: #f0f4f0; border-radius: 8px; display: flex; align-items: center;'>
                <span style='font-size: 1.5rem; margin-right: 0.75rem;'>🕒</span>
                <span style='font-size: 1.2rem; font-weight: 600; color: #2e7d32;'>Last Updated:</span>
                <span style='margin-left: 1rem; font-size: 1.1rem; font-family: monospace; background-color: #e0f2e9; padding: 4px 10px; border-radius: 6px; color: #2e7d32;'>{timestamp}</span>
            </div>
        """, unsafe_allow_html=True)

        # Metrics
        def val(key, suffix=""):
            v = latest_data.get(key)
            return f"{v} {suffix}" if pd.notna(v) else "N/A"

        c1, c2, c3 = st.columns(3)
        c1.metric("🌡️ Temperature", val("Temperature", "°C"))
        c2.metric("💧 Humidity", val("Humidity", "%"))
        c3.metric("🧪 pH Level", val("pH"))

        c4, c5, c6 = st.columns(3)
        c4.metric("🌿 Nitrogen (N)", val("N"))
        c5.metric("🌿 Phosphorus (P)", val("P"))
        c6.metric("🌿 Potassium (K)", val("K"))

        if st.button("🔄 Refresh Data"):
            st.rerun()
    else:
        st.error("No data found. Please check your Google Sheet structure.")

except Exception as e:
    st.error(f"❌ Error: {e}")
