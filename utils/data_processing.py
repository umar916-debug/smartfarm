import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def process_historical_data(df):
    """
    Process historical data for analysis, including cleaning and formatting.
    
    Args:
        df (pandas.DataFrame): Raw data from Google Sheets
        
    Returns:
        pandas.DataFrame: Processed data ready for analysis
    """
    try:
        # Make a copy to avoid modifying the original dataframe
        processed_df = df.copy()
        
        # Handle timestamp column if present
        if 'timestamp' in processed_df.columns:
            # Convert to datetime
            processed_df['timestamp'] = pd.to_datetime(processed_df['timestamp'], errors='coerce')
            
            # Drop rows with invalid timestamps
            processed_df = processed_df.dropna(subset=['timestamp'])
            
            # Sort by timestamp
            processed_df = processed_df.sort_values('timestamp')
        
        # Convert numeric columns to appropriate types
        for column in processed_df.columns:
            # Skip timestamp column
            if column == 'timestamp':
                continue
                
            # Try to convert to numeric
            processed_df[column] = pd.to_numeric(processed_df[column], errors='coerce')
        
        # Handle missing values in numeric columns
        numeric_cols = processed_df.select_dtypes(include=['float64', 'int64']).columns
        
        # For each numeric column, fill missing values with the median
        for col in numeric_cols:
            median_value = processed_df[col].median()
            processed_df[col] = processed_df[col].fillna(median_value)
        
        # Remove duplicates if any
        processed_df = processed_df.drop_duplicates()
        
        # Reset index
        processed_df = processed_df.reset_index(drop=True)
        
        return processed_df
    
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return df  # Return original dataframe in case of error
