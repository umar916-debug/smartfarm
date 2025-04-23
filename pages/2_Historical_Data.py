import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.sheets_integration import get_sheet_data
from utils.data_processing import process_historical_data
from assets.images import farm_crop_images, farming_tech_images

# Set page configuration
st.set_page_config(
    page_title="Historical Data Analysis | Smart Farming",
    page_icon="📈",
    layout="wide"
)

# Page title
st.title("📈 Historical Farm Data Analysis")
if st.button("🔄 Refresh Data"):
    st.experimental_rerun()


# Check if Google Sheets is configured
if 'google_sheets_configured' not in st.session_state or not st.session_state.google_sheets_configured:
    st.warning("⚠️ Google Sheets connection not configured. Please go to the home page to set up your connection.")
    st.page_link("app.py", label="Go to Home Page", icon="🏠")
else:
    # Fetch historical data
    try:
        with st.spinner("Fetching historical data from Google Sheets..."):
            # Get the data from Google Sheets
            df = get_sheet_data(
                st.session_state.spreadsheet_id,
                st.session_state.sheet_name,
                st.session_state.credentials_json
            )
            
            if df is not None and not df.empty:
                # Process the data for analysis
                hist_df = process_historical_data(df)
                
                # Display a summary of the data
                st.subheader("Data Summary")
                
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    st.metric("Total Records", len(hist_df))
                    
                    # Determine date range if timestamp column exists
                    if 'timestamp' in hist_df.columns:
                        hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'])
                        date_range = f"{hist_df['timestamp'].min().strftime('%Y-%m-%d')} to {hist_df['timestamp'].max().strftime('%Y-%m-%d')}"
                        st.metric("Date Range", date_range)
                
                with metrics_col2:
                    # Display image
                    st.image(farm_crop_images[3], use_container_width=True)
                
                # Filter data by date range if timestamp exists
                if 'timestamp' in hist_df.columns:
                    hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'], utc=True).dt.tz_convert('Asia/Kolkata')

                    
                    st.subheader("Filter Data")
                    
                    # Date range filter
                    min_date = hist_df['timestamp'].min().date()
                    max_date = hist_df['timestamp'].max().date()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
                    with col2:
                        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
                    
                    # Filter the dataframe based on selected dates
                    filtered_df = hist_df[
                        (hist_df['timestamp'].dt.date >= start_date) & 
                        (hist_df['timestamp'].dt.date <= end_date)
                    ]
                    
                    if filtered_df.empty:
                        st.warning("No data available for the selected date range.")
                    else:
                        st.success(f"Displaying {len(filtered_df)} records from {start_date} to {end_date}")
                else:
                    filtered_df = hist_df.copy()
                    st.info("No timestamp column found. Displaying all available data.")
                
                # Get numerical columns for analysis
                numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                if 'timestamp' in numeric_cols:
                    numeric_cols.remove('timestamp')
                
                # Data visualization options
                st.subheader("Data Visualization")
                
                viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Time Series", "Correlation Analysis", "Statistical Summary"])
                
                # Tab 1: Time Series Analysis
                with viz_tab1:
                    st.subheader("Time Series Analysis")
                    
                    # Let user select metrics to visualize
                    selected_metrics = st.multiselect(
                        "Select metrics to visualize",
                        options=numeric_cols,
                        default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols
                    )
                    
                    if selected_metrics:
                        # Create time series plot
                        if 'timestamp' in filtered_df.columns:
                            # Create time series plot with timestamp on x-axis
                            fig = px.line(
                                filtered_df, 
                                x='timestamp', 
                                y=selected_metrics,
                                title="Time Series of Selected Metrics",
                                labels={"timestamp": "Date & Time", "value": "Measurement", "variable": "Metric"}
                            )
                            
                            # Add moving averages
                            if st.checkbox("Show Moving Average", value=True):
                                window_size = st.slider("Moving Average Window (days)", 1, 30, 7)
                                
                                # Calculate moving averages for selected metrics
                                for metric in selected_metrics:
                                    # Calculate moving average
                                    ma = filtered_df[metric].rolling(window=window_size).mean()
                                    
                                    # Add to plot
                                    fig.add_trace(
                                        go.Scatter(
                                            x=filtered_df['timestamp'],
                                            y=ma,
                                            mode='lines',
                                            line=dict(width=3, dash='dash'),
                                            name=f"{metric} ({window_size}-day MA)"
                                        )
                                    )
                            
                            # Display the chart
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            # Create line chart with index as x-axis if no timestamp
                            fig = px.line(
                                filtered_df, 
                                y=selected_metrics,
                                title="Time Series of Selected Metrics",
                                labels={"index": "Record Index", "value": "Measurement", "variable": "Metric"}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Add download button for the chart data
                        csv = filtered_df[selected_metrics].to_csv(index=False)
                        st.download_button(
                            label="Download Selected Data as CSV",
                            data=csv,
                            file_name="farm_time_series_data.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("Please select at least one metric to visualize.")
                
                # Tab 2: Correlation Analysis
                with viz_tab2:
                    st.subheader("Correlation Analysis")
                    
                    # Calculate correlation matrix for numeric columns
                    if len(numeric_cols) > 1:
                        corr_matrix = filtered_df[numeric_cols].corr()
                        
                        # Create heatmap
                        fig = px.imshow(
                            corr_matrix,
                            text_auto=True,
                            aspect="auto",
                            color_continuous_scale='RdBu_r',
                            title="Correlation Matrix of Farm Metrics"
                        )
                        
                        # Update layout
                        fig.update_layout(height=500)
                        
                        # Display the heatmap
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display interpretation
                        st.markdown("""
                        ### Interpreting the Correlation Matrix
                        
                        - **Strong Positive Correlation (close to 1)**: As one variable increases, the other tends to increase.
                        - **Strong Negative Correlation (close to -1)**: As one variable increases, the other tends to decrease.
                        - **No Correlation (close to 0)**: No apparent relationship between variables.
                        
                        Strong correlations can reveal important relationships between different farm metrics.
                        """)
                        
                        # Scatter plot for exploring relationships
                        st.subheader("Explore Relationships Between Metrics")
                        
                        # Let user select metrics for scatter plot
                        col1, col2 = st.columns(2)
                        with col1:
                            x_metric = st.selectbox("X-axis Metric", numeric_cols)
                        with col2:
                            y_metric = st.selectbox("Y-axis Metric", [c for c in numeric_cols if c != x_metric],
                                                  index=min(1, len(numeric_cols)-1))
                        
                        # Create scatter plot
                        fig = px.scatter(
                            filtered_df,
                            x=x_metric,
                            y=y_metric,
                            title=f"Relationship Between {x_metric} and {y_metric}",
                            trendline="ols"  # Add trend line
                        )
                        
                        # Display the scatter plot
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Calculate and display correlation coefficient
                        corr_value = corr_matrix.loc[x_metric, y_metric]
                        st.metric(
                            label=f"Correlation Coefficient between {x_metric} and {y_metric}",
                            value=f"{corr_value:.3f}"
                        )
                    else:
                        st.info("At least two numeric metrics are required for correlation analysis.")
                
                # Tab 3: Statistical Summary
                with viz_tab3:
                    st.subheader("Statistical Summary")
                    
                    # Display descriptive statistics
                    if numeric_cols:
                        stats_df = filtered_df[numeric_cols].describe().transpose()
                        
                        # Add more useful stats
                        stats_df['range'] = stats_df['max'] - stats_df['min']
                        stats_df['cv'] = (stats_df['std'] / stats_df['mean']) * 100  # Coefficient of variation
                        
                        # Round the values for better display
                        stats_df = stats_df.round(2)
                        
                        # Display stats table
                        st.dataframe(stats_df, use_container_width=True)
                        
                        # Create box plots
                        fig = px.box(
                            filtered_df,
                            y=numeric_cols,
                            title="Distribution of Farm Metrics",
                            labels={"value": "Value", "variable": "Metric"}
                        )
                        
                        # Update layout
                        fig.update_layout(height=100 + (80 * len(numeric_cols)))
                        
                        # Display the box plots
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Create histograms for selected metrics
                        selected_metric = st.selectbox("Select metric for detailed distribution analysis", numeric_cols)
                        
                        # Create histogram
                        fig = px.histogram(
                            filtered_df,
                            x=selected_metric,
                            nbins=20,
                            marginal="box",
                            title=f"Distribution of {selected_metric}",
                            labels={selected_metric: selected_metric}
                        )
                        
                        # Display the histogram
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No numeric metrics available for statistical analysis.")
                
                # Display the raw data table
                st.subheader("Raw Data")
                with st.expander("View Raw Data"):
                    if 'timestamp' in filtered_df.columns:
                        display_df = filtered_df.sort_values('timestamp', ascending=False)
                    else:
                        display_df = filtered_df
                    
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Download button for raw data
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="Download Raw Data as CSV",
                        data=csv,
                        file_name="farm_historical_data.csv",
                        mime="text/csv"
                    )
            else:
                st.error("No data found in the connected Google Sheet. Please check your connection settings.")
                st.image(farming_tech_images[1], caption="Smart Farming Technology", use_container_width=True)
    
    except Exception as e:
        st.error(f"Error analyzing historical data: {str(e)}")
        st.image(farming_tech_images[1], caption="Smart Farming Technology", use_container_width=True)

# Add information about historical data analysis
st.divider()
with st.expander("About Historical Data Analysis"):
    st.write("""
    ## Understanding Historical Data Analysis
    
    Analyzing historical farm data can provide valuable insights into:
    
    - **Long-term trends:** Identify gradual changes in soil health, moisture levels, and other key metrics.
    - **Seasonal patterns:** Understand how your farm conditions vary throughout the year.
    - **Correlations:** Discover relationships between different metrics that can inform better farming decisions.
    - **Anomalies:** Detect unusual events or outliers that may require attention.
    
    ### How to Use This Analysis
    
    1. **Time Series Analysis:** Monitor how metrics change over time to identify trends.
    2. **Correlation Analysis:** Understand how different farm metrics relate to each other.
    3. **Statistical Summary:** Get a comprehensive overview of your farm data distribution.
    
    Use these insights to make data-driven decisions for optimizing crop yields, resource allocation, and overall farm management.
    """)
