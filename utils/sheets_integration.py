import os
import json
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Cache the credentials to avoid repeated authentications
@st.cache_resource(show_spinner=False)
def authenticate_google_sheets(_credentials_json=None):
    """
    Authenticate with Google Sheets API using service account credentials.
    
    Args:
        _credentials_json (str, optional): JSON credentials string
    
    Returns:
        Google Sheets API service object
    """
    try:
        # Check if credentials are passed in the session state
        if _credentials_json is not None:
            try:
                # Parse the JSON credentials
                creds_info = json.loads(_credentials_json)
                
                # Create credentials from parsed JSON
                credentials = service_account.Credentials.from_service_account_info(
                    creds_info,
                    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                )
                
                # Build the service
                service = build('sheets', 'v4', credentials=credentials)
                return service
            except json.JSONDecodeError:
                st.error("Invalid JSON credentials format. Please check your JSON and try again.")
                return None
            except Exception as e:
                st.error(f"Error with provided credentials: {str(e)}")
                return None
        
        # If no credentials passed, try to use stored credentials
        creds_info = st.secrets.get("gcp_service_account", None)
        
        # If stored credentials exist, use them
        if creds_info is not None:
            credentials = service_account.Credentials.from_service_account_info(
                creds_info,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            service = build('sheets', 'v4', credentials=credentials)
            return service
        
        # If no stored credentials, check environment variables
        try:
            credentials = service_account.Credentials.from_service_account_info(
                {
                    "type": "service_account",
                    "project_id": os.getenv("GCP_PROJECT_ID", ""),
                    "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID", ""),
                    "private_key": os.getenv("GCP_PRIVATE_KEY", "").replace("\\n", "\n"),
                    "client_email": os.getenv("GCP_CLIENT_EMAIL", ""),
                    "client_id": os.getenv("GCP_CLIENT_ID", ""),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv("GCP_CLIENT_X509_CERT_URL", ""),
                    "universe_domain": "googleapis.com"
                },
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            service = build('sheets', 'v4', credentials=credentials)
            return service
        except Exception:
            # If we reach here, no valid credentials exist
            st.warning("No valid Google credentials found. Please provide JSON credentials.")
            return None
    
    except Exception as e:
        st.error(f"Authentication Error: {str(e)}")
        return None

# Cache the sheet data to avoid repeated API calls for the same sheet
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_sheet_data(spreadsheet_id, sheet_name, credentials_json=None):
    """
    Get data from a Google Sheet.
    
    Args:
        spreadsheet_id (str): ID of the Google Spreadsheet
        sheet_name (str): Name of the sheet tab
        credentials_json (str, optional): JSON credentials string
        
    Returns:
        pandas.DataFrame: DataFrame containing the sheet data
    """
    try:
        # Authenticate and get service
        service = authenticate_google_sheets(credentials_json)
        if service is None:
            return None
        
        # Call the Sheets API to get the data
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_name
        ).execute()
        
        # Get the values from the result
        values = result.get('values', [])
        
        if not values:
            st.warning('No data found in the sheet.')
            return None
        
        # Convert to pandas DataFrame
        # First row is assumed to be headers
        headers = values[0]
        
        # If there's only headers, return empty DataFrame with those columns
        if len(values) == 1:
            return pd.DataFrame(columns=headers)
        
        # Create DataFrame from remaining rows
        data = values[1:]
        
        # Handle cases where some rows might have fewer columns than headers
        # Fill missing values with None
        data_fixed = []
        for row in data:
            if len(row) < len(headers):
                # Pad the row with None values
                row = row + [None] * (len(headers) - len(row))
            data_fixed.append(row)
        
        # Create the DataFrame
        df = pd.DataFrame(data_fixed, columns=headers)
        
        # Map column names to standardized names if needed
        column_mapping = {
            'N': 'nitrogen',
            'P': 'phosphorus', 
            'K': 'potassium',
            'Temperature': 'temperature',
            'Humidity': 'humidity',
            'pH': 'ph'
        }
        
        # Rename columns if they match our mapping
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Convert numeric columns to appropriate types
        for column in df.columns:
            # Skip timestamp column for numeric conversion
            if column.lower() == 'timestamp':
                continue
                
            # Try to convert to numeric, if fails, keep as is
            try:
                df[column] = pd.to_numeric(df[column])
            except (ValueError, TypeError):
                # Keep as is if conversion fails
                pass
        
        return df
    
    except HttpError as error:
        st.error(f"Google Sheets API Error: {error}")
        return None
    except Exception as e:
        st.error(f"Error fetching sheet data: {str(e)}")
        return None
