import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt

# Function to fetch and process data for each platform
def fetch_data(db_path, query, platform_name):
    engine = create_engine(f'sqlite:///{db_path}')
    with engine.connect() as con:
        stmt = text(query)
        result = con.execute(stmt)
        data = result.fetchall()

    df = pd.DataFrame(data)
    gdf = gpd.GeoDataFrame(df, 
                           geometry=gpd.points_from_xy(df['longitude'], df['latitude']),
                           crs="EPSG:4326")
    gdf['platform'] = platform_name  # Add a column for platform name
    return gdf

# Queries for each platform
queries = {
    'Takeaway': """
        SELECT r.primarySlug, cr.restaurant_id, cr.category_id, r.city, r.longitude, r.latitude
        FROM restaurants AS r 
        JOIN categories_restaurants AS cr ON r.primarySlug = cr.restaurant_id
        WHERE cr.category_id LIKE '%vegetarian%'
    """,
    'Deliveroo': """
        SELECT latitude, longitude, category
        FROM restaurants
        WHERE category LIKE '%Veg%'
    """,
    'UberEats': """
        SELECT r.location__latitude AS latitude, r.location__longitude AS longitude, rc.category
        FROM restaurants AS r
        JOIN restaurant_to_categories AS rc ON r.id = rc.restaurant_id
        WHERE rc.category LIKE '%Veg%'
    """
}

# Load the Belgium region shapefile
region = gpd.read_file('map/régions_08.shp')
region = region.to_crs(epsg=4326)  # Reproject to EPSG:4326 (WGS84)

# Fetch and combine the data from all platforms
all_restaurants = pd.concat([
    fetch_data('databases/takeaway.db', queries['Takeaway'], 'Takeaway'),
    fetch_data('databases/deliveroo.db', queries['Deliveroo'], 'Deliveroo'),
    fetch_data('databases/ubereats.db', queries['UberEats'], 'UberEats')
])

# Create a 2x2 grid of subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# List of platforms and their colors for individual subplots
platforms = ['Takeaway', 'Deliveroo', 'UberEats']
colors = {'Takeaway': 'green', 'Deliveroo': 'blue', 'UberEats': 'red'}

# Plot individual maps
for i, platform in enumerate(platforms):
    ax = axes[i // 2, i % 2]  # Get the correct subplot axis
    region.plot(ax=ax, color='lightgrey', edgecolor='black')  # Plot regions
    gdf_platform = all_restaurants[all_restaurants['platform'] == platform]
    alpha_value = 0.5 if platform == 'UberEats' else 1  # Adjust alpha for UberEats
    gdf_platform.plot(ax=ax, markersize=10, color=colors[platform], alpha=alpha_value, label=f'{platform} Restaurants')
    ax.set_title(f'{platform} Vegetarian Restaurants')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend()

# Plot combined map in the last subplot (bottom-right)
ax_combined = axes[1, 1]  # Bottom-right subplot
region.plot(ax=ax_combined, color='lightgrey', edgecolor='black')  # Plot regions
for platform in platforms:
    gdf_platform = all_restaurants[all_restaurants['platform'] == platform]
    gdf_platform.plot(ax=ax_combined, markersize=10, color=colors[platform], alpha=alpha_value, label=f'{platform} Restaurants')
ax_combined.set_title('Combined Vegetarian Restaurants')
ax_combined.set_xlabel('Longitude')
ax_combined.set_ylabel('Latitude')
ax_combined.legend()

# Adjust layout to avoid overlap
plt.tight_layout()
plt.show()
