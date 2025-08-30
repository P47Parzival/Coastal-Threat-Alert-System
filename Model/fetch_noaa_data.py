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