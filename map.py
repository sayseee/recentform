import pandas as pd
import folium

# Read the CSV file
df = pd.read_csv('coordinates.csv')

# Create a base map
map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
m = folium.Map(location=map_center, zoom_start=14)

# Add markers to the map
for idx, row in df.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"{row['Name']}, {row['Address']}",
        tooltip=row['Name']
    ).add_to(m)

# Save the map to an HTML file
m.save('map.html')