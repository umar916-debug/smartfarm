import streamlit as st
import pandas as pd
from utils.sheets_integration import get_sheet_data

# Page setup
st.set_page_config(page_title="Live Farm Data", page_icon="🌾", layout="wide")

st.markdown("""
<h1 style='font-size: 2.5rem; font-weight: 700; color: #2e7d32;'>🌾 Live Farm Sensor Dashboard</h1>
<p style='font-size: 1.1rem; color: #aaa;'>Real-time data pulled from Google Sheets connected to your farm sensors.</p>
""", unsafe_allow_html=True)

# Check if sheet is connected
if not all(k in st.session_state for k in ("spreadsheet_id", "sheet_name", "credentials_json")):
    st.warning("⚠️ Google Sheets not configured. Please return to the homepage to set it up.")
    st.page_link("app.py", label="🏠 Go to Home")
    st.stop()

try:
    df = get_sheet_data(
        st.session_state["spreadsheet_id"],
        st.session_state["sheet_name"],
        st.session_state["credentials_json"]
    )

    if df is not None and not df.empty:
        # Get latest row
        latest_data = df.iloc[-1].to_dict()

        # Timestamp
        timestamp = latest_data.get("Timestamp") or latest_data.get("timestamp") or "Unknown"
        try:
            timestamp = pd.to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except:
            pass

        # Timestamp display
        st.markdown(f"""
        <div style='margin: 1.5rem 0; padding: 1rem 1.5rem; border-left: 5px solid #4CAF50;
                    background-color: #f0f4f0; border-radius: 8px; display: flex; align-items: center;'>
            <span style='font-size: 1.3rem; color: #2e7d32; font-weight: 600;'>🕒 Last Updated:</span>
            <span style='margin-left: 1rem; font-size: 1.1rem; font-family: monospace;
                         background-color: #e0f2e9; padding: 6px 12px; border-radius: 6px; color: #2e7d32;'>{timestamp}</span>
        </div>
        """, unsafe_allow_html=True)

        # Metrics
        def get_val(key, unit=""):
            val = latest_data.get(key)
            return f"{val} {unit}" if pd.notna(val) else "N/A"

        col1, col2, col3 = st.columns(3)
        col1.metric("🌡️ Temperature", get_val("Temperature", "°C"))
        col2.metric("💧 Humidity", get_val("Humidity", "%"))
        col3.metric("🧪 pH", get_val("pH"))

        col4, col5, col6 = st.columns(3)
        col4.metric("🟢 Nitrogen (N)", get_val("N"))
        col5.metric("🟣 Phosphorus (P)", get_val("P"))
        col6.metric("🟠 Potassium (K)", get_val("K"))

        # Refresh Button
        if st.button("🔄 Refresh Now"):
            st.rerun()

    else:
        st.error("❌ No data found in your sheet.")

except Exception as e:
    st.error(f"❌ Error fetching data: {e}")
