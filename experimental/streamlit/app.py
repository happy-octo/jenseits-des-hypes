import streamlit as st
import time
import requests
import pandas as pd

# Backend API URL
backend_url = "http://localhost:8000/get-events/"

# Title of the app
st.title("Real-Time Event Viewer")

# Placeholder for real-time data visualization
placeholder = st.empty()


# Function to fetch events from the backend
def fetch_events():
    try:
        response = requests.get(backend_url)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching events: {e}")
        return []


# Main loop to update the UI
while True:
    # Fetch events from the backend
    events = fetch_events()

    # Convert events to a DataFrame for better visualization
    if events:
        df = pd.DataFrame(events)
    else:
        df = pd.DataFrame(columns=["id", "value"])

    # Update the placeholder with new data
    with placeholder.container():
        st.write("### Real-Time Events")
        st.table(df)

    # Wait before refreshing
    time.sleep(10)
