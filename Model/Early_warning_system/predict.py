import requests
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import joblib
from datetime import datetime, timedelta
import pytz # Import pytz for timezone-aware datetimes

# --- Step 1: Define the Model Architecture ---
# This MUST be the exact same architecture as the one you trained.
class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=100, output_size=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        self.lstm = nn.LSTM(input_size, hidden_layer_size, batch_first=True)
        self.linear = nn.Linear(hidden_layer_size, output_size)

    def forward(self, input_seq):
        lstm_out, _ = self.lstm(input_seq)
        last_time_step_output = lstm_out[:, -1, :]
        predictions = self.linear(last_time_step_output)
        return predictions

# --- Step 2: Function to Fetch and Prepare the Latest Data ---
def get_latest_data(station_id, scaler):
    """Fetches the last 24 hours of data and prepares it for the model."""
    print("Fetching latest 24 hours of data...")

    # Calculate date range for the last 24 hours using timezone-aware datetimes
    # Adjusting date range to fetch data from a few days ago
    end_date = datetime.now(pytz.utc) - timedelta(days=1) # Fetch data up to yesterday
    start_date = end_date - timedelta(days=3) # Get data from 3 days ago

    # Format dates for the API
    # The API expects dates in YYYYMMDD format for begin_date and end_date
    # and will use the time_zone parameter for filtering within the day
    begin_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')

    API_URL = (
        f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
        f"begin_date={begin_date_str}&end_date={end_date_str}"
        f"&station={station_id}"
        f"&product=hourly_height&datum=MLLW&units=metric&time_zone=gmt"
        f"&application=my_prediction_app&format=json"
    )

    print(f"Attempting to fetch data from URL: {API_URL}")
    print(f"Using date range: {begin_date_str} to {end_date_str}")


    response = requests.get(API_URL)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from NOAA API. Status code: {response.status_code}")

    json_data = response.json()
    # Check if 'data' is present and not empty
    if 'data' not in json_data or not json_data['data']:
        raise Exception("No data in API response. The station may be offline or there's no data for the requested period.")

    df = pd.DataFrame(json_data['data'])

    # --- Data Cleaning ---
    df.rename(columns={'t': 'timestamp', 'v': 'water_level'}, inplace=True)
    df['water_level'] = pd.to_numeric(df['water_level'], errors='coerce')
    df.dropna(inplace=True)

    # We only need the last 24 data points (hours)
    if len(df) < 24:
        raise Exception(f"Not enough data fetched to make a prediction (need 24 hours). Only got {len(df)} data points.")

    # Sort by timestamp just in case the API doesn't guarantee order
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')

    latest_data = df.tail(24)

    # --- Normalization ---
    # Use the LOADED scaler to transform the new data
    normalized_data = scaler.transform(latest_data[['water_level']])

    # Convert to a PyTorch tensor
    sequence_tensor = torch.tensor(normalized_data, dtype=torch.float32).view(1, 24, 1)

    return sequence_tensor

# --- Step 3: Main Prediction Function ---
def predict_next_hour():
    STATION_ID = "8518750" # The Battery, NY
    DANGER_THRESHOLD = 2.5 # meters - SET YOUR OWN THRESHOLD

    # Load the scaler
    try:
        scaler = joblib.load('scaler.joblib')
    except FileNotFoundError:
        print("Error: scaler.joblib not found. Please run train.py first.")
        return

    # Load the trained model
    model = LSTMModel()
    try:
        model_path = 'water_level_predictor.pth'
        model.load_state_dict(torch.load(model_path))
        model.eval() # Set model to evaluation mode
        print("Trained model loaded successfully.")
    except FileNotFoundError:
        print(f"Error: {model_path} not found. Please run train.py first.")
        return

    # Get the latest data sequence
    try:
        input_sequence = get_latest_data(STATION_ID, scaler)
    except Exception as e:
        print(f"Error preparing data: {e}")
        return

    # --- Make the Prediction ---
    with torch.no_grad():
        normalized_prediction = model(input_sequence)

    # --- Inverse Transform to get the real value ---
    # The prediction is a tensor, so we extract its value with .item()
    # and reshape it for the scaler
    predicted_value_scaled = np.array([[normalized_prediction.item()]])
    real_world_prediction = scaler.inverse_transform(predicted_value_scaled)

    # The output is a 2D array, so we get the single value from it
    final_prediction = real_world_prediction[0][0]

    print("\n--- FORECAST ---")
    print(f"Predicted water level for the next hour: {final_prediction:.2f} meters")

    # --- Alerting Logic ---
    if final_prediction > DANGER_THRESHOLD:
        print(f"🚨 ALERT! Predicted level exceeds the danger threshold of {DANGER_THRESHOLD}m.")
    else:
        print("✅ Levels are within the normal range.")

# --- Run the prediction ---
if __name__ == '__main__':
    predict_next_hour()