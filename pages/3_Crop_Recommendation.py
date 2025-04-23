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
                # Removed 'rainfall' from required features
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
                    - **Environmental Factors**: Temperature, Humidity, pH, and Rainfall
                    
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
                        st.warning(f"Your dataset is missing the following required features for crop recommendation: {', '.join(missing_features)}")
                        st.info("You can still get recommendations by manually entering values below.")
                        
                        # Set default values
                        default_values = {
                            'nitrogen': 50,
                            'phosphorus': 30,
                            'potassium': 30,
                            'temperature': 25,
                            'humidity': 60,
                            'ph': 6.5
                        }
                        
                        has_model = False
                    else:
                        # Train the model if we have all required features
                        model, features, crops, accuracy = train_crop_recommendation_model(df)
                        
                        # Display model info
                        st.success(f"Recommendation model trained successfully with {accuracy:.2f}% accuracy")
                        
                        # Get average values from dataset to use as defaults
                        default_values = {feature: df[feature].mean() for feature in required_features}
                        
                        has_model = True
                    
                    # Create input form for parameter values
                    st.subheader("Enter Your Farm Parameters")

                    # Get the latest row from the DataFrame based on timestamp
                    latest_row = df.sort_values("timestamp", ascending=False).iloc[0]

                    # Set up columns for input form
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        n_value = st.number_input("Nitrogen (N) content (mg/kg)", 
                                                min_value=0, max_value=200, 
                                                value=int(latest_row["nitrogen"]),
                                                help="Nitrogen content in soil (mg/kg)")

                        p_value = st.number_input("Phosphorus (P) content (mg/kg)", 
                                                min_value=0, max_value=200, 
                                                value=int(latest_row["phosphorus"]),
                                                help="Phosphorus content in soil (mg/kg)")

                        k_value = st.number_input("Potassium (K) content (mg/kg)", 
                                                min_value=0, max_value=200, 
                                                value=int(latest_row["potassium"]),
                                                help="Potassium content in soil (mg/kg)")

                    with col2:
                        temp_value = st.number_input("Temperature (°C)", 
                                                    min_value=0.0, max_value=50.0, 
                                                    value=float(latest_row["temperature"]),
                                                    help="Average temperature in Celsius")

                        humidity_value = st.number_input("Humidity (%)", 
                                                        min_value=0.0, max_value=100.0, 
                                                        value=float(latest_row["humidity"]),
                                                        help="Relative humidity percentage")

                    with col3:
                        ph_value = st.number_input("pH value", 
                                                  min_value=0.0, max_value=14.0, 
                                                  value=float(latest_row["ph"]),
                                                  help="pH level of soil (0-14)")

                    # Button to get recommendations
                    if st.button("Get Crop Recommendations"):
                        # Prepare input data (removed rainfall)
                        input_data = {
                            'nitrogen': n_value,
                            'phosphorus': p_value,
                            'potassium': k_value,
                            'temperature': temp_value,
                            'humidity': humidity_value,
                            'ph': ph_value
                        }
                        
                        # Use trained model if available, otherwise use a default recommendation logic
                        if has_model:
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
                                'cotton': {
                                    'description': 'A fiber crop that grows best in warm climates with moderate rainfall.',
                                    'ideal_conditions': 'Temperature: 20-35°C, Humidity: 60-70%, pH: 5.8-7.0',
                                    'growing_period': '5-6 months'
                                },
                                'sugarcane': {
                                    'description': 'A tropical grass that produces sugar and requires plenty of water and sunlight.',
                                    'ideal_conditions': 'Temperature: 24-34°C, Humidity: 60-80%, pH: 6.0-7.5',
                                    'growing_period': '9-24 months'
                                },
                                'jute': {
                                    'description': 'A fiber crop that grows best in warm and humid conditions.',
                                    'ideal_conditions': 'Temperature: 25-35°C, Humidity: 70-90%, pH: 6.0-7.5',
                                    'growing_period': '3-4 months'
                                },
                                'coffee': {
                                    'description': 'A tropical perennial crop that grows best in moderate temperatures.',
                                    'ideal_conditions': 'Temperature: 15-25°C, Humidity: 60-80%, pH: 5.5-6.5',
                                    'growing_period': 'Perennial (3-4 years for first harvest)'
                                },
                                'mungbean': {
                                    'description': 'A legume crop that fixes nitrogen in the soil and grows well in warm conditions.',
                                    'ideal_conditions': 'Temperature: 20-35°C, Humidity: 50-80%, pH: 6.2-7.2',
                                    'growing_period': '2-3 months'
                                },
                                'chickpea': {
                                    'description': 'A drought-resistant legume crop with nitrogen-fixing properties.',
                                    'ideal_conditions': 'Temperature: 15-30°C, Humidity: 40-60%, pH: 5.5-7.0',
                                    'growing_period': '3-4 months'
                                },
                                'kidneybeans': {
                                    'description': 'A legume crop that requires moderate temperatures and rainfall.',
                                    'ideal_conditions': 'Temperature: 20-30°C, Humidity: 50-70%, pH: 6.0-7.5',
                                    'growing_period': '3-4 months'
                                },
                                'pigeonpeas': {
                                    'description': 'A drought-resistant legume crop that improves soil fertility.',
                                    'ideal_conditions': 'Temperature: 20-35°C, Humidity: 40-70%, pH: 5.0-7.0',
                                    'growing_period': '4-6 months'
                                },
                                'mothbeans': {
                                    'description': 'A drought-resistant legume crop suitable for semi-arid regions.',
                                    'ideal_conditions': 'Temperature: 25-35°C, Humidity: 30-60%, pH: 6.0-7.5',
                                    'growing_period': '3-4 months'
                                },
                                'blackgram': {
                                    'description': 'A legume crop that grows well in warm and humid conditions.',
                                    'ideal_conditions': 'Temperature: 25-35°C, Humidity: 50-80%, pH: 6.0-7.5',
                                    'growing_period': '2-3 months'
                                },
                                'lentil': {
                                    'description': 'A cool-season legume crop that is highly nutritious.',
                                    'ideal_conditions': 'Temperature: 15-25°C, Humidity: 40-70%, pH: 6.0-8.0',
                                    'growing_period': '3-4 months'
                                },
                                'pomegranate': {
                                    'description': 'A drought-resistant fruit tree that grows well in semi-arid conditions.',
                                    'ideal_conditions': 'Temperature: 20-35°C, Humidity: 40-60%, pH: 5.5-7.2',
                                    'growing_period': 'Perennial (3-5 years for first harvest)'
                                },
                                'banana': {
                                    'description': 'A tropical fruit crop that requires plenty of water and nutrients.',
                                    'ideal_conditions': 'Temperature: 20-35°C, Humidity: 70-90%, pH: 5.5-7.0',
                                    'growing_period': '9-12 months'
                                },
                                'mango': {
                                    'description': 'A tropical fruit tree that grows well in warm climates with a distinct dry season.',
                                    'ideal_conditions': 'Temperature: 24-30°C, Humidity: 50-80%, pH: 5.5-7.5',
                                    'growing_period': 'Perennial (4-5 years for first harvest)'
                                },
                                'grapes': {
                                    'description': 'A perennial vine that produces fruit clusters and prefers temperate climates.',
                                    'ideal_conditions': 'Temperature: 15-30°C, Humidity: 40-70%, pH: 6.0-7.0',
                                    'growing_period': 'Perennial (2-3 years for first harvest)'
                                },
                                'watermelon': {
                                    'description': 'A warm-season fruit crop that requires plenty of sunlight and water.',
                                    'ideal_conditions': 'Temperature: 20-35°C, Humidity: 50-70%, pH: 6.0-7.0',
                                    'growing_period': '3-4 months'
                                },
                                'muskmelon': {
                                    'description': 'A warm-season fruit crop similar to watermelon but with different water requirements.',
                                    'ideal_conditions': 'Temperature: 20-30°C, Humidity: 50-70%, pH: 6.0-7.0',
                                    'growing_period': '3-4 months'
                                },
                                'apple': {
                                    'description': 'A deciduous fruit tree that requires cool winters for proper dormancy.',
                                    'ideal_conditions': 'Temperature: 15-25°C, Humidity: 50-70%, pH: 6.0-7.0',
                                    'growing_period': 'Perennial (3-5 years for first harvest)'
                                },
                                'orange': {
                                    'description': 'A citrus fruit tree that grows well in subtropical climates.',
                                    'ideal_conditions': 'Temperature: 20-35°C, Humidity: 40-70%, pH: 5.5-6.5',
                                    'growing_period': 'Perennial (3-5 years for first harvest)'
                                },
                                'papaya': {
                                    'description': 'A fast-growing tropical fruit tree with year-round harvesting.',
                                    'ideal_conditions': 'Temperature: 20-35°C, Humidity: 60-80%, pH: 6.0-7.0',
                                    'growing_period': '8-10 months for first harvest'
                                },
                                'coconut': {
                                    'description': 'A tropical palm tree that grows well in coastal areas with high humidity.',
                                    'ideal_conditions': 'Temperature: 25-35°C, Humidity: 70-90%, pH: 5.5-7.0',
                                    'growing_period': 'Perennial (6-10 years for first harvest)'
                                }
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
                            
                            # Update layout
                            fig.update_layout(
                                xaxis_title="Crop Type",
                                yaxis_title="Suitability (%)",
                                yaxis_range=[0, 100]
                            )
                            
                            # Display the chart
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Add parameter match information (new feature)
                            st.subheader("Parameter Match Analysis")
                            st.write("This analysis shows how well your current farm parameters match the ideal conditions for each recommended crop.")
                            
                            # Create tabs for parameter comparison
                            if parameter_match_info and len(parameter_match_info) > 0:
                                match_tabs = st.tabs([f"{crop.title()}" for crop in recommended_crops[:3]])
                                
                                for i, crop in enumerate(recommended_crops[:3]):
                                    if crop in parameter_match_info:
                                        with match_tabs[i]:
                                            match_info = parameter_match_info[crop]
                                            
                                            # Display overall match percentage
                                            st.markdown(f"""
                                            <div style="background-color: rgba(45, 45, 45, 0.7); padding: 15px; border-radius: 10px; 
                                                border-left: 5px solid #4CAF50; margin: 20px 0; text-align: center;">
                                                <h3 style="margin: 0; color: #4CAF50;">Overall Match: {match_info['overall']}%</h3>
                                                <p style="margin: 5px 0 0 0; font-size: 14px;">How well your farm parameters match {crop.title()}'s ideal growing conditions</p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                            
                                            # Create parameter match table
                                            col1, col2 = st.columns([3, 2])
                                            
                                            with col1:
                                                # Create a parameter comparison dataframe
                                                match_data = []
                                                for param, match_percent in match_info['matches'].items():
                                                    if param in input_data and param in match_info['ideal_ranges']:
                                                        ideal_range = match_info['ideal_ranges'][param]
                                                        match_data.append({
                                                            'Parameter': param.title(),
                                                            'Your Value': input_data[param],
                                                            'Ideal Range': f"{ideal_range[0]} - {ideal_range[1]}" if isinstance(ideal_range, tuple) else ideal_range,
                                                            'Match (%)': match_percent if isinstance(match_percent, (int, float)) else 'N/A'
                                                        })
                                                
                                                match_df = pd.DataFrame(match_data)
                                                st.table(match_df)
                                            
                                            with col2:
                                                # Create visualization of parameter matches
                                                if any(isinstance(m, (int, float)) for m in match_info['matches'].values()):
                                                    match_viz_data = {
                                                        'Parameter': [p.title() for p in match_info['matches'].keys() if isinstance(match_info['matches'][p], (int, float))],
                                                        'Match (%)': [m for m in match_info['matches'].values() if isinstance(m, (int, float))]
                                                    }
                                                    
                                                    match_viz_df = pd.DataFrame(match_viz_data)
                                                    
                                                    # Create a bar chart for parameter matches
                                                    fig = px.bar(match_viz_df, x='Parameter', y='Match (%)', 
                                                                color='Match (%)',
                                                                color_continuous_scale=[(0, "red"), (0.5, "yellow"), (1, "green")],
                                                                labels={'Match (%)': 'Match Percentage'},
                                                                title=f'Parameter Match for {crop.title()}')
                                                    
                                                    fig.update_layout(height=300)
                                                    st.plotly_chart(fig, use_container_width=True)
                                                
                                            # Add recommendations based on parameter matches
                                            st.subheader("Improvement Suggestions")
                                            suggestions = []
                                            
                                            for param, match_percent in match_info['matches'].items():
                                                if isinstance(match_percent, (int, float)) and match_percent < 70:
                                                    ideal_range = match_info['ideal_ranges'].get(param, None)
                                                    if ideal_range and isinstance(ideal_range, tuple):
                                                        current_val = input_data.get(param, 0)
                                                        min_val, max_val = ideal_range
                                                        
                                                        if current_val < min_val:
                                                            suggestions.append(f"Increase {param.title()} from {current_val} to at least {min_val}")
                                                        elif current_val > max_val:
                                                            suggestions.append(f"Decrease {param.title()} from {current_val} to below {max_val}")
                                            
                                            if suggestions:
                                                for suggestion in suggestions:
                                                    st.markdown(f"- {suggestion}")
                                            else:
                                                st.write("Your parameters are generally well-suited for this crop. No major adjustments needed.")
                            else:
                                st.info("Parameter match information is not available for these crops.")
                            
                        else:
                            # If model not available, provide general recommendations based on input
                            st.subheader("Parameter-Based Recommendations")
                            st.info("Recommendations are based on general agricultural knowledge since a complete dataset is not available.")
                            
                            # Simple recommendation logic based on input parameters
                            recommendations = []
                            
                            # pH-based recommendations
                            if ph_value < 5.5:
                                recommendations.append("Crops suitable for acidic soil (pH < 5.5): Blueberries, Potatoes, Sweet Potatoes")
                            elif 5.5 <= ph_value <= 6.5:
                                recommendations.append("Crops suitable for slightly acidic soil (pH 5.5-6.5): Strawberries, Corn, Beans, Rice")
                            elif 6.5 < ph_value <= 7.5:
                                recommendations.append("Crops suitable for neutral soil (pH 6.5-7.5): Wheat, Barley, Sunflowers, Cucumber")
                            else:
                                recommendations.append("Crops suitable for alkaline soil (pH > 7.5): Asparagus, Beets, Cabbage")
                            
                            # Temperature-based recommendations
                            if temp_value < 15:
                                recommendations.append("Crops suitable for cool temperatures (< 15°C): Spinach, Lettuce, Kale, Peas")
                            elif 15 <= temp_value <= 25:
                                recommendations.append("Crops suitable for moderate temperatures (15-25°C): Wheat, Barley, Carrots, Potatoes")
                            else:
                                recommendations.append("Crops suitable for warm temperatures (> 25°C): Corn, Tomatoes, Peppers, Rice")
                            
                            # Display recommendations
                            for recommendation in recommendations:
                                st.success(recommendation)
                            
                            # Display input parameters summary
                            st.subheader("Your Input Parameters")
                            
                            # Create a radar chart of input parameters
                            # Normalize the values for better visualization (removed rainfall)
                            param_names = ['N', 'P', 'K', 'Temperature', 'Humidity', 'pH']
                            
                            # Create normalized values for radar chart
                            norm_values = [
                                n_value / 100,  # N (normalized to 0-2)
                                p_value / 100,  # P (normalized to 0-2)
                                k_value / 100,  # K (normalized to 0-2)
                                temp_value / 40,  # Temp (normalized to 0-1.25)
                                humidity_value / 100,  # Humidity (normalized to 0-1)
                                ph_value / 14,  # pH (normalized to 0-1)
                            ]
                            
                            # Create radar chart
                            fig = plt.figure(figsize=(8, 6))
                            ax = fig.add_subplot(111, polar=True)
                            
                            # Plot the data
                            angles = np.linspace(0, 2*np.pi, len(param_names), endpoint=False).tolist()
                            norm_values.append(norm_values[0])  # Complete the loop
                            angles.append(angles[0])  # Complete the loop
                            
                            # Create the plot
                            ax.plot(angles, norm_values, 'o-', linewidth=2)
                            ax.fill(angles, norm_values, alpha=0.25)
                            
                            # Set the labels
                            ax.set_thetagrids(np.degrees(angles[:-1]), param_names)
                            
                            # Set title
                            ax.set_title("Farm Parameter Profile", y=1.1)
                            
                            # Display the chart
                            st.pyplot(fig)
                
                # Tab 2: Parameter Information
                with recom_tab2:
                    st.subheader("Understanding Farm Parameters")
                    
                    # Create expandable sections for each parameter type
                    with st.expander("Soil Nutrients (N, P, K)"):
                        st.markdown("""
                        ### Nitrogen (N)
                        
                        Nitrogen is essential for leaf growth and crop yield. It's a crucial component of chlorophyll, 
                        amino acids, proteins, and enzymes.
                        
                        - **Low N (0-30 mg/kg)**: Plants often show yellowing of leaves, stunted growth
                        - **Medium N (30-60 mg/kg)**: Adequate for most non-leafy crops
                        - **High N (60+ mg/kg)**: Ideal for leafy vegetables and high-yield cereals
                        
                        ### Phosphorus (P)
                        
                        Phosphorus is vital for root development, flowering, fruiting, and seed formation.
                        
                        - **Low P (0-10 mg/kg)**: Plants may show stunted root growth, delayed maturity
                        - **Medium P (10-30 mg/kg)**: Suitable for most crops
                        - **High P (30+ mg/kg)**: Beneficial for root crops and fruiting plants
                        
                        ### Potassium (K)
                        
                        Potassium contributes to overall plant health, disease resistance, and water regulation.
                        
                        - **Low K (0-20 mg/kg)**: Plants may show weakness, susceptibility to disease
                        - **Medium K (20-40 mg/kg)**: Adequate for most crops
                        - **High K (40+ mg/kg)**: Ideal for root crops, fruits, and drought resistance
                        
                        **Source**: FAO Soils Portal, Agricultural Extension Services
                        """)
                    
                    with st.expander("Environmental Factors"):
                        st.markdown("""
                        ### Temperature
                        
                        Temperature affects plant growth rates, germination, and developmental stages.
                        
                        - **Cool (0-15°C)**: Suitable for cold-season crops like spinach, kale, peas
                        - **Moderate (15-25°C)**: Optimal for many common crops like wheat, barley, potatoes
                        - **Warm (25-35°C)**: Ideal for heat-loving crops like corn, tomatoes, melons
                        - **Hot (35°C+)**: Only specialized crops can thrive
                        
                        ### Humidity
                        
                        Humidity affects transpiration, pollination, and disease susceptibility.
                        
                        - **Low (20-40%)**: Better for drought-resistant crops, reduced fungal diseases
                        - **Medium (40-70%)**: Suitable for most crops
                        - **High (70-90%)**: Best for tropical crops like rice, banana, sugarcane
                        
                        ### pH Value
                        
                        Soil pH affects nutrient availability and microbial activity.
                        
                        - **Acidic (pH < 6.0)**: Good for acid-loving crops like blueberries, potatoes
                        - **Slightly Acidic to Neutral (pH 6.0-7.0)**: Optimal for most crops
                        - **Alkaline (pH > 7.0)**: Suitable for beets, asparagus, cabbage
                        
                        ### Rainfall
                        
                        Annual rainfall determines water availability and irrigation needs.
                        
                        - **Low (< 600 mm/year)**: Suitable for drought-resistant crops like millet, sorghum
                        - **Medium (600-1200 mm/year)**: Good for most common crops
                        - **High (1200+ mm/year)**: Ideal for water-intensive crops like rice, sugarcane
                        
                        **Sources**: FAO, USDA, Agricultural Research Services
                        """)
                    
                    with st.expander("Recommended Parameter Ranges by Crop Type"):
                        st.markdown("""
                        ### Cereals
                        - **Rice**: N (80-100 mg/kg), P (30-50 mg/kg), K (60-80 mg/kg), pH (5.5-6.5), Rainfall (1200-1800 mm)
                        - **Wheat**: N (40-60 mg/kg), P (20-40 mg/kg), K (30-50 mg/kg), pH (6.0-7.0), Rainfall (450-650 mm)
                        - **Maize**: N (60-80 mg/kg), P (30-50 mg/kg), K (40-60 mg/kg), pH (5.8-6.8), Rainfall (500-800 mm)
                        
                        ### Legumes
                        - **Chickpea**: N (20-30 mg/kg), P (40-60 mg/kg), K (30-40 mg/kg), pH (6.0-8.0), Rainfall (600-1000 mm)
                        - **Lentil**: N (20-30 mg/kg), P (40-50 mg/kg), K (30-40 mg/kg), pH (6.0-8.0), Rainfall (350-500 mm)
                        - **Beans**: N (40-60 mg/kg), P (30-50 mg/kg), K (50-60 mg/kg), pH (6.0-7.0), Rainfall (400-600 mm)
                        
                        ### Fruits
                        - **Apple**: N (40-80 mg/kg), P (30-60 mg/kg), K (120-180 mg/kg), pH (5.8-7.0), Rainfall (800-1200 mm)
                        - **Banana**: N (90-120 mg/kg), P (30-40 mg/kg), K (160-200 mg/kg), pH (5.5-7.0), Rainfall (1500-2500 mm)
                        - **Citrus**: N (50-80 mg/kg), P (30-50 mg/kg), K (50-100 mg/kg), pH (5.5-6.5), Rainfall (1200-1500 mm)
                        
                        **Sources**: ICAR (Indian Council of Agricultural Research), FAO, Agricultural Universities
                        """)
                    
                    # Citation information
                    st.info("""
                    **Parameter information sources:**
                    
                    - FAO (Food and Agriculture Organization of the United Nations)
                    - USDA (United States Department of Agriculture)
                    - ICAR (Indian Council of Agricultural Research)
                    - Agricultural Universities and Research Stations
                    """)
            else:
                st.error("No data found in the connected Google Sheet. Please check your connection settings.")
                st.image(farming_tech_images[2], caption="Smart Farming Technology", use_container_width=True)
    
    except Exception as e:
        st.error(f"Error generating crop recommendations: {str(e)}")
        st.image(farming_tech_images[2], caption="Smart Farming Technology", use_container_width=True)

# Add information about the crop recommendation system
st.divider()
with st.expander("About the Recommendation System"):
    st.write("""
    ## How Our Crop Recommendation Works
    
    Our recommendation system uses machine learning to analyze your farm's environmental conditions
    and soil nutrients, matching them with crops that are likely to thrive in those specific conditions.
    
    ### The Recommendation Process
    
    1. **Data Collection**: We gather data about your farm's soil nutrients (N, P, K), pH levels, 
       temperature, humidity, and rainfall.
       
    2. **Machine Learning Analysis**: Our model compares your farm's conditions with thousands of 
       data points on optimal growing conditions for different crops.
       
    3. **Recommendation Generation**: The system identifies crops that are most likely to succeed
       in your specific farming environment.
       
    4. **Confidence Scoring**: Each recommendation includes a suitability percentage indicating
       how well your conditions match the ideal growing environment for that crop.
    
    ### Data Sources
    
    Our recommendation system uses data from agricultural research institutions, including:
    
    - FAO (Food and Agriculture Organization)
    - ICAR (Indian Council of Agricultural Research)
    - USDA (United States Department of Agriculture)
    - Public agricultural universities and research stations
    
    ### Improving Recommendations
    
    The more data you provide about your farm, the more accurate our recommendations become.
    Consider regular soil testing and weather monitoring for optimal results.
    """)
