import requests
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# --- Step 1: Define API Parameters to Fetch Data ---

# We'll fetch data from a well-known station: The Battery, New York (ID: 8518750)
# You can find other station IDs here: https://tidesandcurrents.noaa.gov/stations.html
STATION_ID = "8518750" 

# Let's get data for the last 3 months. The API needs dates in YYYYMMDD format.
# NOTE: The NOAA API is most reliable for recent historical data.
END_DATE = "20250830" # Today's date
START_DATE = "20250601" # Roughly 3 months ago

# We are requesting hourly water level data.
# 'product' specifies the type of data we want.
# 'datum' is the reference point for sea level. 'MLLW' is a standard.
# 'units' are in meters ('metric').
# 'time_zone' is GMT to avoid daylight saving issues.
# 'format' is JSON, which is easy to work with in Python.
API_URL = (
    f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
    f"begin_date={START_DATE}&end_date={END_DATE}"
    f"&station={STATION_ID}"
    f"&product=hourly_height"
    f"&datum=MLLW"
    f"&units=metric"
    f"&time_zone=gmt"
    f"&application=my_awesome_app" # It's good practice to name your app
    f"&format=json"
)

# --- Step 2: Make the API Request and Load into Pandas ---

print(f"Fetching data for station {STATION_ID}...")
response = requests.get(API_URL)
data = None

# Check if the request was successful
if response.status_code == 200:
    print("Data fetched successfully!")
    json_data = response.json()
    
    # Create a pandas DataFrame, which is like a spreadsheet for Python
    df = pd.DataFrame(json_data['data'])
    print("Initial data preview:")
    print(df.head())
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
    print("Error:", response.text)
    exit()

# --- Step 3: Prepare the Data for a Machine Learning Model ---

print("\n--- Preparing Data for ML Model ---")

# 1. Rename columns for clarity. 't' is timestamp, 'v' is value (water level).
df.rename(columns={'t': 'timestamp', 'v': 'water_level'}, inplace=True)

# 2. Convert timestamp string to a proper datetime object.
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 3. Set the timestamp as the index of our DataFrame. This is standard for time-series data.
df.set_index('timestamp', inplace=True)

# 4. Convert water_level to a numeric type. If any values can't be converted,
#    they will be replaced with NaN (Not a Number).
df['water_level'] = pd.to_numeric(df['water_level'], errors='coerce')

# 5. Handle missing data. A simple way is to interpolate (fill in gaps logically).
df.interpolate(method='time', inplace=True)
df.dropna(inplace=True) # Drop any remaining NaN values

print("\nCleaned and processed data preview:")
print(df.head())

# 6. Normalize the data. ML models work best when input values are scaled small,
#    typically between 0 and 1. We use MinMaxScaler for this.
scaler = MinMaxScaler()
df['water_level_normalized'] = scaler.fit_transform(df[['water_level']])

print("\nData with normalized values:")
print(df.head())


# --- Step 4: Visualize the Data ---

print("\nGenerating plot...")
plt.figure(figsize=(15, 6))
plt.title(f'Water Level at Station {STATION_ID}')
plt.xlabel('Date')
plt.ylabel('Water Level (meters)')
plt.plot(df.index, df['water_level'], label='Original Water Level')
plt.legend()
plt.grid(True)
plt.show()

print("\nScript finished. Your data is now cleaned and normalized, ready for a model!")

import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# --- Steps 1-4: Fetch and Prepare Data ---

def fetch_and_prepare_data():
    """Fetches and prepares NOAA data, returning a cleaned DataFrame and scaler."""
    STATION_ID = "8518750"
    # Using a longer date range for more training data
    END_DATE = "20250830"
    START_DATE = "20250101" 
    API_URL = (
        f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
        f"begin_date={START_DATE}&end_date={END_DATE}&station={STATION_ID}"
        f"&product=hourly_height&datum=MLLW&units=metric&time_zone=gmt"
        f"&application=my_awesome_app&format=json"
    )
    
    print("Fetching and preparing data...")
    response = requests.get(API_URL)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from NOAA API. Status: {response.status_code}")
        
    json_data = response.json()
    # Handle potential API errors gracefully
    if 'data' not in json_data:
        print("Error: 'data' key not found in API response.")
        print(json_data)
        exit()

    df = pd.DataFrame(json_data['data'])
    
    df.rename(columns={'t': 'timestamp', 'v': 'water_level'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df['water_level'] = pd.to_numeric(df['water_level'], errors='coerce')
    df.interpolate(method='time', inplace=True)
    df.dropna(inplace=True)
    
    # The scaler is used to normalize data to a 0-1 range and to inverse the transformation later
    scaler = MinMaxScaler(feature_range=(-1, 1))
    df['water_level_normalized'] = scaler.fit_transform(df[['water_level']])
    
    print("Data ready.")
    return df, scaler

# --- Step 5: Create Sequences for the LSTM Model ---

def create_sequences(data, sequence_length):
    """Creates input sequences (X) and their corresponding targets (y)."""
    sequences = []
    labels = []
    for i in range(len(data) - sequence_length):
        seq = data[i:i+sequence_length]
        label = data[i+sequence_length]
        sequences.append(seq)
        labels.append(label)
        
    return torch.tensor(np.array(sequences), dtype=torch.float32), torch.tensor(np.array(labels), dtype=torch.float32)

# --- Step 6: Define the PyTorch LSTM Model Architecture ---

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=100, output_size=1):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size
        self.lstm = nn.LSTM(input_size, hidden_layer_size, batch_first=True)
        self.linear = nn.Linear(hidden_layer_size, output_size)

    def forward(self, input_seq):
        # The input_seq shape is (batch_size, sequence_length, input_size)
        lstm_out, _ = self.lstm(input_seq)
        # We only want the output from the last time step
        last_time_step_output = lstm_out[:, -1, :]
        predictions = self.linear(last_time_step_output)
        return predictions

# --- Step 7: Split Data into Training and Testing sets ---

def split_data(X, y, test_size=0.2):
    """Splits the data into training and testing sets."""
    test_data_size = int(len(X) * test_size)
    
    X_train, X_test = X[:-test_data_size], X[-test_data_size:]
    y_train, y_test = y[:-test_data_size], y[-test_data_size:]
    
    return X_train, X_test, y_train, y_test

# --- Step 8: Train the Model ---

if __name__ == '__main__':
    df, scaler = fetch_and_prepare_data()
    
    SEQUENCE_LENGTH = 24 # Use 24 hours of data to predict the next hour
    
    data_normalized = df['water_level_normalized'].values
    
    X, y = create_sequences(data_normalized, SEQUENCE_LENGTH)
    
    # Reshape y to be (num_samples, 1) for the loss function
    y = y.view(-1, 1) 
    
    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2)
    
    # Reshape X for the LSTM layer: (batch_size, sequence_length, num_features)
    X_train = X_train.view(-1, SEQUENCE_LENGTH, 1)
    X_test = X_test.view(-1, SEQUENCE_LENGTH, 1)

    print(f"Training data shape: {X_train.shape}")
    print(f"Testing data shape: {X_test.shape}")

    # --- Model, Loss, and Optimizer Initialization ---
    model = LSTMModel()
    loss_function = nn.MSELoss() # Mean Squared Error is good for regression
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # --- The Training Loop ---
    epochs = 10 # An epoch is one full pass through the training data
    
    print("\nStarting training...")
    for i in range(epochs):
        model.train() # Set the model to training mode
        for seq, labels in zip(X_train, y_train):
            optimizer.zero_grad() # Reset gradients
            
            # Reshape seq for the model
            seq = seq.view(1, SEQUENCE_LENGTH, 1)
            
            y_pred = model(seq)
            
            single_loss = loss_function(y_pred, labels.view(1,1))
            single_loss.backward() # Backpropagation
            optimizer.step() # Update weights

        if (i+1) % 1 == 0:
            print(f'Epoch {i+1}/{epochs} Loss: {single_loss.item():.4f}')

    print("Training finished.")

    # --- Step 9: Evaluate the Model on Test Data ---
    model.eval() # Set the model to evaluation mode
    test_predictions = []

    with torch.no_grad(): # We don't need to calculate gradients for evaluation
        for seq in X_test:
            seq = seq.view(1, SEQUENCE_LENGTH, 1)
            test_predictions.append(model(seq).item())

    # Inverse transform the predictions and actual values to the original scale
    actual_predictions = scaler.inverse_transform(np.array(test_predictions).reshape(-1, 1))
    actual_test_values = scaler.inverse_transform(y_test.numpy())

    # --- Step 10: Visualize the Results ---
    plt.figure(figsize=(15, 6))
    plt.title('Actual vs. Predicted Water Levels')
    plt.xlabel('Time Step')
    plt.ylabel('Water Level (meters)')
    plt.plot(actual_test_values, label='Actual Values', color='blue')
    plt.plot(actual_predictions, label='Predicted Values', color='red', linestyle='--')
    plt.legend()
    plt.grid(True)
    plt.show()

# (This goes at the end of your train.py script)

# --- Step 11: Save the Model and Scaler for Future Use ---
import joblib

# Save the trained model's state dictionary
torch.save(model.state_dict(), 'water_level_predictor.pth')

# Save the scaler object
joblib.dump(scaler, 'scaler.joblib')

print("\nModel and scaler have been saved to the 'models' directory.")