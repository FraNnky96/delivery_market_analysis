from sqlalchemy import create_engine, Table, MetaData
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

def connect_to_database(db_path):
    engine = create_engine(db_path)
    return engine.connect()

def fetch_restaurant_titles(con, table_name, column_name):
    metadata = MetaData()
    restaurants = Table(table_name, metadata, autoload=True, autoload_with=con)
    query = con.execute(restaurants.select().with_only_columns([getattr(restaurants.c, column_name)]))
    results = query.fetchall()
    return pd.DataFrame(results, columns=['title'])

def main():
    # Fetch data from UberEats
    con = connect_to_database('sqlite:///databases/ubereats.db')
    df_ubereats = fetch_restaurant_titles(con, 'restaurants', 'title')
    df_ubereats['source'] = 'UberEats'
    con.close()

    # Fetch data from Takeaway
    con = connect_to_database('sqlite:///databases/takeaway.db')
    df_takeaway = fetch_restaurant_titles(con, 'restaurants', 'name')
    df_takeaway['source'] = 'Takeaway'
    con.close()

    # Fetch data from Deliveroo
    con = connect_to_database('sqlite:///databases/deliveroo.db')
    df_deliveroo = fetch_restaurant_titles(con, 'restaurants', 'name')
    df_deliveroo['source'] = 'Deliveroo'
    con.close()

    # Concatenate the three dataframes
    df = pd.concat([df_ubereats, df_takeaway, df_deliveroo])

    # Create a venn diagram to show the number of restaurants in each platform
    venn3([set(df[df['source'] == 'UberEats']['title']),
           set(df[df['source'] == 'Takeaway']['title']),
           set(df[df['source'] == 'Deliveroo']['title'])],
          set_labels=('UberEats', 'Takeaway', 'Deliveroo'))

    plt.show()

if __name__ == "__main__":
    main()