import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime, timedelta

# Function to load data from Google Sheets
@st.cache_data(ttl=60)
def load_data():
    # Replace this with your published CSV URL from Google Sheets
    sheet_url = "https://docs.google.com/spreadsheets/d/e/your_google_sheet_id/pub?gid=0&single=true&output=csv"
    df = pd.read_csv(sheet_url)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

def live_data_monitoring():
    st.subheader("🌿 Live Data Monitoring")

    sensor_to_plot = st.selectbox("Select Sensor", ["Temperature", "Humidity", "SoilMoisture", "Light"])
    chart = st.empty()

    while True:
        df = load_data()
        latest_data = df.tail(50)  # last 50 data points

        fig = px.line(
            latest_data,
            x="Timestamp",
            y=sensor_to_plot,
            title=f"Live {sensor_to_plot} Data",
            markers=True
        )
        fig.update_layout(xaxis_title="Time", yaxis_title=sensor_to_plot)

        chart.plotly_chart(fig, use_container_width=True)

        time.sleep(10)
        st.experimental_rerun()

def historical_data():
    st.subheader("📊 Historical Data")

    df = load_data()

    # Filters
    with st.sidebar:
        st.markdown("## Filters")
        min_date, max_date = df["Timestamp"].min(), df["Timestamp"].max()
        start_date = st.date_input("Start date", min_value=min_date.date(), max_value=max_date.date(), value=min_date.date())
        end_date = st.date_input("End date", min_value=min_date.date(), max_value=max_date.date(), value=max_date.date())

        sensor_options = ["Temperature", "Humidity", "SoilMoisture", "Light"]
        selected_sensors = st.multiselect("Select sensors", sensor_options, default=sensor_options)

    # Filter data
    mask = (df["Timestamp"].dt.date >= start_date) & (df["Timestamp"].dt.date <= end_date)
    filtered_data = df.loc[mask, ["Timestamp"] + selected_sensors]

    # Display raw data
    st.write("### Raw Data")
    st.dataframe(filtered_data)

    # Export to CSV
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "historical_data.csv", "text/csv")

    # Plotting
    if selected_sensors:
        st.write("### Sensor Trends")
        fig = px.line(
            filtered_data,
            x="Timestamp",
            y=selected_sensors,
            title="Sensor Trends Over Time"
        )
        fig.update_layout(xaxis_title="Time", yaxis_title="Sensor Reading")
        st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(page_title="Smart Farming Dashboard", layout="wide")
    st.title("🌱 Smart Farming Dashboard")

    page = st.sidebar.radio("Select Page", ["Live Data Monitoring", "Historical Data"])

    if page == "Live Data Monitoring":
        live_data_monitoring()
    elif page == "Historical Data":
        historical_data()

if __name__ == "__main__":
    main()
