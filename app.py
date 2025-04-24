import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Smart Farming Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GOOGLE SHEETS CONFIGURATION ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

SERVICE_ACCOUNT_FILE = "creds.json"  # Your service account key file
SHEET_NAME = "Smart Farming Data"    # Your Google Sheet name

# --- AUTHENTICATE AND LOAD DATA ---
def load_data():
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(credentials)
        sheet = client.open(SHEET_NAME).sheet1
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        return df
    except Exception as e:
        st.error(f"❌ Failed to connect to Google Sheets: {e}")
        return None

# --- MAIN APP ---
def main():
    st.title("🌱 Smart Farming Dashboard")
    st.markdown("Monitor real-time data and summary statistics from your farm.")

    df = load_data()
    if df is not None:
        st.subheader("📊 Sensor Data")
        st.dataframe(df, use_container_width=True)

        if 'Temperature' in df.columns and 'Humidity' in df.columns:
            try:
                df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
                df['Humidity'] = pd.to_numeric(df['Humidity'], errors='coerce')
                avg_temp = df['Temperature'].mean()
                avg_humidity = df['Humidity'].mean()

                st.subheader("📈 Summary Statistics")
                st.metric("Average Temperature (°C)", f"{avg_temp:.2f}")
                st.metric("Average Humidity (%)", f"{avg_humidity:.2f}")
            except Exception as e:
                st.warning(f"⚠️ Error calculating averages: {e}")
        else:
            st.warning("⚠️ Required columns ('Temperature', 'Humidity') not found in the sheet.")

if __name__ == "__main__":
    main()
