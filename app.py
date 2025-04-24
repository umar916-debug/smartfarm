import streamlit as st
import os
import json
from utils.sheets_integration import validate_credentials

# Set page configuration
st.set_page_config(
    page_title="Smart Farm Monitoring",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'spreadsheet_id' not in st.session_state:
    st.session_state.spreadsheet_id = ""
if 'sheet_name' not in st.session_state:
    st.session_state.sheet_name = ""
if 'credentials_uploaded' not in st.session_state:
    st.session_state.credentials_uploaded = False
if 'credentials_path' not in st.session_state:
    st.session_state.credentials_path = ""

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #43A047;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #E8F5E9;
        border-radius: 0.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown("<h1 class='main-header'>Smart Farm Monitoring</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='sub-header'>Google Sheets Configuration</h2>", unsafe_allow_html=True)

# Create a directory for storing credentials if it doesn't exist
credentials_dir = "credentials"
if not os.path.exists(credentials_dir):
    os.makedirs(credentials_dir)

# Google Sheets Configuration Form
with st.form("sheets_config_form"):
    spreadsheet_id = st.text_input(
        "Google Spreadsheet ID",
        value=st.session_state.spreadsheet_id,
        help="Enter the ID of your Google Spreadsheet (found in the URL)"
    )
    
    sheet_name = st.text_input(
        "Sheet Name",
        value=st.session_state.sheet_name,
        help="Enter the name of the sheet containing sensor data"
    )
    
    # File uploader for credentials.json
    uploaded_file = st.file_uploader(
        "Upload credentials.json",
        type=["json"],
        help="Upload your Google API credentials file (credentials.json)"
    )
    
    submit_button = st.form_submit_button("Save Configuration")
    
    if submit_button:
        if not spreadsheet_id:
            st.error("Please enter a Spreadsheet ID")
        elif not sheet_name:
            st.error("Please enter a Sheet Name")
        elif not uploaded_file and not st.session_state.credentials_uploaded:
            st.error("Please upload your credentials.json file")
        else:
            st.session_state.spreadsheet_id = spreadsheet_id
            st.session_state.sheet_name = sheet_name
            
            # Process credentials file if uploaded
            if uploaded_file is not None:
                credentials_path = os.path.join(credentials_dir, "credentials.json")
                
                # Read and save the credentials file
                credentials_data = json.load(uploaded_file)
                with open(credentials_path, "w") as f:
                    json.dump(credentials_data, f)
                
                # Validate credentials
                if validate_credentials(credentials_path):
                    st.session_state.credentials_uploaded = True
                    st.session_state.credentials_path = credentials_path
                    st.success("Configuration saved successfully!")
                else:
                    st.error("Invalid credentials file. Please check your credentials.json file.")
            else:
                st.success("Configuration updated successfully!")

# Display current configuration (if set)
if st.session_state.spreadsheet_id and st.session_state.sheet_name and st.session_state.credentials_uploaded:
    st.markdown(
        f"""
        <div class='success-message'>
        <h3>Current Configuration</h3>
        <p><strong>Spreadsheet ID:</strong> {st.session_state.spreadsheet_id}</p>
        <p><strong>Sheet Name:</strong> {st.session_state.sheet_name}</p>
        <p><strong>Credentials:</strong> Uploaded ✅</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("### Next Steps")
    st.markdown("Now that you've configured your Google Sheets connection, you can view your farm data.")
    
    # Button to navigate to the Live Data page
    if st.button("View Live Data", use_container_width=True):
        st.switch_page("pages/1_Live_Data.py")
else:
    st.info("Please complete the configuration form to get started.")
