import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text
import pandas as pd

# Function to connect to the database
def connect_to_database(db_path):
    try:
        engine = create_engine(db_path)
        return engine.connect()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to fetch restaurant data from the database
def fetch_restaurant_data(con, query):
    try:
        results = con.execute(text(query)).fetchall()
        return results
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

# Function to create a dataframe from the results
def create_dataframe(results, columns, source):
    df = pd.DataFrame(results, columns=columns)
    df['source'] = source
    return df

# Function to check coordinates are within Belgium's boundaries
def check_coordinates(df):
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    df = df[(df['latitude'] != 0.0) & (df['longitude'] != 0.0)]
    valid_latitude = (df['latitude'] >= 50.5) & (df['latitude'] <= 51.7)
    valid_longitude = (df['longitude'] >= 2.5) & (df['longitude'] <= 6)
    valid_data = valid_latitude & valid_longitude

    if not valid_data.all():
        print(f"Invalid coordinates found:\n{df[~valid_data]}")

    return df[valid_data]

# Function to plot the individual and combined scatter plots
# Function to plot the individual and combined scatter plots
def plot_individual_and_combined_restaurants(df_deliveroo, df_ubereats, df_takeaway):
    # Load the Belgium region shapefile
    region = gpd.read_file('map/régions_08.shp')

    # Ensure that both the shapefile and the data are in the same CRS
    region = region.to_crs(epsg=4326)  # Reproject to EPSG:4326 (WGS84)

    # Set up the 2x2 grid of plots
    fig, axs = plt.subplots(2, 2, figsize=(14, 12))

    data = [(df_deliveroo, 'blue', 'Deliveroo Restaurants'),
            (df_ubereats, 'red', 'UberEats Restaurants'),
            (df_takeaway, 'green', 'Takeaway Restaurants')]

    for i, (df, color, title) in enumerate(data):
        ax = axs[i // 2, i % 2]
        
        df_valid = check_coordinates(df)
        
        # Plot the map of Belgium
        region.plot(ax=ax, color='lightgray', edgecolor='black')
        
        # If the data is Takeaway, apply alpha transparency
        alpha_value = 0.5 if title == 'Takeaway Restaurants' else 1  # Make Takeaway restaurants more transparent

        sns.scatterplot(x='longitude', y='latitude', data=df_valid, color=color, s=20, ax=ax, alpha=alpha_value)
        
        # Set map limits to focus on Belgium
        ax.set_xlim(2.5, 6)
        ax.set_ylim(50.5, 51.7)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title(title)
        ax.grid(True)

    combined_df = pd.concat([df_deliveroo, df_ubereats, df_takeaway], ignore_index=True)
    ax_combined = axs[1, 1]
    
    combined_df_valid = check_coordinates(combined_df)
    
    # Plot the map of Belgium
    region.plot(ax=ax_combined, color='lightgray', edgecolor='black')
    
    # Plot the combined data with hue for source (Deliveroo, UberEats, Takeaway)
    sns.scatterplot(x='longitude', y='latitude', data=combined_df_valid, hue='source', palette='Set1', s=20, ax=ax_combined)
    
    # Set map limits to focus on Belgium
    ax_combined.set_xlim(2.5, 6)
    ax_combined.set_ylim(50.5, 51.7)
    ax_combined.set_xlabel('Longitude')
    ax_combined.set_ylabel('Latitude')
    ax_combined.set_title('Combined Restaurants from Deliveroo, UberEats, and Takeaway')
    ax_combined.grid(True)
    ax_combined.legend(title='Source')

    plt.tight_layout()
    plt.show()


# Main function to fetch data and plot the individual and combined restaurants
def main():
    # Deliveroo
    con = connect_to_database('sqlite:///databases/deliveroo.db')
    query = """SELECT latitude, longitude FROM restaurants"""
    results = fetch_restaurant_data(con, query)
    df_deliveroo = create_dataframe(results, ['latitude', 'longitude'], 'Deliveroo')
    con.close()

    # UberEats
    con = connect_to_database('sqlite:///databases/ubereats.db')
    query = """SELECT location__latitude, location__longitude FROM restaurants"""
    results = fetch_restaurant_data(con, query)
    df_ubereats = create_dataframe(results, ['latitude', 'longitude'], 'UberEats')
    con.close()

    # Takeaway
    con = connect_to_database('sqlite:///databases/takeaway.db')
    query = """SELECT latitude, longitude FROM restaurants"""
    results = fetch_restaurant_data(con, query)
    df_takeaway = create_dataframe(results, ['latitude', 'longitude'], 'Takeaway')
    con.close()

    # Plot individual and combined restaurants
    plot_individual_and_combined_restaurants(df_deliveroo, df_ubereats, df_takeaway)

if __name__ == "__main__":
    main()


