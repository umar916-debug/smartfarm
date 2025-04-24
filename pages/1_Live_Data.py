import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils.sheets_integration import get_sheet_data

# Set page configuration
st.set_page_config(
    page_title="Smart Farm - Live Data",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .metric-card {
        border-radius: 0.5rem;
        padding: 1rem;
        background-color: white;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1.2rem;
        color: #555;
    }
    .metric-unit {
        font-size: 1rem;
        color: #777;
    }
    .metric-optimal {
        color: #2E7D32;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .metric-warning {
        color: #FF9800;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .metric-danger {
        color: #D32F2F;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .optimal-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #2E7D32;
        margin-right: 0.5rem;
    }
    .warning-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #FF9800;
        margin-right: 0.5rem;
    }
    .danger-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #D32F2F;
        margin-right: 0.5rem;
    }
    .timestamp {
        text-align: center;
        font-size: 1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Check if configuration is set
if ('spreadsheet_id' not in st.session_state or 
    'sheet_name' not in st.session_state or 
    'credentials_path' not in st.session_state or 
    not st.session_state.credentials_uploaded):
    st.error("Please configure your Google Sheets connection first.")
    if st.button("Go to Configuration", use_container_width=True):
        st.switch_page("app.py")
    st.stop()

# Function to determine metric status
def get_metric_status(value, thresholds):
    if value is None:
        return "danger"
    try:
        value_float = float(value)
        if value_float >= thresholds[0] and value_float <= thresholds[1]:
            return "optimal"
        elif (value_float >= thresholds[0] - thresholds[2] and value_float < thresholds[0]) or \
             (value_float > thresholds[1] and value_float <= thresholds[1] + thresholds[2]):
            return "warning"
        else:
            return "danger"
    except (ValueError, TypeError):
        return "danger"

# Function to create a metric card
def create_metric_card(label, value, unit, icon, thresholds, description):
    status = get_metric_status(value, thresholds)
    
    try:
        value_float = float(value) if value is not None else None
        value_display = f"{value_float:.1f}" if value_float is not None else "N/A"
    except (ValueError, TypeError):
        value_display = "N/A"
    
    if status == "optimal":
        status_html = f"""<div class="metric-optimal">
                           <span class="optimal-indicator"></span>
                           Optimal
                        </div>"""
    elif status == "warning":
        status_html = f"""<div class="metric-warning">
                           <span class="warning-indicator"></span>
                           Warning
                        </div>"""
    else:
        status_html = f"""<div class="metric-danger">
                           <span class="danger-indicator"></span>
                           Critical
                        </div>"""
    
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value_display} <span class="metric-unit">{unit}</span></div>
        {status_html}
        <div style="font-size: 0.85rem; color: #777; margin-top: 0.5rem;">
            {description}
        </div>
    </div>
    """
    return html

# Main header
st.markdown("<h1 class='main-header'>Smart Farm Monitoring</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='sub-header'>Live Sensor Data</h2>", unsafe_allow_html=True)

# Create a refresh button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    refresh = st.button("🔄 Refresh Data", use_container_width=True)

# Get data from Google Sheets
@st.cache_data(ttl=300)  # Cache data for 5 minutes
def load_data():
    return get_sheet_data(
        st.session_state.credentials_path,
        st.session_state.spreadsheet_id,
        st.session_state.sheet_name
    )

# Load data (refresh if button clicked)
if refresh:
    st.cache_data.clear()
data = load_data()

# Display data
if data is not None and not data.empty:
    # Get the latest row of data
    latest_data = data.iloc[-1]
    
    # Display last updated timestamp
    try:
        # Try to parse the timestamp
        timestamp = pd.to_datetime(latest_data.get('timestamp'))
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"<div class='timestamp'>Last updated: {formatted_timestamp}</div>", unsafe_allow_html=True)
    except:
        st.markdown("<div class='timestamp'>Last updated: Unknown</div>", unsafe_allow_html=True)
    
    # Create metric cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Temperature
        st.markdown(
            create_metric_card(
                "Temperature", 
                latest_data.get('temperature'), 
                "°C", 
                "🌡️", 
                [20, 30, 5],  # Optimal min, max, warning buffer
                "Optimal range: 20-30°C"
            ), 
            unsafe_allow_html=True
        )
        
        # Soil Moisture
        st.markdown(
            create_metric_card(
                "Soil Moisture", 
                latest_data.get('soil_moisture'), 
                "%", 
                "💧", 
                [40, 70, 10],  # Optimal min, max, warning buffer
                "Optimal range: 40-70%"
            ), 
            unsafe_allow_html=True
        )
        
        # pH
        st.markdown(
            create_metric_card(
                "pH Level", 
                latest_data.get('pH'), 
                "", 
                "🧪", 
                [6.0, 7.5, 0.5],  # Optimal min, max, warning buffer
                "Optimal range: 6.0-7.5"
            ), 
            unsafe_allow_html=True
        )
    
    with col2:
        # Humidity
        st.markdown(
            create_metric_card(
                "Humidity", 
                latest_data.get('humidity'), 
                "%", 
                "💨", 
                [60, 80, 10],  # Optimal min, max, warning buffer
                "Optimal range: 60-80%"
            ), 
            unsafe_allow_html=True
        )
        
        # Light Intensity
        st.markdown(
            create_metric_card(
                "Light Intensity", 
                latest_data.get('light_intensity'), 
                "lux", 
                "☀️", 
                [10000, 30000, 5000],  # Optimal min, max, warning buffer
                "Optimal range: 10000-30000 lux"
            ), 
            unsafe_allow_html=True
        )
        
        # Nitrogen
        st.markdown(
            create_metric_card(
                "Nitrogen", 
                latest_data.get('nitrogen'), 
                "ppm", 
                "🌿", 
                [150, 300, 50],  # Optimal min, max, warning buffer
                "Optimal range: 150-300 ppm"
            ), 
            unsafe_allow_html=True
        )
    
    with col3:
        # Phosphorus
        st.markdown(
            create_metric_card(
                "Phosphorus", 
                latest_data.get('phosphorus'), 
                "ppm", 
                "🌱", 
                [30, 60, 10],  # Optimal min, max, warning buffer
                "Optimal range: 30-60 ppm"
            ), 
            unsafe_allow_html=True
        )
        
        # Potassium
        st.markdown(
            create_metric_card(
                "Potassium", 
                latest_data.get('potassium'), 
                "ppm", 
                "🍃", 
                [150, 300, 50],  # Optimal min, max, warning buffer
                "Optimal range: 150-300 ppm"
            ), 
            unsafe_allow_html=True
        )
        
        # Empty space for alignment
        st.markdown("<div style='height: 215px;'></div>", unsafe_allow_html=True)
    
    # Display a note about interpreting the metrics
    st.info("""
        **How to interpret these metrics:**
        - 🟢 **Optimal**: Sensor values are within the ideal range for plant growth.
        - 🟠 **Warning**: Values are approaching critical thresholds, attention may be needed.
        - 🔴 **Critical**: Values are outside acceptable ranges, immediate action required.
    """)
    
else:
    st.error("No data available. Please check your Google Sheets configuration and ensure the sheet contains data.")
    
    # Show sample data format
    st.markdown("### Expected Data Format")
    st.markdown("""
    Your Google Sheet should have the following columns:
    - `timestamp`: Date and time of the reading
    - `temperature`: Temperature in °C
    - `humidity`: Humidity in %
    - `soil_moisture`: Soil moisture in %
    - `light_intensity`: Light intensity in lux
    - `pH`: pH level
    - `nitrogen`: Nitrogen level in ppm
    - `phosphorus`: Phosphorus level in ppm
    - `potassium`: Potassium level in ppm
    """)

# Add a link back to the configuration page
st.sidebar.title("Navigation")
if st.sidebar.button("📝 Edit Configuration"):
    st.switch_page("app.py")
