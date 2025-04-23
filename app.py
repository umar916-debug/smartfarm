import streamlit as st
import pandas as pd
import os
import json
from assets.images import IoT-in-Agriculture-scaled, farming_tech_images, agricultural_sensor_images
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
        margin-bottom: 1rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .metric-title {
        font-size: 1.1rem;
        font-weight: 500;
        color: #81C784;
    }
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and header image
st.markdown("<h1 class='main-header'>🌱 Smart Farming Dashboard</h1>", unsafe_allow_html=True)
from PIL import Image

try:
    image = Image.open("IoT-in-Agriculture-scaled.jpg")
    st.image(image, use_container_width=True, caption="Smart Farming - High Quality Agriculture")
except Exception as e:
    st.warning("Header image could not be loaded. Make sure the image is present in the app folder.")

# Prompt user for credentials manually
with st.expander("🔐 Enter Google Sheets Credentials", expanded=True):
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

                if df is not None and not df.empty:
                    st.success("Data loaded successfully from Google Sheets")
                    st.image(farming_tech_images[1], use_container_width=True, caption="Live Sensor Feed")
                    st.dataframe(df.head(), use_container_width=True)

                    st.markdown("<h3 style='color:#4CAF50;'>📊 Latest Farm Data</h3>", unsafe_allow_html=True)
                    latest = df.sort_values("timestamp", ascending=False).iloc[0]

                    col1, col2, col3 = st.columns(3)
                    col1.metric("🌡️ Temperature", f"{latest['temperature']} °C")
                    col2.metric("💧 Humidity", f"{latest['humidity']} %")
                    col3.metric("🧪 pH Level", latest['ph'])

                    col4, col5, col6 = st.columns(3)
                    col4.metric("🌿 Nitrogen (N)", latest['nitrogen'])
                    col5.metric("🌿 Phosphorus (P)", latest['phosphorus'])
                    col6.metric("🌿 Potassium (K)", latest['potassium'])

                    st.image(farming_tech_images[2], use_container_width=True, caption="Smart Farming Visualization")
                else:
                    st.error("Google Sheet is empty or couldn't be read. Check Sheet name and structure.")

            except Exception as e:
                st.error(f"Failed to load data: {e}")
