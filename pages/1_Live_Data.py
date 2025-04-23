import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from utils.sheets_integration import get_sheet_data

# Set page configuration
st.set_page_config(
    page_title="Live Farm Data | Smart Farming",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        font-size: 14px;
        color: #7f8c8d;
    }
    .timestamp {
        font-size: 16px;
        color: #3498db;
        margin-bottom: 20px;
    }
    .header {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Page title
st.markdown("<h1 class='header'>🌱 Real-Time Farm Monitoring</h1>", unsafe_allow_html=True)

# Check if Google Sheets is configured
if 'google_sheets_configured' not in st.session_state or not st.session_state.google_sheets_configured:
    st.warning("⚠️ Google Sheets connection not configured. Please configure your connection first.")
else:
    # Fetch the latest data
    try:
        with st.spinner("Fetching latest farm data..."):
            # Get the data from Google Sheets
            df = get_sheet_data(
                st.session_state.spreadsheet_id,
                st.session_state.sheet_name,
                st.session_state.credentials_json
            )
            
            if df is not None and not df.empty:
                # Get the latest row
                latest_data = df.iloc[-1].to_dict()
                
                # Display timestamp (matching Google Sheets format)
                if 'timestamp' in latest_data:
                    timestamp = pd.to_datetime(latest_data['timestamp'])
                    st.markdown(f"<div class='timestamp'>Last Reading: <strong>{timestamp.strftime('%Y-%m-%d %H:%M:%S')}</strong></div>", 
                               unsafe_allow_html=True)
                else:
                    st.warning("No timestamp found in the data")
                
                # Create two columns for layout
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Display key metrics in cards
                    st.markdown("<h3>Current Readings</h3>", unsafe_allow_html=True)
                    
                    # Define the metrics we want to display
                    metrics_to_display = [
                        ('temperature', '🌡️ Temperature', '°C'),
                        ('humidity', '💧 Humidity', '%'),
                        ('soil_moisture', '🌱 Soil Moisture', '%'),
                        ('ph', '⚗️ Soil pH', 'pH'),
                        ('nitrogen', 'N Nitrogen', 'mg/kg'),
                        ('phosphorus', 'P Phosphorus', 'mg/kg'),
                        ('potassium', 'K Potassium', 'mg/kg')
                    ]
                    
                    # Display each metric in a styled card
                    for metric, label, unit in metrics_to_display:
                        if metric in latest_data:
                            value = latest_data[metric]
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">{label}</div>
                                <div class="metric-value">{value} {unit}</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                with col2:
                    # Display a time series chart of the data
                    st.markdown("<h3>Recent Trends</h3>", unsafe_allow_html=True)
                    
                    # Prepare the data for plotting
                    plot_df = df.copy()
                    
                    # Convert timestamp to datetime if it exists
                    if 'timestamp' in plot_df.columns:
                        plot_df['timestamp'] = pd.to_datetime(plot_df['timestamp'])
                        plot_df.set_index('timestamp', inplace=True)
                    
                    # Get last 24 hours of data (or all if less)
                    recent_data = plot_df.last('24H') if 'timestamp' in df.columns else plot_df.tail(24)
                    
                    # Create interactive plot
                    if not recent_data.empty:
                        fig = px.line(
                            recent_data,
                            y=[col for col in recent_data.columns if col != 'timestamp'],
                            title="Sensor Data Over Time",
                            labels={'value': 'Measurement', 'timestamp': 'Time', 'variable': 'Sensor'}
                        )
                        fig.update_layout(
                            height=500,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Not enough data to display trends")
                
                # Add a refresh button at the bottom
                if st.button("🔄 Refresh Data", type="primary"):
                    st.rerun()
                
            else:
                st.error("No data found in the connected Google Sheet")
    
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

# Minimal about section
with st.expander("About this dashboard"):
    st.write("""
    This real-time monitoring dashboard displays the latest sensor readings from your farm.
    - Data is pulled directly from your Google Sheets
    - Timestamps match exactly with your source data
    - Charts show trends over the last 24 hours
    - Click 'Refresh Data' to get the latest readings
    """)
