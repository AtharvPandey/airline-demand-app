import requests
import pandas as pd

API_KEY = '3868f8c227724cf3368e583cbfe0e543'
url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&limit=100"

response = requests.get(url)
data = response.json()

flights = data['data']
flight_list = []

for flight in flights:
    try:
        airline = flight['airline']['name']
        departure = flight['departure']['airport']
        arrival = flight['arrival']['airport']
        route = f"{departure} → {arrival}"
        status = flight['flight_status']
        flight_list.append([airline, route, status])
    except:
        continue

# Create DataFrame
df = pd.DataFrame(flight_list, columns=["Airline", "Route", "Status"])

# Show top 5 records
print("\n🛫 Sample Data:")
print(df.head())

# Most frequent routes
popular_routes = df['Route'].value_counts().head(5)
print("\n🔥 Top 5 Popular Routes:")
print(popular_routes)

# Most common airlines
popular_airlines = df['Airline'].value_counts().head(5)
print("\n✈️ Top 5 Airlines by Frequency:")
print(popular_airlines)

# Flight status counts
status_count = df['Status'].value_counts()
print("\n📊 Flight Status Summary:")
print(status_count)
