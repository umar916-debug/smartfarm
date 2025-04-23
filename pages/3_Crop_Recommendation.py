import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

from utils.sheets_integration import get_sheet_data
from utils.ml_models import train_crop_recommendation_model, predict_crop
from assets.images import farm_crop_images

# --- Page Configuration ---
st.set_page_config(
    page_title="Crop Recommendation | Smart Farming",
    page_icon="🌾",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌾 Smart Crop Recommendation")

# --- Helper: General Recommendation Logic ---
def display_general_recommendations(params):
    st.subheader("General Crop Recommendations")
    recs = []
    pH = params['ph']
    temp = params['temperature']

    if pH < 5.5:
        recs.append("🌱 **Acidic soil**: Blueberries, Potatoes, Sweet Potatoes")
    elif 5.5 <= pH <= 6.5:
        recs.append("🌾 **Slightly acidic soil**: Strawberries, Corn, Beans, Rice")
    elif 6.5 < pH <= 7.5:
        recs.append("🌻 **Neutral soil**: Wheat, Barley, Sunflowers, Cucumber")
    else:
        recs.append("🥬 **Alkaline soil**: Asparagus, Beets, Cabbage")

    if temp < 15:
        recs.append("❄️ **Cool temperatures**: Lettuce, Kale, Spinach, Peas")
    elif 15 <= temp <= 25:
        recs.append("🌤️ **Moderate temperatures**: Carrots, Potatoes, Wheat, Barley")
    else:
        recs.append("☀️ **Warm temperatures**: Tomatoes, Peppers, Corn, Rice")

    for rec in recs:
        st.success(rec)

# --- Google Sheets Check ---
if 'google_sheets_configured' not in st.session_state or not st.session_state.google_sheets_configured:
    st.warning("⚠️ Google Sheets connection not configured.")
    st.page_link("app.py", label="Go to Home Page", icon="🏠")
    st.stop()

# --- Auto-refresh every 60 seconds ---
REFRESH_INTERVAL = 60
if 'last_refresh' not in st.session_state or time.time() - st.session_state.last_refresh > REFRESH_INTERVAL:
    st.session_state.last_refresh = time.time()
    st.rerun()

try:
    with st.spinner("Loading data and training model..."):
        df = get_sheet_data(
            st.session_state.spreadsheet_id,
            st.session_state.sheet_name,
            st.session_state.credentials_json
        )

    if df is None or df.empty:
        raise ValueError("No data found.")

    column_mapping = {
        'n': 'nitrogen', 'p': 'phosphorus', 'k': 'potassium',
        'temp': 'temperature', 'hum': 'humidity'
    }
    df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)

    required_features = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph']
    missing_features = [feat for feat in required_features if feat not in df.columns]

    st.subheader("📊 How Crop Recommendations Work")
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("""
        Our ML system analyzes your farm’s environment and nutrients to suggest optimal crops.

        **Features used:**
        - 🌱 **Soil Nutrients**: Nitrogen (N), Phosphorus (P), Potassium (K)
        - 🌦️ **Climate**: Temperature, Humidity, Soil pH
        """)
    with col2:
        st.image(farm_crop_images[5], use_container_width=True)

    tab1, tab2 = st.tabs(["🌾 Get Recommendations", "ℹ️ Parameter Info"])

    with tab1:
        default_values = {
            'nitrogen': 50, 'phosphorus': 30, 'potassium': 30,
            'temperature': 25.0, 'humidity': 60.0, 'ph': 6.5
        }

        latest_row = None
        if 'timestamp' in df.columns:
            latest_row = df.sort_values('timestamp', ascending=False).iloc[0]
        elif not df.empty:
            latest_row = df.iloc[-1]

        def get_param(name, default):
            return float(latest_row[name]) if latest_row is not None and name in latest_row else default

        # Initialize/reset session state
        if 'input_params' not in st.session_state:
            st.session_state.input_params = {
                k: get_param(k, default_values[k]) for k in default_values
            }

        st.subheader("📥 Enter Your Farm Parameters")
        c1, c2, c3 = st.columns(3)
        with c1:
            n = st.number_input("Nitrogen (mg/kg)", min_value=0, max_value=200, value=int(st.session_state.input_params["nitrogen"]))
            p = st.number_input("Phosphorus (mg/kg)", min_value=0, max_value=200, value=int(st.session_state.input_params["phosphorus"]))
            k = st.number_input("Potassium (mg/kg)", min_value=0, max_value=200, value=int(st.session_state.input_params["potassium"]))
        with c2:
            temp = st.number_input("Temperature (°C)", min_value=0.0, max_value=50.0, value=st.session_state.input_params["temperature"])
            hum = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=st.session_state.input_params["humidity"])
        with c3:
            ph = st.number_input("pH", min_value=0.0, max_value=14.0, value=st.session_state.input_params["ph"])

        input_data = {
            'nitrogen': n, 'phosphorus': p, 'potassium': k,
            'temperature': temp, 'humidity': hum, 'ph': ph
        }

        # Save updated values
        st.session_state.input_params = input_data

        st.subheader("📊 Used Parameters")
        st.dataframe(pd.DataFrame.from_dict(input_data, orient='index', columns=['Value']).style.format("{:.2f}"), use_container_width=True)

        # Buttons
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            get_recommend = st.button("🌱 Get Crop Recommendations")
        with col_btn2:
            if st.button("🔄 Reset Parameters"):
                st.session_state.input_params = default_values
                st.rerun()

        if get_recommend:
            if not missing_features:
                try:
                    model, features, crops, accuracy = train_crop_recommendation_model(df)
                    st.success(f"✅ Model trained with {accuracy:.2f}% accuracy")

                    recs, probs, _ = predict_crop(model, features, crops, input_data)

                    st.subheader("🌿 Recommended Crops")
                    cols = st.columns(min(3, len(recs)))
                    for i, (crop, prob) in enumerate(zip(recs, probs)):
                        with cols[i]:
                            st.markdown(f"### {crop.title()}")
                            st.progress(prob)
                            st.write(f"Suitability: {prob:.1f}%")

                    st.subheader("📈 Suitability Chart")
                    chart_data = pd.DataFrame({'Crop': recs, 'Suitability (%)': probs})
                    fig = px.bar(chart_data, x='Crop', y='Suitability (%)', color='Suitability (%)',
                                 color_continuous_scale='Viridis', title="Crop Suitability")
                    fig.update_layout(yaxis_range=[0, 100])
                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Prediction error: {e}")
                    display_general_recommendations(input_data)
            else:
                st.warning(f"Missing features: {', '.join(missing_features)}. Using fallback.")
                display_general_recommendations(input_data)

    with tab2:
        st.markdown("""
        ### 🧪 Parameter Details
        - **Nitrogen (N)**: Encourages leafy growth.
        - **Phosphorus (P)**: Stimulates root development.
        - **Potassium (K)**: Improves disease resistance.
        - **Temperature**: Affects plant metabolism.
        - **Humidity**: Impacts water uptake and disease pressure.
        - **pH**: Influences nutrient availability and uptake.
        """)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please enter parameters manually.")
    display_general_recommendations({
        'nitrogen': 50, 'phosphorus': 30, 'potassium': 30,
        'temperature': 25.0, 'humidity': 60.0, 'ph': 6.5
    })

# --- About Section ---
st.divider()
with st.expander("ℹ️ About the Recommendation System"):
    st.write("""
    This smart farming tool uses machine learning to personalize crop recommendations 
    based on your farm’s nutrient profile and climate conditions. 
    It also supports Google Sheets integration for real-time monitoring.
    """)
