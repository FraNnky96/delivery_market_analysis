from sqlalchemy import create_engine, Table, MetaData, text
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def connect_to_database(db_path):
    engine = create_engine(db_path)
    return engine.connect()

def fetch_restaurant_data(con, query):
    results = con.execute(text(query)).fetchall()
    return results

def create_dataframe(results, columns, source):
    df = pd.DataFrame(results, columns=columns)
    df['source'] = source
    return df

def plot_restaurants(df, color, title):
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x='longitude', y='latitude', data=df, color=color)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.ylim(50.50, 51.70)
    plt.xlim(2.5, 6)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    plt.close()

def main():
    
    # Deliveroo
    con = connect_to_database('sqlite:///databases/deliveroo.db')
    query = """SELECT latitude, longitude FROM restaurants"""
    results = fetch_restaurant_data(con, query)
    df_deliveroo = create_dataframe(results, ['latitude', 'longitude'], 'Deliveroo')
    plot_restaurants(df_deliveroo, 'blue', 'Deliveroo Restaurants')
    con.close()

    # UberEats
    con = connect_to_database('sqlite:///databases/ubereats.db')
    query = """SELECT location__latitude, location__longitude FROM restaurants"""
    results = fetch_restaurant_data(con, query)
    df_ubereats = create_dataframe(results, ['latitude', 'longitude'], 'UberEats')
    df_ubereats['longitude'] = df_ubereats['longitude'].astype(float)
    df_ubereats['latitude'] = df_ubereats['latitude'].astype(float)
    plot_restaurants(df_ubereats, 'red', 'UberEats Restaurants')
    con.close()

    # Takeaway
    con = connect_to_database('sqlite:///databases/takeaway.db')
    query = """SELECT latitude, longitude FROM restaurants"""
    results = fetch_restaurant_data(con, query)
    df_takeaway = create_dataframe(results, ['latitude', 'longitude'], 'Takeaway')
    df_takeaway['longitude'] = df_takeaway['longitude'].astype(float)
    df_takeaway['latitude'] = df_takeaway['latitude'].astype(float)
    plot_restaurants(df_takeaway, 'green', 'Takeaway Restaurants')
    con.close()

    # Sub plot of all three
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x='longitude', y='latitude', data=df_deliveroo, color='blue', label='Deliveroo')
    sns.scatterplot(x='longitude', y='latitude', data=df_ubereats, color='red', label='UberEats')
    sns.scatterplot(x='longitude', y='latitude', data=df_takeaway, color='green', label='Takeaway')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.ylim(50.50, 51.70)
    plt.xlim(2.5, 6)
    plt.title('Restaurants')
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()
    plt.close()

    # Sub plot of Deliveroo and UberEats
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x='longitude', y='latitude', data=df_deliveroo, color='blue', label='Deliveroo')
    sns.scatterplot(x='longitude', y='latitude', data=df_ubereats, color='red', label='UberEats')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.ylim(50.50, 51.70)
    plt.xlim(2.5, 6)
    plt.title('Deliveroo and UberEats Restaurants')
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()
    plt.close()

    # Plot histogram distribution of restaurants in each platform
    plt.figure(figsize=(10, 5))
    sns.histplot(df_deliveroo['latitude'], color='blue', label='Deliveroo', kde=True)
    sns.histplot(df_ubereats['latitude'], color='red', label='UberEats', kde=True)
    sns.histplot(df_takeaway['latitude'], color='green', label='Takeaway', kde=True)
    plt.xlabel('Latitude')
    plt.ylabel('Frequency')
    plt.title('Restaurant Distribution')
    plt.ylim(0, 800)
    plt.xlim(50.50, 51.60)
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()
    plt.close()


if __name__ == "__main__":
    main()







