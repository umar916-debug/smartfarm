import streamlit as st
import pandas as pd
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from utils.sheets_integration import authenticate_google_sheets
from assets.images import farm_crop_images, agricultural_sensor_images

def get_sheet_data(spreadsheet_id, sheet_name, credentials_json):
    try:
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]

        if isinstance(credentials_json, str):
            credentials_json = json.loads(credentials_json)

        creds = Credentials.from_service_account_info(credentials_json, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
        records = sheet.get_all_records()
        df = pd.DataFrame(records)

        required_columns = ['Timestamp', 'Temperature', 'Humidity', 'N', 'P', 'K', 'pH']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Missing required columns. Found: {df.columns.tolist()}")
            return None

        return df[required_columns]

    except Exception as e:
        st.error(f"Error fetching sheet data: {str(e)}")
        return None

# Streamlit config
st.set_page_config(
    page_title="Smart Farming Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #4CAF50;
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .subheader {
        color: #81C784;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 4px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🌱 Smart Farming Dashboard</h1>", unsafe_allow_html=True)

# Introduction
st.markdown("""
<div style='background-color: #2d2d2d; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;'>
<p style='font-size: 1.1rem;'>Welcome to the Smart Farming Dashboard - your hub for real-time monitoring, analysis, and crop recommendations.</p>
<ul>
  <li><b style='color:#81C784;'>Live monitoring</b> from sensors</li>
  <li><b style='color:#81C784;'>Historical trends</b> analysis</li>
  <li><b style='color:#81C784;'>AI crop recommendations</b></li>
</ul>
</div>
""", unsafe_allow_html=True)

st.image(farm_crop_images[0], use_container_width=True)

st.markdown("<h2 style='text-align: center; color: #4CAF50;'>Key Features</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background:#2d2d2d; padding: 20px; border-radius: 10px; text-align:center;'>
        <h3 style='color: #4CAF50;'>📊 Live Monitoring</h3>
        <p>Real-time sensor data on temperature, humidity, and nutrients.</p>
        <a href='./pages/1_Live_Data.py'><button>Go to Live Data</button></a>
    </div>
    """, unsafe_allow_html=True)
    st.image(agricultural_sensor_images[0], use_container_width=True)

with col2:
    st.markdown("""
    <div style='background:#2d2d2d; padding: 20px; border-radius: 10px; text-align:center;'>
        <h3 style='color: #4CAF50;'>📈 Historical Analysis</h3>
        <p>Trends and patterns over time to improve farming efficiency.</p>
        <a href='./pages/2_Historical_Data.py'><button>View Historical Data</button></a>
    </div>
    """, unsafe_allow_html=True)
    st.image(farm_crop_images[1], use_container_width=True)

with col3:
    st.markdown("""
    <div style='background:#2d2d2d; padding: 20px; border-radius: 10px; text-align:center;'>
        <h3 style='color: #4CAF50;'>🌾 Crop Recommendations</h3>
        <p>Smart AI-based suggestions tailored to your soil and environment.</p>
        <a href='./pages/3_Crop_Recommendation.py'><button>Get Recommendations</button></a>
    </div>
    """, unsafe_allow_html=True)
    st.image(farm_crop_images[2], use_container_width=True)

st.divider()

# Google Sheets setup
st.markdown("<h2 style='text-align: center; color: #4CAF50;'>🔄 Connect Your Data Source</h2>", unsafe_allow_html=True)

if 'google_sheets_configured' not in st.session_state:
    config_file = '.streamlit/sheets_config.json'
    if os.path.exists(config_file):
        with open(config_file) as f:
            config = json.load(f)
            st.session_state.update(config)
    else:
        st.session_state.update({
            'google_sheets_configured': False,
            'spreadsheet_id': '',
            'sheet_name': '',
            'credentials_json': '',
            'show_sheet_url': False
        })

st.session_state.show_sheet_url = st.toggle("Use Google Sheet URL", value=st.session_state.show_sheet_url)

with st.form("sheets_config_form"):
    st.markdown("<h4 style='color: #4CAF50;'>Connection Details</h4>", unsafe_allow_html=True)

    if st.session_state.show_sheet_url:
        sheet_url = st.text_input("Google Sheet URL")
        match = re.search(r'/d/([\w-]+)', sheet_url)
        spreadsheet_id = match.group(1) if match else ''
    else:
        spreadsheet_id = st.text_input("Spreadsheet ID", value=st.session_state.spreadsheet_id)

    sheet_name = st.text_input("Sheet Name", value=st.session_state.sheet_name)
    credentials_json = st.text_area("Google Credentials (JSON)", value=st.session_state.credentials_json, height=150)

    if st.form_submit_button("Connect"):
        if not (spreadsheet_id and sheet_name and credentials_json):
            st.error("All fields are required.")
        else:
            try:
                creds = json.loads(credentials_json)
                df = get_sheet_data(spreadsheet_id, sheet_name, creds)
                if df is not None:
                    st.session_state.update({
                        'google_sheets_configured': True,
                        'spreadsheet_id': spreadsheet_id,
                        'sheet_name': sheet_name,
                        'credentials_json': credentials_json
                    })
                    os.makedirs('.streamlit', exist_ok=True)
                    with open('.streamlit/sheets_config.json', 'w') as f:
                        json.dump(st.session_state, f)
                    st.success(f"Connected to sheet: {sheet_name}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# Show sample data
if st.session_state.google_sheets_configured:
    try:
        creds = json.loads(st.session_state.credentials_json)
        df = get_sheet_data(st.session_state.spreadsheet_id, st.session_state.sheet_name, creds)
        if df is not None:
            st.markdown("<h4 style='color: #4CAF50;'>Sample Data</h4>", unsafe_allow_html=True)
            st.dataframe(df.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Error loading data: {e}")

    if st.button("Reset Connection"):
        os.remove('.streamlit/sheets_config.json')
        st.session_state.clear()
        st.rerun()

st.divider()
st.markdown("<div style='text-align:center; color:#81C784;'>Smart Farming Dashboard v1.0 | Powered by Streamlit</div>", unsafe_allow_html=True)
