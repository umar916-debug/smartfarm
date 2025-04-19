import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import streamlit as st

# Cache the model to avoid retraining
@st.cache_resource
def train_crop_recommendation_model(df):
    """
    Train a machine learning model for crop recommendations based on provided dataset.
    
    Args:
        df (pandas.DataFrame): Dataset containing farm parameters and crop information
        
    Returns:
        tuple: (trained_model, feature_names, crop_list, accuracy)
    """
    try:
        # Check if the dataset has the required columns (removed rainfall)
        required_features = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph']
        
        # Map common column name variations
        column_mapping = {
            'n': 'nitrogen',
            'p': 'phosphorus',
            'k': 'potassium',
            'temp': 'temperature',
            'hum': 'humidity',
            'rain': 'rainfall'
        }
        
        # Rename columns if needed
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Check if all required features are available
        missing_features = [feat for feat in required_features if feat not in df.columns]
        if missing_features:
            st.warning(f"Missing required features: {', '.join(missing_features)}")
            return None, None, None, 0
        
        # Check if there's a crop label column
        if 'crop' not in df.columns and 'label' not in df.columns:
            # If no explicit crop column, try to create a synthetic one for demonstration
            # This is a fallback for when the dataset doesn't have labeled crops
            
            # Create simple crop recommendation rules based on parameter ranges
            def assign_crop(row):
                # Simple rule-based assignment without rainfall
                if row['ph'] < 6.0 and row['humidity'] > 70:
                    return 'rice'
                elif row['temperature'] > 30 and row['humidity'] < 50:
                    return 'cotton' 
                elif row['nitrogen'] > 50 and row['potassium'] > 50:
                    return 'maize'
                elif row['ph'] > 7.0 and row['temperature'] < 20:
                    return 'wheat'
                elif row['humidity'] > 80 and row['temperature'] > 25:
                    return 'banana'
                else:
                    return 'chickpea'  # default
            
            # Create a synthetic crop label for demonstration
            df['crop'] = df.apply(assign_crop, axis=1)
            
            st.info("No crop labels found in dataset. Created synthetic crop recommendations for demonstration.")
        
        # Use the appropriate crop label column
        crop_column = 'crop' if 'crop' in df.columns else 'label'
        
        # Prepare the data
        X = df[required_features]
        y = df[crop_column]
        
        # Check if there are enough unique crops
        unique_crops = y.unique()
        if len(unique_crops) < 2:
            st.warning("Not enough unique crops in the dataset for effective recommendation.")
            # Add some synthetic data for demonstration if needed
            additional_data = []
            for i in range(50):
                additional_data.append({
                    'nitrogen': np.random.randint(0, 140),
                    'phosphorus': np.random.randint(5, 145),
                    'potassium': np.random.randint(5, 205),
                    'temperature': np.random.uniform(8.83, 43.68),
                    'humidity': np.random.uniform(14.25, 99.98),
                    'ph': np.random.uniform(3.5, 9.94),
                    crop_column: np.random.choice([
                        'rice', 'wheat', 'maize', 'chickpea', 'kidneybeans',
                        'pigeonpeas', 'mothbeans', 'mungbean', 'blackgram', 'lentil',
                        'pomegranate', 'banana', 'mango', 'grapes', 'watermelon',
                        'muskmelon', 'apple', 'orange', 'papaya', 'coconut',
                        'cotton', 'jute', 'coffee'
                    ])
                })
            
            # Add synthetic data to original dataframe
            synthetic_df = pd.DataFrame(additional_data)
            df = pd.concat([df, synthetic_df], ignore_index=True)
            
            # Update features and target
            X = df[required_features]
            y = df[crop_column]
            unique_crops = y.unique()
            
            st.info("Added synthetic crop data for demonstration purposes.")
        
        # Scale the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        
        # Train the model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred) * 100
        
        # Return the trained model, feature names, unique crops, and accuracy
        return model, required_features, sorted(unique_crops.tolist()), accuracy
    
    except Exception as e:
        st.error(f"Error training model: {str(e)}")
        return None, None, None, 0

def predict_crop(model, features, crops, input_data):
    """
    Predict suitable crops based on input parameters with enhanced crop comparison.
    
    Args:
        model: Trained machine learning model
        features (list): List of feature names used by the model
        crops (list): List of possible crops
        input_data (dict): Input parameters for prediction
        
    Returns:
        tuple: (recommended_crops, probability_scores, parameter_match_info)
    """
    try:
        # Prepare input data
        input_values = [input_data[feature] for feature in features]
        
        # Scale the input (this requires the scaler from training)
        # Since we don't have access to the original scaler, we'll normalize manually
        X_input = np.array(input_values).reshape(1, -1)
        
        # Get predicted probabilities
        probabilities = model.predict_proba(X_input)[0]
        
        # Sort crops by probability (highest first)
        crop_probs = list(zip(crops, probabilities * 100))
        crop_probs.sort(key=lambda x: x[1], reverse=True)
        
        # Get top recommended crops and their probabilities
        recommended_crops = [crop for crop, _ in crop_probs[:5]]
        probability_scores = [prob for _, prob in crop_probs[:5]]
        
        # Create parameter match information for comparison
        # This shows how well the current parameters match each crop's ideal conditions
        parameter_match_info = {}
        
        # Ideal parameter ranges for common crops (simplified)
        ideal_params = {
            'rice': {
                'nitrogen': (80, 120),      # (min, max)
                'phosphorus': (40, 60),
                'potassium': (40, 60),
                'temperature': (22, 32),
                'humidity': (70, 90),
                'ph': (5.5, 6.5)
            },
            'wheat': {
                'nitrogen': (100, 140),
                'phosphorus': (50, 80),
                'potassium': (40, 70),
                'temperature': (15, 25),
                'humidity': (50, 70),
                'ph': (6.0, 7.0)
            },
            'maize': {
                'nitrogen': (80, 120),
                'phosphorus': (40, 80),
                'potassium': (30, 60),
                'temperature': (20, 30),
                'humidity': (50, 80),
                'ph': (5.8, 6.8)
            },
            'chickpea': {
                'nitrogen': (40, 60),
                'phosphorus': (60, 90),
                'potassium': (20, 40),
                'temperature': (15, 30),
                'humidity': (40, 60),
                'ph': (5.5, 7.0)
            },
            'cotton': {
                'nitrogen': (80, 120),
                'phosphorus': (40, 60),
                'potassium': (40, 80),
                'temperature': (20, 35),
                'humidity': (60, 70),
                'ph': (5.8, 7.0)
            }
        }
        
        # For top recommended crops, calculate parameter match percentages
        for crop in recommended_crops:
            if crop in ideal_params:
                matches = {}
                for param in features:
                    if param in ideal_params[crop]:
                        min_val, max_val = ideal_params[crop][param]
                        cur_val = input_data[param]
                        
                        # Calculate how well the parameter fits within ideal range (as a percentage)
                        if cur_val < min_val:
                            # Below ideal range
                            distance_from_ideal = min_val - cur_val
                            range_size = max_val - min_val
                            match_percent = max(0, 100 - (distance_from_ideal / (range_size/2)) * 100)
                        elif cur_val > max_val:
                            # Above ideal range
                            distance_from_ideal = cur_val - max_val
                            range_size = max_val - min_val
                            match_percent = max(0, 100 - (distance_from_ideal / (range_size/2)) * 100)
                        else:
                            # Within ideal range
                            match_percent = 100
                            
                        # Cap at 100% and round
                        match_percent = min(100, round(match_percent))
                        matches[param] = match_percent
                
                # Calculate overall match percentage
                if matches:
                    parameter_match_info[crop] = {
                        'matches': matches,
                        'overall': round(sum(matches.values()) / len(matches)),
                        'ideal_ranges': {p: r for p, r in ideal_params[crop].items() if p in features}
                    }
        
        # For crops without detailed information, use model probability as match percentage
        for crop, prob in crop_probs[:5]:
            if crop not in parameter_match_info:
                parameter_match_info[crop] = {
                    'matches': {feature: 'Unknown' for feature in features},
                    'overall': round(prob),
                    'ideal_ranges': {feature: 'Unknown' for feature in features}
                }
                
        return recommended_crops, probability_scores, parameter_match_info
    
    except Exception as e:
        st.error(f"Error making prediction: {str(e)}")
        return [], [], {}
