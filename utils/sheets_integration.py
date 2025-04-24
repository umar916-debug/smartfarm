import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

def validate_credentials(credentials_path):
    """Validate the credentials file by attempting to authorize with Google"""
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        client = gspread.authorize(credentials)
        return True
    except Exception as e:
        st.error(f"Error validating credentials: {str(e)}")
        return False

def get_sheet_data(credentials_path, spreadsheet_id, sheet_name):
    """
    Fetch data from Google Sheets and return as a pandas DataFrame
    
    Parameters:
    credentials_path (str): Path to the credentials.json file
    spreadsheet_id (str): ID of the Google Spreadsheet
    sheet_name (str): Name of the sheet to fetch
    
    Returns:
    DataFrame or None: Pandas DataFrame containing sheet data or None if error
    """
    try:
        # Set up the credentials
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        client = gspread.authorize(credentials)
        
        # Open the spreadsheet and worksheet
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        
        # Get all values from the worksheet
        data = worksheet.get_all_records()
        
        # Check if data is empty
        if not data:
            st.error("No data found in the specified sheet.")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Check for required columns
        required_columns = [
            'timestamp', 'temperature', 'humidity', 'soil_moisture', 
            'light_intensity', 'pH', 'nitrogen', 'phosphorus', 'potassium'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.warning(f"Missing columns in sheet: {', '.join(missing_columns)}")
            
            # Add missing columns with empty values
            for col in missing_columns:
                df[col] = None
        
        # Return the DataFrame
        return df
    
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Spreadsheet with ID '{spreadsheet_id}' not found. Please check the Spreadsheet ID.")
        return None
    
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Sheet '{sheet_name}' not found in the spreadsheet. Please check the Sheet Name.")
        return None
    
    except gspread.exceptions.APIError as e:
        st.error(f"Google Sheets API error: {str(e)}")
        return None
    
    except Exception as e:
        st.error(f"Error fetching data from Google Sheets: {str(e)}")
        return None
