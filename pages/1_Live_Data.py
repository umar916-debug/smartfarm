import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from utils.sheets_integration import get_sheet_data
from assets.images import agricultural_sensor_images, farming_tech_images

# Set page configuration
st.set_page_config(
    page_title="Live Farm Data | Smart Farming",
    page_icon="📊",
    layout="wide"
)

# Page title
st.title("📊 Live Farm Data Monitoring")

# Check if Google Sheets is configured
if 'google_sheets_configured' not in st.session_state or not st.session_state.google_sheets_configured:
    st.warning("⚠️ Google Sheets connection not configured. Please go to the home page to set up your connection.")
    st.page_link("app.py", label="Go to Home Page", icon="🏠")
else:
    # Fetch the latest data
    try:
        with st.spinner("Fetching latest data from Google Sheets..."):
            # Get the data from Google Sheets
            df = get_sheet_data(
                st.session_state.spreadsheet_id,
                st.session_state.sheet_name,
                st.session_state.credentials_json
            )
            
            if df is not None and not df.empty:
                # Get the latest row (assuming the data is chronological)
                latest_data = df.iloc[-1].to_dict()
                
                # Display timestamp if available
                if 'timestamp' in latest_data:
                    timestamp = latest_data['timestamp']
                    st.subheader(f"Last Updated: {timestamp}")
                else:
                    st.subheader(f"Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Display sensor image
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(agricultural_sensor_images[1], use_container_width=True, 
                             caption="Farm Sensor Network")
                
                # Create dashboard cards for each metric
                with col2:
                    # Filter out non-numeric and timestamp columns for the dashboard
                    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                    # Remove any specific columns you don't want to display
                    if 'timestamp' in numeric_cols:
                        numeric_cols.remove('timestamp')
                    
                    # Create a grid of metric cards
                    metric_cols = st.columns(min(4, len(numeric_cols)))
                    
                    # Define metric mappings with units and thresholds
                    metric_info = {
                        'temperature': {'unit': '°C', 'good_range': (15, 30), 'icon': '🌡️'},
                        'humidity': {'unit': '%', 'good_range': (40, 80), 'icon': '💧'},
                        'soil_moisture': {'unit': '%', 'good_range': (30, 70), 'icon': '🌱'},
                        'light_intensity': {'unit': 'lux', 'good_range': (10000, 50000), 'icon': '☀️'},
                        'ph': {'unit': 'pH', 'good_range': (5.5, 7.5), 'icon': '⚗️'},
                        'nitrogen': {'unit': 'mg/kg', 'good_range': (150, 300), 'icon': 'N'},
                        'phosphorus': {'unit': 'mg/kg', 'good_range': (25, 50), 'icon': 'P'},
                        'potassium': {'unit': 'mg/kg', 'good_range': (150, 300), 'icon': 'K'},
                        'rainfall': {'unit': 'mm', 'good_range': (900, 1400), 'icon': '🌧️'},
                    }
                    
                    # Map any column names to standardized names for display
                    column_display_map = {
                        'temp': 'temperature',
                        'hum': 'humidity',
                        'soil_moist': 'soil_moisture',
                        'light': 'light_intensity',
                        'n': 'nitrogen',
                        'p': 'phosphorus',
                        'k': 'potassium',
                        'rain': 'rainfall'
                    }
                    
                    # Display each metric in a card
                    for i, col_name in enumerate(numeric_cols):
                        # Get standardized name if available
                        display_name = column_display_map.get(col_name, col_name)
                        
                        # Get metric info or use defaults
                        info = metric_info.get(display_name, 
                                              {'unit': '', 'good_range': (0, 100), 'icon': '📊'})
                        
                        # Format the value with appropriate units
                        value = latest_data.get(col_name, 'N/A')
                        if isinstance(value, (int, float)):
                            formatted_value = f"{value} {info['unit']}"
                            
                            # Determine if the value is in the good range
                            if value < info['good_range'][0]:
                                delta_color = "inverse"  # Lower than ideal (red)
                                delta_description = f"Below optimal range ({info['good_range'][0]} - {info['good_range'][1]} {info['unit']})"
                            elif value > info['good_range'][1]:
                                delta_color = "inverse"  # Higher than ideal (red)
                                delta_description = f"Above optimal range ({info['good_range'][0]} - {info['good_range'][1]} {info['unit']})"
                            else:
                                delta_color = "normal"  # Within ideal range (green)
                                delta_description = "Within optimal range"
                            
                            # Get previous value for comparison if available
                            if len(df) > 1:
                                prev_value = df.iloc[-2][col_name]
                                delta = f"{value - prev_value:+.2f} {info['unit']}"
                            else:
                                delta = None
                        else:
                            formatted_value = str(value)
                            delta = None
                            delta_color = "off"
                            delta_description = ""
                        
                        # Display the metric
                        with metric_cols[i % len(metric_cols)]:
                            st.metric(
                                label=f"{info['icon']} {display_name.replace('_', ' ').title()}",
                                value=formatted_value,
                                delta=delta,
                                delta_color=delta_color,
                                help=f"Optimal range: {info['good_range'][0]}-{info['good_range'][1]} {info['unit']}\n{delta_description}"
                            )
                
                # Display a recent trend chart for important metrics
                st.subheader("Recent Trends")
                
                # Select only the numerical columns for the trend chart
                chart_df = df.copy()
                
                # Handle timestamp column for the chart
                if 'timestamp' in chart_df.columns:
                    chart_df['timestamp'] = pd.to_datetime(chart_df['timestamp'])
                    chart_df.set_index('timestamp', inplace=True)
                else:
                    # Create a timestamp index if none exists
                    chart_df.index = pd.date_range(end=pd.Timestamp.now(), periods=len(chart_df), freq='h')
                
                # Get the last N rows for the recent trend (default to last 20 or all if less)
                n_rows = min(20, len(chart_df))
                recent_df = chart_df.tail(n_rows)
                
                # Let user select which metrics to display
                selected_metrics = st.multiselect(
                    "Select metrics to display in the trend chart",
                    options=numeric_cols,
                    default=numeric_cols[:3] if len(numeric_cols) > 3 else numeric_cols
                )
                
                if selected_metrics:
                    # Create the line chart with Plotly
                    fig = px.line(
                        recent_df, 
                        y=selected_metrics,
                        markers=True,
                        title="Recent Sensor Data Trends",
                        labels={"value": "Measurement", "index": "Time", "variable": "Metric"}
                    )
                    
                    # Customize the chart
                    fig.update_layout(
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        height=400,
                    )
                    
                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Please select at least one metric to display the trend chart.")
                
                # Add a data table with all the recent data
                with st.expander("View Recent Raw Data"):
                    st.dataframe(recent_df.reset_index(), use_container_width=True)
                
                # Add a refresh button
                if st.button("Refresh Data"):
                    st.rerun()
            else:
                st.error("No data found in the connected Google Sheet. Please check your connection settings.")
                st.image(farming_tech_images[0], caption="Farm Technology Network", use_container_width=True)
    
    except Exception as e:
        st.error(f"Error fetching data from Google Sheets: {str(e)}")
        st.image(farming_tech_images[0], caption="Farm Technology Network", use_container_width=True)

# Add information about the data
st.divider()
with st.expander("About the Live Data Monitoring"):
    st.write("""
    ## How Live Monitoring Works
    
    This dashboard connects to your Google Sheet containing sensor data from your farm.
    The system automatically fetches the latest readings and displays them in an easy-to-understand format.
    
    ### Data Refresh
    
    - The dashboard shows the most recent data point from your connected sensors.
    - Click the 'Refresh Data' button to fetch the latest readings.
    - Optimal ranges are displayed to help you quickly identify potential issues.
    
    ### Monitored Parameters
    
    Depending on your sensor setup, the dashboard can display various metrics including:
    
    - Temperature: Ambient air temperature around your crops.
    - Humidity: Relative humidity in the air.
    - Soil Moisture: Water content in the soil.
    - Light Intensity: Amount of sunlight reaching the crops.
    - pH: Acidity or alkalinity of the soil.
    - NPK: Nitrogen, Phosphorus, and Potassium levels in the soil.
    - Rainfall: Recent precipitation measurements.
    """)
