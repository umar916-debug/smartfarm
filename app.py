import streamlit as st
import pandas as pd
import os
from utils.sheets_integration import authenticate_google_sheets
from assets.images import farm_crop_images, farming_tech_images, agricultural_sensor_images

# Set page configuration
st.set_page_config(
    page_title="Smart Farming Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better UI
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
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #66BB6A;
    }
    div.stMarkdown h3 {
        color: #4CAF50;
        padding-top: 1rem;
    }
    .css-1544g2n.e1fqkh3o4 {
        padding-top: 2rem;
    }
    div.block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Main app header with styled title
st.markdown("<h1 class='main-header'>🌱 Smart Farming Dashboard</h1>", unsafe_allow_html=True)

# Introduction and overview
st.markdown("""
<div style='background-color: rgba(45, 45, 45, 0.7); padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;'>
<p style='font-size: 1.1rem;'>Welcome to the Smart Farming Dashboard - your central hub for monitoring farm conditions, 
analyzing historical data, and receiving intelligent crop recommendations.</p>

<p>This application helps you:</p>
<ul>
  <li><strong style='color: #81C784;'>Monitor real-time farm data</strong> from connected sensors</li>
  <li><strong style='color: #81C784;'>Analyze historical trends</strong> in your farming metrics</li>
  <li><strong style='color: #81C784;'>Get AI-powered recommendations</strong> for optimal crop selection</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Header image
st.image(farm_crop_images[0], use_container_width=True, caption="Smart Farming Solutions")

# Main dashboard overview
st.markdown("<h2 style='text-align: center; color: #4CAF50;'>Key Features</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background-color: rgba(45, 45, 45, 0.7); padding: 20px; border-radius: 10px; text-align: center; height: 100%; margin: 10px 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
        <h3 style="color: #4CAF50; margin-top: 0;">📊 Live Monitoring</h3>
        <p>View real-time data from your farm sensors including temperature, humidity, and soil nutrients.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image(agricultural_sensor_images[0], use_container_width=True)
    st.page_link("pages/1_Live_Data.py", label="Go to Live Data", icon="📊", use_container_width=True)

with col2:
    st.markdown("""
    <div style="background-color: rgba(45, 45, 45, 0.7); padding: 20px; border-radius: 10px; text-align: center; height: 100%; margin: 10px 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
        <h3 style="color: #4CAF50; margin-top: 0;">📈 Historical Analysis</h3>
        <p>Analyze trends and patterns in your historical farm data to optimize growing conditions.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image(farm_crop_images[1], use_container_width=True)
    st.page_link("pages/2_Historical_Data.py", label="View Historical Data", icon="📈", use_container_width=True)

with col3:
    st.markdown("""
    <div style="background-color: rgba(45, 45, 45, 0.7); padding: 20px; border-radius: 10px; text-align: center; height: 100%; margin: 10px 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
        <h3 style="color: #4CAF50; margin-top: 0;">🌾 Crop Recommendations</h3>
        <p>Get AI-powered suggestions for optimal crop selection based on your farm's unique conditions.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image(farm_crop_images[2], use_container_width=True)
    st.page_link("pages/3_Crop_Recommendation.py", label="Get Recommendations", icon="🌾", use_container_width=True)

st.divider()

# Setup Google Sheets integration if not already configured
st.markdown("<h2 style='text-align: center; color: #4CAF50; margin-top: 2rem;'>🔄 Connect Your Data Source</h2>", unsafe_allow_html=True)

# Style container for Google Sheets configuration
st.markdown("""
<div style="background-color: rgba(45, 45, 45, 0.7); padding: 25px; border-radius: 10px; border: 1px solid #4CAF50; margin-bottom: 20px;">
    <h3 style="color: #81C784; margin-top: 0; margin-bottom: 15px;">Google Sheets Integration</h3>
    <p style="margin-bottom: 20px;">Configure your Google Sheets connection to start monitoring farm data in real-time. This application requires access to a Google Sheet with the following columns: <span style="color: #81C784;">Timestamp, Temperature, Humidity, N (Nitrogen), P (Phosphorus), K (Potassium), and pH</span>.</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state - use st.session_state.get() to preserve values between sessions
if 'google_sheets_configured' not in st.session_state:
    # Check if the config is stored in a file or load from previous session
    try:
        import os
        import json
        config_file = '.streamlit/sheets_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                st.session_state.google_sheets_configured = config.get('configured', False)
                st.session_state.spreadsheet_id = config.get('spreadsheet_id', "")
                st.session_state.sheet_name = config.get('sheet_name', "")
                st.session_state.credentials_json = config.get('credentials_json', "")
                st.session_state.show_sheet_url = config.get('show_sheet_url', False)
        else:
            st.session_state.google_sheets_configured = False
            st.session_state.spreadsheet_id = ""
            st.session_state.sheet_name = ""
            st.session_state.credentials_json = ""
            st.session_state.show_sheet_url = False
    except Exception:
        st.session_state.google_sheets_configured = False
        st.session_state.spreadsheet_id = ""
        st.session_state.sheet_name = ""
        st.session_state.credentials_json = ""
        st.session_state.show_sheet_url = False

# Toggle button with custom style
st.markdown("""
<style>
    div[data-testid="stToggleButton"] label p {
        font-size: 1rem;
        color: #4CAF50 !important;
    }
</style>
""", unsafe_allow_html=True)

# Toggle between URL input and spreadsheet ID/sheet name
toggle_col1, toggle_col2 = st.columns([3, 1])
with toggle_col1:
    st.session_state.show_sheet_url = st.toggle("Use Google Sheet URL instead of ID", value=st.session_state.show_sheet_url)

# Style the form container
st.markdown("""
<style>
    div.stForm > div {
        background-color: rgba(35, 35, 35, 0.5);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #4CAF50;
    }
    div.stForm [data-baseweb="input"] {
        border-radius: 4px;
        border: 1px solid #4CAF50 !important;
    }
    div.stForm [data-baseweb="textarea"] {
        border-radius: 4px;
        border: 1px solid #4CAF50 !important;
    }
    div.stForm button {
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets configuration form
with st.form("sheets_config_form"):
    # Form title
    st.markdown("<h4 style='color: #4CAF50; margin-top: 0;'>Connection Details</h4>", unsafe_allow_html=True)
    
    # Input for Google Sheet with icon
    if st.session_state.show_sheet_url:
        sheet_url = st.text_input(
            "📄 Google Sheet URL",
            help="The full URL of your Google Sheet, e.g., 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit'",
            value="" if st.session_state.spreadsheet_id == "" else f"https://docs.google.com/spreadsheets/d/{st.session_state.spreadsheet_id}/edit"
        )
        # Extract spreadsheet ID from URL
        if sheet_url:
            import re
            match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
            if match:
                spreadsheet_id = match.group(1)
            else:
                spreadsheet_id = ""
        else:
            spreadsheet_id = ""
    else:
        spreadsheet_id = st.text_input(
            "🆔 Google Spreadsheet ID", 
            help="The ID from your Google Sheet URL, e.g., '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'",
            value=st.session_state.spreadsheet_id
        )
    
    # Sheet name input with icon
    sheet_name = st.text_input(
        "📑 Sheet Name", 
        help="The name of the specific sheet tab (e.g., 'Sheet1')",
        value=st.session_state.sheet_name
    )
    
    # JSON credentials input with icon
    credentials_json = st.text_area(
        "🔐 Google Service Account Credentials (JSON)",
        help="Paste your Google service account credentials in JSON format here",
        value=st.session_state.credentials_json,
        height=150
    )
    
    # Create 3 columns for better button positioning
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        submitted = st.form_submit_button("🔄 Connect to Google Sheets")
    
    if submitted:
        # Validate inputs
        if not spreadsheet_id:
            st.error("Please provide a valid Google Spreadsheet ID or URL.")
        elif not sheet_name:
            st.error("Please provide a sheet name.")
        elif not credentials_json:
            st.error("Please provide your Google service account credentials.")
        else:
            # Try to authenticate and connect to the Google Sheets
            try:
                with st.spinner("Connecting to Google Sheets..."):
                    # Authenticate with Google Sheets using the provided credentials
                    service = authenticate_google_sheets(credentials_json)
                    
                    if service is None:
                        st.error("Failed to authenticate with Google Sheets. Please check your credentials.")
                    else:
                        # Test connection by retrieving sheet metadata
                        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                        sheet_titles = [sheet['properties']['title'] for sheet in sheet_metadata['sheets']]
                        
                        if sheet_name in sheet_titles:
                            st.session_state.google_sheets_configured = True
                            st.session_state.spreadsheet_id = spreadsheet_id
                            st.session_state.sheet_name = sheet_name
                            st.session_state.credentials_json = credentials_json
                            
                            # Save configuration to file for persistence
                            try:
                                import os
                                import json
                                # Ensure the .streamlit directory exists
                                os.makedirs('.streamlit', exist_ok=True)
                                config_file = '.streamlit/sheets_config.json'
                                config = {
                                    'configured': True,
                                    'spreadsheet_id': spreadsheet_id,
                                    'sheet_name': sheet_name,
                                    'credentials_json': credentials_json,
                                    'show_sheet_url': st.session_state.show_sheet_url
                                }
                                with open(config_file, 'w') as f:
                                    json.dump(config, f)
                            except Exception as e:
                                print(f"Warning: Could not save configuration: {str(e)}")
                                
                            st.success(f"Successfully connected to Google Sheet '{sheet_metadata['properties']['title']}', tab '{sheet_name}'")
                        else:
                            st.error(f"Sheet tab '{sheet_name}' not found. Available tabs: {', '.join(sheet_titles)}")
            except Exception as e:
                st.error(f"Failed to connect to Google Sheets: {str(e)}")

# Display connection status with styled containers
if st.session_state.google_sheets_configured:
    # Custom styled success message
    st.markdown(f"""
    <div style="background-color: rgba(45, 45, 45, 0.7); padding: 15px; border-radius: 10px; 
        border-left: 5px solid #4CAF50; margin: 20px 0; display: flex; align-items: center;">
        <span style="color: #4CAF50; font-size: 24px; margin-right: 10px;">✅</span>
        <div>
            <p style="margin: 0; font-size: 16px; font-weight: 500;">Connected to Google Sheets</p>
            <p style="margin: 0; font-size: 14px; color: #81C784;">Sheet: '{st.session_state.sheet_name}'</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display sample data if available in a styled container
    try:
        with st.spinner("Loading sample data..."):
            df = get_sheet_data(
                st.session_state.spreadsheet_id,
                st.session_state.sheet_name,
                st.session_state.credentials_json
            )
            if df is not None and not df.empty:
                st.markdown("""
                <div style="background-color: rgba(35, 35, 35, 0.5); padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <h4 style="color: #4CAF50; margin-top: 0;">Sample Data from Your Sheet</h4>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(df.head(3), use_container_width=True)
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")
    
    # Add some space before the reset button
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Centered reset button with custom styling
    col1, col2, col3 = st.columns([3, 1, 3])
    with col2:
        if st.button("Reset Connection", use_container_width=True):
            # Remove configuration file if it exists
            try:
                import os
                config_file = '.streamlit/sheets_config.json'
                if os.path.exists(config_file):
                    os.remove(config_file)
            except Exception as e:
                print(f"Warning: Could not remove config file: {str(e)}")
            
            # Reset session state
            st.session_state.google_sheets_configured = False
            st.session_state.spreadsheet_id = ""
            st.session_state.sheet_name = ""
            st.session_state.credentials_json = ""
            st.rerun()
else:
    # Custom styled warning message
    st.markdown("""
    <div style="background-color: rgba(45, 45, 45, 0.7); padding: 15px; border-radius: 10px; 
        border-left: 5px solid #FFC107; margin: 20px 0; display: flex; align-items: center;">
        <span style="color: #FFC107; font-size: 24px; margin-right: 10px;">⚠️</span>
        <p style="margin: 0; font-weight: 500;">Not connected to any Google Sheet. Please configure the connection above.</p>
    </div>
    """, unsafe_allow_html=True)

# App footer
st.divider()

# About section with styled container
st.markdown("""
<div style="background-color: rgba(45, 45, 45, 0.7); padding: 25px; border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
    <h2 style="color: #4CAF50; margin-top: 0;">About Smart Farming Dashboard</h2>
    <p style="font-size: 1.1rem; margin-bottom: 15px;">
        This application integrates with your existing farm sensors through Google Sheets to provide
        real-time monitoring, historical analysis, and intelligent crop recommendations.
    </p>
    <p>
        The machine learning models used for recommendations are trained on your historical farm data
        and consider various environmental factors specific to your farming context.
    </p>
</div>
""", unsafe_allow_html=True)

# Tech stack information in a styled expander
with st.expander("Technical Information"):
    st.markdown("""
    <div style="padding: 10px; background-color: rgba(35, 35, 35, 0.5); border-radius: 5px;">
        <h4 style="color: #4CAF50; margin-top: 0;">Technology Stack</h4>
        <ul>
            <li><strong style="color: #81C784;">Data Visualization:</strong> Streamlit, Plotly, Matplotlib</li>
            <li><strong style="color: #81C784;">Data Processing:</strong> Pandas, NumPy</li>
            <li><strong style="color: #81C784;">Machine Learning:</strong> Scikit-learn for crop recommendations</li>
            <li><strong style="color: #81C784;">Data Integration:</strong> Google Sheets API for real-time sensor data</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Download section with styled container
from utils.code_zip import download_code_zip
st.markdown("""
<div style="background-color: rgba(45, 45, 45, 0.7); padding: 25px; border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); text-align: center;">
    <h3 style="color: #4CAF50; margin-top: 0;">📥 Download Source Code</h3>
    <p>Get the complete source code of this application for your reference or customization.</p>
</div>
""", unsafe_allow_html=True)

# Download button styled separately because it needs to be interactive
download_code_zip()

