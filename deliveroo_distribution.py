import pandas as pd
from sqlalchemy import create_engine, text
import seaborn as sns
import matplotlib.pyplot as plt

# Create engine to connect to the database
engine = create_engine('sqlite:///databases/deliveroo.db')

# Use a context manager to handle the connection
with engine.connect() as con:
    # Query the database to get restaurant counts by postal code
    stmt = text("""
    SELECT postal_code, COUNT(name) as restaurant_count
    FROM restaurants
    GROUP BY postal_code
    """)
    
    # Execute the query and fetch the results
    result = con.execute(stmt)
    data = result.fetchall()

# Create a DataFrame from the results
df = pd.DataFrame(data, columns=['postal_code', 'restaurant_count'])

# Clean postal_code column: Remove non-numeric characters and convert to integers
df['postal_code'] = df['postal_code'].str.replace(r'\D', '', regex=True)
df['postal_code'] = pd.to_numeric(df['postal_code'], errors='coerce')

# Drop rows with NaN postal codes or invalid postal codes (e.g., zero)
df = df.dropna(subset=['postal_code'])
df = df[df['postal_code'] != 0]

# Postal code to province mapping
postal_code_mapping = {
    range(1000, 1300): 'Brussels-Capital Region',
    range(1300, 1500): 'Walloon Brabant',
    range(1500, 2000): 'Flemish Brabant',  # First range for Flemish Brabant (1500 - 1999)
    range(3000, 3500): 'Flemish Brabant',  # Second range for Flemish Brabant (3000 - 3499)
    range(2000, 3000): 'Antwerp',
    range(3500, 4000): 'Limburg',
    range(4000, 5000): 'Liège',
    range(5000, 6000): 'Namur',
    range(6600, 7000): 'Luxembourg',
    range(7000, 8000): 'Hainaut',
    range(8000, 9000): 'West Flanders',
    range(9000, 10000): 'East Flanders',
}

# Function to map postal codes to provinces
def get_province(postal_code):
    """Returns the province based on postal code ranges"""
    for postal_range, province in postal_code_mapping.items():
        if postal_range.start <= postal_code <= postal_range.stop - 1:
            return province
    return "Unknown"  # Return "Unknown" if no matching range

# Apply the function to the postal code column to replace with province names
df['province'] = df['postal_code'].apply(get_province)

# Group by province and sum the restaurant count
df_province = df.groupby('province').agg({'restaurant_count': 'sum'}).reset_index()

# Sort the DataFrame by restaurant_count in descending order
df_province_sorted = df_province.sort_values(by='restaurant_count', ascending=False)

# Make sure to show all provinces, filling missing ones with zero counts
# Add missing provinces with zero restaurants if they're not in the dataset
all_provinces = [
    'Brussels-Capital Region', 'Walloon Brabant', 'Flemish Brabant', 'Antwerp', 'Limburg', 
    'Liège', 'Namur', 'Luxembourg', 'Hainaut', 'West Flanders', 'East Flanders'
]

# Create a DataFrame with all provinces and merge with restaurant counts
df_province_full = pd.DataFrame(all_provinces, columns=['province'])
df_province_full = pd.merge(df_province_full, df_province_sorted, on='province', how='left').fillna(0)

# Sort by restaurant_count again in descending order
df_province_full = df_province_full.sort_values(by='restaurant_count', ascending=False)

# Print the provinces
print(df_province_full)

# Create a bar plot for the number of restaurants by province
plt.figure(figsize=(12, 6))
sns.barplot(x='restaurant_count', y='province', data=df_province_full, palette='viridis')
plt.xlabel('Number of Restaurants')
plt.ylabel('Province')
plt.title('All Provinces by Number of Restaurants for Deliveroo')
plt.xticks(rotation=45)
plt.show()















