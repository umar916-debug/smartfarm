import streamlit as st
import pandas as pd
import os
import json
from PIL import Image
from assets.images import farm_crop_images, farming_tech_images, agricultural_sensor_images
from utils.sheets_integration import authenticate_google_sheets, get_sheet_data

# --- Google Sheets Config ---
SPREADSHEET_ID = "1a4YMiZ2J9Qbvvy6jenTmYpy_w2dsnA4Tury36COAJCk"
SHEET_NAME = "Sheet1"
CREDENTIALS_JSON = ""  # KEEP THIS BLANK FOR MANUAL ENTRY

# Set page configuration
st.set_page_config(
    page_title="Smart Farming Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        color: #4CAF50;
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .block-container {
        padding-top: 2rem;
    }
    .stDataFrame {
        border: 1px solid #4CAF50;
        border-radius: 10px;
        overflow: hidden;
    }
    .metric-container {
        margin-bottom: 2rem;
    }
    .css-1d391kg {  /* Makes dataframe font larger */
        font-size: 16px !important;
    }
    .caption {
        text-align: center;
        color: #81C784;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and header image
st.markdown("<h1 class='main-header'>🌱 Smart Farming Dashboard</h1>", unsafe_allow_html=True)

try:
    image = Image.open("assets/smart_farming_latest.jpg")
    st.image(image, use_container_width=True)
    st.markdown("<div class='caption'>Smart Farming - High Quality Agriculture</div>", unsafe_allow_html=True)
except Exception as e:
    st.warning("Header image could not be loaded. Make sure the image is placed inside the 'assets/' folder.")

# Prompt user for credentials manually
with st.expander("🔐 Enter Google Sheets Credentials", expanded=True):
    USE_URL = st.toggle("Use Google Sheet URL instead of ID", value=False)
if USE_URL:
    SHEET_URL = st.text_input("Google Sheet URL")
    import re
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', SHEET_URL)
    SPREADSHEET_ID = match.group(1) if match else ""
    SHEET_NAME = st.text_input("Sheet Name", value=SHEET_NAME)
    CREDENTIALS_JSON = st.text_area("Google Service Account Credentials (JSON)", height=200)
else:
    SPREADSHEET_ID = st.text_input("Spreadsheet ID", value=SPREADSHEET_ID)
    SHEET_NAME = st.text_input("Sheet Name", value=SHEET_NAME)
    CREDENTIALS_JSON = st.text_area("Google Service Account Credentials (JSON)", height=200)

    if st.button("📅 Load Farm Data"):
        if not SPREADSHEET_ID or not SHEET_NAME or not CREDENTIALS_JSON:
            st.error("Please fill in all fields to continue.")
        else:
            try:
                with st.spinner("Connecting to Google Sheets and loading data..."):
                    service = authenticate_google_sheets(CREDENTIALS_JSON)
                    df = get_sheet_data(SPREADSHEET_ID, SHEET_NAME, CREDENTIALS_JSON)

                # ✅ Clean column names to ensure accurate matching
                df.columns = df.columns.str.strip().str.lower()

                if df is not None and not df.empty:
                    st.session_state["spreadsheet_id"] = SPREADSHEET_ID
                    st.session_state["sheet_name"] = SHEET_NAME
                    st.session_state["credentials_json"] = CREDENTIALS_JSON

                    latest = df.sort_values("timestamp", ascending=False).iloc[-1]

                    # Extract timestamp from latest row
                    timestamp_str = latest.get("timestamp")
                    try:
                        timestamp = pd.to_datetime(timestamp_str).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        timestamp = timestamp_str

                    st.markdown(f"""
                        <div style='font-size: 1.2rem; margin-top: 1rem; background-color: #f9f9f9; padding: 0.8rem 1rem; border-left: 5px solid #388e3c;'>
                            🕒 <strong>Last Updated:</strong>
                            <code style='background-color: #eef6f0; padding: 4px 8px; border-radius: 5px;'>""" + timestamp + """</code>
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🌡️ Temperature", f"{latest['temperature']} °C")
                    col2.metric("💧 Humidity", f"{latest['humidity']} %")
                    col3.metric("🧪 pH Level", latest['ph'])

                    col4, col5, col6 = st.columns(3)
                    col4.metric("🌿 Nitrogen (N)", latest['nitrogen'])
                    col5.metric("🌿 Phosphorus (P)", latest['phosphorus'])
                    col6.metric("🌿 Potassium (K)", latest['k'])
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.image(farming_tech_images[2], use_container_width=True, caption="Smart Farming Visualization")
                else:
                    st.error("Google Sheet is empty or couldn't be read. Check Sheet name and structure.")

            except Exception as e:
                st.error(f"Failed to load data: {e}")
