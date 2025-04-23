import streamlit as st
import pandas as pd
from utils.sheets_integration import get_sheet_data

# Config
st.set_page_config(page_title="Live Farm Sensor Dashboard", page_icon="🌿", layout="wide")

st.markdown("""
<h1 style='font-size: 3rem; font-weight: 700; color: #2e7d32;'>🌿 Live Farm Sensor Dashboard</h1>
<p style='font-size: 1.1rem; color: #ccc;'>Real-time sensor readings from your smart farm</p>
""", unsafe_allow_html=True)

# Check if connection is set
if not all(k in st.session_state for k in ("spreadsheet_id", "sheet_name", "credentials_json")):
    st.warning("⚠️ Please configure your Google Sheets connection on the Home page.")
    st.page_link("app.py", label="🏠 Go to Home Page")
    st.stop()

try:
    df = get_sheet_data(
        st.session_state["spreadsheet_id"],
        st.session_state["sheet_name"],
        st.session_state["credentials_json"]
    )

    if df is not None and not df.empty:
        # Normalize columns
        original_columns = df.columns.tolist()
        df.columns = df.columns.str.strip()
        col_map = {col.lower(): col for col in df.columns}
        latest = df.iloc[-1]

        # Timestamp
        timestamp_raw = latest.get(col_map.get("timestamp", ""), "Unknown")
        try:
            parsed_ts = pd.to_datetime(timestamp_raw)
            timestamp = parsed_ts.strftime("%Y-%m-%d %H:%M:%S")
        except:
            timestamp = "Unknown (timestamp column not found)"

        st.markdown(f"""
            <div style='margin-top: 1.5rem; padding: 1rem 1.5rem; border-left: 5px solid #4CAF50; background-color: #f0f4f0; border-radius: 8px; display: flex; align-items: center;'>
                <span style='font-size: 1.5rem; margin-right: 0.75rem;'>🕒</span>
                <span style='font-size: 1.2rem; font-weight: 600; color: #2e7d32;'>Last Updated:</span>
                <span style='margin-left: 1rem; font-size: 1.1rem; font-family: monospace; background-color: #e0f2e9; padding: 4px 10px; border-radius: 6px; color: #2e7d32;'>{timestamp}</span>
            </div>
        """, unsafe_allow_html=True)

        # Metrics
        def get_val(key, suffix=""):
            col = col_map.get(key.lower())
            return f"{latest[col]}{suffix}" if col and pd.notna(latest[col]) else "N/A"

        st.markdown("### 📊 Sensor Readings")
        c1, c2, c3 = st.columns(3)
        c1.metric("🌡️ Temperature", get_val("temperature", " °C"))
        c2.metric("💧 Humidity", get_val("humidity", " %"))
        c3.metric("🧪 pH Level", get_val("ph"))

        c4, c5, c6 = st.columns(3)
        c4.metric("🌿 Nitrogen (N)", get_val("n"))
        c5.metric("🌿 Phosphorus (P)", get_val("p"))
        c6.metric("🌿 Potassium (K)", get_val("k"))

        st.markdown("---")
        if st.button("🔄 Refresh Data"):
            st.rerun()
    else:
        st.error("No data found in your sheet. Make sure it's correctly formatted.")

except Exception as e:
    st.error(f"❌ Error fetching data: {e}")
