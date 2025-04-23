import streamlit as st
import pandas as pd
from utils.sheets_integration import get_sheet_data

st.set_page_config(page_title="DEBUG | NPK Checker", layout="wide")
st.title("🧪 DEBUG: N, P, K Checker")

if not all(k in st.session_state for k in ("spreadsheet_id", "sheet_name", "credentials_json")):
    st.error("Google Sheets not configured.")
    st.stop()

try:
    df = get_sheet_data(
        st.session_state["spreadsheet_id"],
        st.session_state["sheet_name"],
        st.session_state["credentials_json"]
    )

    if df is not None and not df.empty:
        st.success("✅ Sheet loaded")

        # Show column names
        st.subheader("📋 Columns in DataFrame")
        st.write(df.columns.tolist())

        # Show the latest row
        latest_row = df.iloc[-1]
        st.subheader("🧾 Latest Row")
        st.write(latest_row)

        # Show dict for direct access test
        latest_data = latest_row.to_dict()
        st.subheader("🔍 Latest Row as Dictionary")
        st.json(latest_data)

        # Try to access NPK specifically
        st.subheader("🧪 Manual NPK Access Test")
        st.write("N =", latest_data.get("N", "❌ Missing"))
        st.write("P =", latest_data.get("P", "❌ Missing"))
        st.write("K =", latest_data.get("K", "❌ Missing"))

    else:
        st.error("DataFrame is empty.")

except Exception as e:
    st.error(f"Error: {e}")
