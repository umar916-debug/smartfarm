import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from utils.sheets_integration import get_sheet_data
from utils.ml_models import train_crop_recommendation_model, predict_crop
from assets.images import farm_crop_images, farming_tech_images

# Set page configuration
st.set_page_config(
    page_title="Crop Recommendation | Smart Farming",
    page_icon="🌾",
    layout="wide"
)

# Page title
st.title("🌾 Smart Crop Recommendation")

# Check if Google Sheets is configured
if 'google_sheets_configured' not in st.session_state or not st.session_state.google_sheets_configured:
    st.warning("⚠️ Google Sheets connection not configured. Please go to the home page to set up your connection.")
    st.page_link("app.py", label="Go to Home Page", icon="🏠")
else:
    # Load and prepare data
    try:
        with st.spinner("Loading farm data and training recommendation model..."):
            # Get the data from Google Sheets
            df = get_sheet_data(
                st.session_state.spreadsheet_id,
                st.session_state.sheet_name,
                st.session_state.credentials_json
            )
            
            if df is not None and not df.empty:
                # Check if the dataset has the required columns for crop recommendation
                required_features = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph']
                
                # Map common column name variations
                column_mapping = {
                    'n': 'nitrogen',
                    'p': 'phosphorus',
                    'k': 'potassium',
                    'temp': 'temperature',
                    'hum': 'humidity'
                }
                
                # Rename columns if needed
                df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
                
                # Check if we have the necessary features
                missing_features = [feat for feat in required_features if feat not in df.columns]
                
                # Display an explanation of the recommendation system
                st.subheader("How Crop Recommendations Work")
                
                intro_col1, intro_col2 = st.columns([3, 2])
                
                with intro_col1:
                    st.write("""
                    Our smart recommendation system analyzes your farm's environmental conditions 
                    and soil nutrients to suggest the most suitable crops for optimal yield.
                    
                    The system considers:
                    - **Soil Nutrients**: Nitrogen (N), Phosphorus (P), and Potassium (K) levels
                    - **Environmental Factors**: Temperature, Humidity, pH
                    
                    Based on these factors, the machine learning model predicts which crops are 
                    most likely to thrive in your specific farming conditions.
                    """)
                
                with intro_col2:
                    st.image(farm_crop_images[5], use_column_width=True)
                
                # Tab interface for different recommendation methods
                recom_tab1, recom_tab2 = st.tabs(["Get Recommendations", "Parameter Information"])
                
                # Tab 1: Get Recommendations
                with recom_tab1:
                    if missing_features:
                        st.warning(f"Your dataset is missing the following required features: {', '.join(missing_features)}")
                        st.info("Please manually enter values for the missing parameters below.")
                    
                    # Set default values for all parameters
                    default_values = {
                        'nitrogen': 50,
                        'phosphorus': 30,
                        'potassium': 30,
                        'temperature': 25,
                        'humidity': 60,
                        'ph': 6.5
                    }
                    
                    # Try to train the model if we have all required features
                    has_model = False
                    if not missing_features:
                        try:
                            model, features, crops, accuracy = train_crop_recommendation_model(df)
                            st.success(f"Recommendation model trained successfully with {accuracy:.2f}% accuracy")
                            has_model = True
                        except Exception as e:
                            st.warning(f"Model training failed: {str(e)}. Using general recommendations instead.")
                    
                    # Create input form for parameter values
                    st.subheader("Enter Your Farm Parameters")

                    # Get the latest row from the DataFrame if available
                    latest_row = None
                    try:
                        if not df.empty and 'timestamp' in df.columns:
                            latest_row = df.sort_values("timestamp", ascending=False).iloc[0]
                        elif not df.empty:
                            latest_row = df.iloc[-1]  # Use last row if no timestamp
                    except:
                        latest_row = None

                    # Set up columns for input form
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        # Nitrogen input
                        n_value = st.number_input(
                            "Nitrogen (N) content (mg/kg)",
                            min_value=0, max_value=200,
                            value=int(latest_row["nitrogen"]) if latest_row is not None and "nitrogen" in latest_row else default_values['nitrogen'],
                            help="Nitrogen content in soil (mg/kg)"
                        )

                        # Phosphorus input
                        p_value = st.number_input(
                            "Phosphorus (P) content (mg/kg)",
                            min_value=0, max_value=200,
                            value=int(latest_row["phosphorus"]) if latest_row is not None and "phosphorus" in latest_row else default_values['phosphorus'],
                            help="Phosphorus content in soil (mg/kg)"
                        )

                        # Potassium input
                        k_value = st.number_input(
                            "Potassium (K) content (mg/kg)",
                            min_value=0, max_value=200,
                            value=int(latest_row["potassium"]) if latest_row is not None and "potassium" in latest_row else default_values['potassium'],
                            help="Potassium content in soil (mg/kg)"
                        )

                    with col2:
                        # Temperature input
                        temp_value = st.number_input(
                            "Temperature (°C)",
                            min_value=0.0, max_value=50.0,
                            value=float(latest_row["temperature"]) if latest_row is not None and "temperature" in latest_row else default_values['temperature'],
                            help="Average temperature in Celsius"
                        )

                        # Humidity input
                        humidity_value = st.number_input(
                            "Humidity (%)",
                            min_value=0.0, max_value=100.0,
                            value=float(latest_row["humidity"]) if latest_row is not None and "humidity" in latest_row else default_values['humidity'],
                            help="Relative humidity percentage"
                        )

                    with col3:
                        # pH input
                        ph_value = st.number_input(
                            "pH value",
                            min_value=0.0, max_value=14.0,
                            value=float(latest_row["ph"]) if latest_row is not None and "ph" in latest_row else default_values['ph'],
                            help="pH level of soil (0-14)"
                        )

                    # Button to get recommendations
                    if st.button("Get Crop Recommendations"):
                        # Prepare input data
                        input_data = {
                            'nitrogen': n_value,
                            'phosphorus': p_value,
                            'potassium': k_value,
                            'temperature': temp_value,
                            'humidity': humidity_value,
                            'ph': ph_value
                        }
                        
                        # Display the parameters being used
                        st.subheader("Parameters Being Used")
                        param_df = pd.DataFrame.from_dict(input_data, orient='index', columns=['Value'])
                        st.dataframe(param_df.style.format("{:.2f}"))
                        
                        # Use trained model if available, otherwise use a default recommendation logic
                        if has_model:
                            try:
                                recommended_crops, probabilities, parameter_match_info = predict_crop(model, features, crops, input_data)
                                
                                # Display recommendations
                                st.subheader("Recommended Crops")
                                
                                # Create columns for top recommendations
                                rec_cols = st.columns(min(3, len(recommended_crops)))
                                
                                # Define crop information and ideal conditions
                                crop_info = {
                                    'rice': {
                                        'description': 'A staple food crop, rice grows well in warm, humid environments with plenty of water.',
                                        'ideal_conditions': 'Temperature: 20-35°C, Humidity: 80-85%, pH: 5.5-6.5',
                                        'growing_period': '3-6 months'
                                    },
                                    'wheat': {
                                        'description': 'A versatile grain crop that can adapt to many environments but prefers moderate temperatures.',
                                        'ideal_conditions': 'Temperature: 15-25°C, Humidity: 50-70%, pH: 6.0-7.0',
                                        'growing_period': '4-8 months'
                                    },
                                    'maize': {
                                        'description': 'Also known as corn, maize is a warm-season crop that requires plenty of sunlight.',
                                        'ideal_conditions': 'Temperature: 20-30°C, Humidity: 50-80%, pH: 5.8-6.8',
                                        'growing_period': '3-5 months'
                                    },
                                    # ... (rest of crop_info dictionary)
                                }
                                
                                # Display top recommendations with info
                                for i, (crop, probability) in enumerate(zip(recommended_crops, probabilities)):
                                    if i < len(rec_cols):
                                        with rec_cols[i]:
                                            st.markdown(f"### {crop.title()}")
                                            st.progress(probability)
                                            st.write(f"Suitability: {probability:.1f}%")
                                            
                                            # Display crop info if available
                                            if crop.lower() in crop_info:
                                                info = crop_info[crop.lower()]
                                                
                                                with st.expander("Crop Information"):
                                                    st.write(f"**Description**: {info['description']}")
                                                    st.write(f"**Ideal Conditions**: {info['ideal_conditions']}")
                                                    st.write(f"**Growing Period**: {info['growing_period']}")
                                            else:
                                                with st.expander("Crop Information"):
                                                    st.write("Detailed information not available for this crop.")
                                
                                # Create a chart showing all recommendations
                                st.subheader("All Recommended Crops")
                                
                                chart_data = pd.DataFrame({
                                    'Crop': recommended_crops,
                                    'Suitability (%)': probabilities
                                })
                                
                                fig = px.bar(
                                    chart_data, 
                                    x='Crop', 
                                    y='Suitability (%)',
                                    color='Suitability (%)',
                                    color_continuous_scale='Viridis',
                                    title="Crop Suitability Based on Your Farm Parameters"
                                )
                                
                                fig.update_layout(
                                    xaxis_title="Crop Type",
                                    yaxis_title="Suitability (%)",
                                    yaxis_range=[0, 100]
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                            except Exception as e:
                                st.error(f"Error generating recommendations: {str(e)}")
                                has_model = False  # Fall back to general recommendations
                        
                        if not has_model:
                            # General recommendations based on input parameters
                            st.subheader("General Crop Recommendations")
                            st.info("These recommendations are based on general agricultural knowledge.")
                            
                            recommendations = []
                            
                            # pH-based recommendations
                            if ph_value < 5.5:
                                recommendations.append("🌱 **Acidic soil (pH < 5.5)**: Blueberries, Potatoes, Sweet Potatoes")
                            elif 5.5 <= ph_value <= 6.5:
                                recommendations.append("🌾 **Slightly acidic soil (pH 5.5-6.5)**: Strawberries, Corn, Beans, Rice")
                            elif 6.5 < ph_value <= 7.5:
                                recommendations.append("🌻 **Neutral soil (pH 6.5-7.5)**: Wheat, Barley, Sunflowers, Cucumber")
                            else:
                                recommendations.append("🥬 **Alkaline soil (pH > 7.5)**: Asparagus, Beets, Cabbage")
                            
                            # Temperature-based recommendations
                            if temp_value < 15:
                                recommendations.append("❄️ **Cool temperatures (< 15°C)**: Spinach, Lettuce, Kale, Peas")
                            elif 15 <= temp_value <= 25:
                                recommendations.append("🌤️ **Moderate temperatures (15-25°C)**: Wheat, Barley, Carrots, Potatoes")
                            else:
                                recommendations.append("☀️ **Warm temperatures (> 25°C)**: Corn, Tomatoes, Peppers, Rice")
                            
                            # Display recommendations
                            for recommendation in recommendations:
                                st.success(recommendation)
                
                # Tab 2: Parameter Information (unchanged)
                with recom_tab2:
                    # ... (keep the existing Parameter Information tab content)
                    pass
                
            else:
                st.info("No data found in the connected Google Sheet. Please enter your farm parameters manually.")
                
                # Create input form with default values only
                st.subheader("Enter Your Farm Parameters")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    n_value = st.number_input(
                        "Nitrogen (N) content (mg/kg)",
                        min_value=0, max_value=200,
                        value=50,
                        help="Nitrogen content in soil (mg/kg)"
                    )
                    p_value = st.number_input(
                        "Phosphorus (P) content (mg/kg)",
                        min_value=0, max_value=200,
                        value=30,
                        help="Phosphorus content in soil (mg/kg)"
                    )
                    k_value = st.number_input(
                        "Potassium (K) content (mg/kg)",
                        min_value=0, max_value=200,
                        value=30,
                        help="Potassium content in soil (mg/kg)"
                    )
                
                with col2:
                    temp_value = st.number_input(
                        "Temperature (°C)",
                        min_value=0.0, max_value=50.0,
                        value=25.0,
                        help="Average temperature in Celsius"
                    )
                    humidity_value = st.number_input(
                        "Humidity (%)",
                        min_value=0.0, max_value=100.0,
                        value=60.0,
                        help="Relative humidity percentage"
                    )
                
                with col3:
                    ph_value = st.number_input(
                        "pH value",
                        min_value=0.0, max_value=14.0,
                        value=6.5,
                        help="pH level of soil (0-14)"
                    )
                
                if st.button("Get General Recommendations"):
                    # Provide general recommendations
                    st.subheader("General Crop Recommendations")
                    st.info("These recommendations are based on general agricultural knowledge.")
                    
                    recommendations = []
                    
                    # pH-based recommendations
                    if ph_value < 5.5:
                        recommendations.append("🌱 **Acidic soil (pH < 5.5)**: Blueberries, Potatoes, Sweet Potatoes")
                    elif 5.5 <= ph_value <= 6.5:
                        recommendations.append("🌾 **Slightly acidic soil (pH 5.5-6.5)**: Strawberries, Corn, Beans, Rice")
                    elif 6.5 < ph_value <= 7.5:
                        recommendations.append("🌻 **Neutral soil (pH 6.5-7.5)**: Wheat, Barley, Sunflowers, Cucumber")
                    else:
                        recommendations.append("🥬 **Alkaline soil (pH > 7.5)**: Asparagus, Beets, Cabbage")
                    
                    # Temperature-based recommendations
                    if temp_value < 15:
                        recommendations.append("❄️ **Cool temperatures (< 15°C)**: Spinach, Lettuce, Kale, Peas")
                    elif 15 <= temp_value <= 25:
                        recommendations.append("🌤️ **Moderate temperatures (15-25°C)**: Wheat, Barley, Carrots, Potatoes")
                    else:
                        recommendations.append("☀️ **Warm temperatures (> 25°C)**: Corn, Tomatoes, Peppers, Rice")
                    
                    # Display recommendations
                    for recommendation in recommendations:
                        st.success(recommendation)
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please enter your farm parameters manually below.")
        
        # Create input form with default values only
        st.subheader("Enter Your Farm Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            n_value = st.number_input(
                "Nitrogen (N) content (mg/kg)",
                min_value=0, max_value=200,
                value=50,
                help="Nitrogen content in soil (mg/kg)"
            )
            p_value = st.number_input(
                "Phosphorus (P) content (mg/kg)",
                min_value=0, max_value=200,
                value=30,
                help="Phosphorus content in soil (mg/kg)"
            )
            k_value = st.number_input(
                "Potassium (K) content (mg/kg)",
                min_value=0, max_value=200,
                value=30,
                help="Potassium content in soil (mg/kg)"
            )
        
        with col2:
            temp_value = st.number_input(
                "Temperature (°C)",
                min_value=0.0, max_value=50.0,
                value=25.0,
                help="Average temperature in Celsius"
            )
            humidity_value = st.number_input(
                "Humidity (%)",
                min_value=0.0, max_value=100.0,
                value=60.0,
                help="Relative humidity percentage"
            )
        
        with col3:
            ph_value = st.number_input(
                "pH value",
                min_value=0.0, max_value=14.0,
                value=6.5,
                help="pH level of soil (0-14)"
            )
        
        if st.button("Get General Recommendations"):
            # Provide general recommendations
            st.subheader("General Crop Recommendations")
            st.info("These recommendations are based on general agricultural knowledge.")
            
            recommendations = []
            
            # pH-based recommendations
            if ph_value < 5.5:
                recommendations.append("🌱 **Acidic soil (pH < 5.5)**: Blueberries, Potatoes, Sweet Potatoes")
            elif 5.5 <= ph_value <= 6.5:
                recommendations.append("🌾 **Slightly acidic soil (pH 5.5-6.5)**: Strawberries, Corn, Beans, Rice")
            elif 6.5 < ph_value <= 7.5:
                recommendations.append("🌻 **Neutral soil (pH 6.5-7.5)**: Wheat, Barley, Sunflowers, Cucumber")
            else:
                recommendations.append("🥬 **Alkaline soil (pH > 7.5)**: Asparagus, Beets, Cabbage")
            
            # Temperature-based recommendations
            if temp_value < 15:
                recommendations.append("❄️ **Cool temperatures (< 15°C)**: Spinach, Lettuce, Kale, Peas")
            elif 15 <= temp_value <= 25:
                recommendations.append("🌤️ **Moderate temperatures (15-25°C)**: Wheat, Barley, Carrots, Potatoes")
            else:
                recommendations.append("☀️ **Warm temperatures (> 25°C)**: Corn, Tomatoes, Peppers, Rice")
            
            # Display recommendations
            for recommendation in recommendations:
                st.success(recommendation)

# About section (unchanged)
st.divider()
with st.expander("About the Recommendation System"):
    # ... (keep the existing About section content)
    pass            
