from sqlalchemy import create_engine, text
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Function to fetch data for Deliveroo
def get_deliveroo_data():
    engine = create_engine('sqlite:///databases/deliveroo.db')

    with engine.connect() as con:
        stmt = text("""
        SELECT postal_code, COUNT(name) as restaurant_count
        FROM restaurants
        GROUP BY postal_code
        """)
        result = con.execute(stmt)
        data = result.fetchall()

    df = pd.DataFrame(data, columns=['postal_code', 'restaurant_count'])

    # Clean postal_code column
    df['postal_code'] = df['postal_code'].str.replace(r'\D', '', regex=True)
    df['postal_code'] = pd.to_numeric(df['postal_code'], errors='coerce')

    # Remove NaN and zero postal codes
    df = df.dropna(subset=['postal_code'])
    df = df[df['postal_code'] != 0]

    # Postal code to province mapping
    postal_code_mapping = {
        range(1000, 1300): 'Brussels-Capital Region',
        range(1300, 1500): 'Walloon Brabant',
        range(1500, 2000): 'Flemish Brabant',
        range(2000, 3000): 'Antwerp',
        range(3000, 3500): 'Flemish Brabant',
        range(3500, 4000): 'Limburg',
        range(4000, 5000): 'Liège',
        range(5000, 6000): 'Namur',
        range(6600, 7000): 'Luxembourg',
        range(7000, 8000): 'Hainaut',
        range(8000, 9000): 'West Flanders',
        range(9000, 10000): 'East Flanders',
    }

    # Map postal codes to provinces
    def get_province(postal_code):
        for postal_range, province in postal_code_mapping.items():
            if postal_range.start <= postal_code <= postal_range.stop - 1:
                return province
        return "Unknown"

    df['province'] = df['postal_code'].apply(get_province)

    # Group by province and sum the restaurant count
    df_province = df.groupby('province').agg({'restaurant_count': 'sum'}).reset_index()
    df_province_sorted = df_province.sort_values(by='restaurant_count', ascending=False)

    # Add missing provinces with zero restaurants
    all_provinces = ['Brussels-Capital Region', 'Walloon Brabant', 'Flemish Brabant', 'Antwerp', 'Limburg', 'Liège', 'Namur', 'Luxembourg', 'Hainaut', 'West Flanders', 'East Flanders']
    df_province_full = pd.DataFrame(all_provinces, columns=['province'])
    df_province_full = pd.merge(df_province_full, df_province_sorted, on='province', how='left').fillna(0)
    df_province_full = df_province_full.sort_values(by='restaurant_count', ascending=False)
    df_province_full['platform'] = 'Deliveroo'

    return df_province_full

# Function to fetch data for UberEats
def get_ubereats_data():
    engine = create_engine('sqlite:///databases/ubereats.db')

    with engine.connect() as con:
        stmt = text("""
        SELECT location__geo__region, COUNT(location__geo__region) as province_count
        FROM restaurants
        GROUP BY location__geo__region
        ORDER BY province_count DESC
        """)
        result = con.execute(stmt)
        data = result.fetchall()

    df = pd.DataFrame(data)
    df.columns = ['province', 'province_count']

    # Clean province names
    df.loc[df['province'] == 'anvers', 'province'] = 'Antwerp'
    df.loc[df['province'] == 'bruxelles-capitale', 'province'] = 'Brussels'
    df.loc[df['province'] == 'flandre-orientale', 'province'] = 'East Flanders'
    df.loc[df['province'] == 'brabant-flamand', 'province'] = 'Flemish Brabant'
    df.loc[df['province'] == 'flandre-occidentale', 'province'] = 'West Flanders'
    df.loc[df['province'] == 'brabant-wallon', 'province'] = 'Walloon Brabant'
    df.loc[df['province'] == 'limbourg', 'province'] = 'Limburg'
    df.loc[df['province'] == 'liÃ¨ge', 'province'] = 'Liège'
    df.loc[df['province'] == 'hainaut', 'province'] = 'Hainaut'
    df.loc[df['province'].isnull(), 'province'] = 'Luxemburg'

    # Add missing province for UberEats (example)
    df = df._append({'province': 'Namen', 'province_count': 0}, ignore_index=True)

    df['platform'] = 'UberEats'

    return df

# Function to fetch data for Takeaway
def get_takeaway_data():
    engine = create_engine('sqlite:///databases/takeaway.db')

    with engine.connect() as con:
        stmt = text("""
        SELECT DISTINCT r.primarySlug, loc.postalCode
        FROM restaurants AS r
        LEFT JOIN locations_to_restaurants AS l ON r.primarySlug = l.restaurant_id
        LEFT JOIN locations AS loc ON l.location_id = loc.id
        """)
        result = con.execute(stmt)
        data = result.fetchall()

    df = pd.DataFrame(data, columns=['primarySlug', 'postalCode'])
    unique_rest_with_postal = df.drop_duplicates(subset='primarySlug')

    postal_code_to_province = {
        range(1000, 1300): 'Brussels-Capital Region',
        range(1300, 1500): 'Walloon Brabant',
        range(1500, 2000): 'Flemish Brabant',
        range(2000, 3000): 'Antwerp',
        range(3000, 3500): 'Flemish Brabant',
        range(3500, 4000): 'Limburg',
        range(4000, 5000): 'Liège',
        range(5000, 6000): 'Namur',
        range(6600, 7000): 'Luxembourg',
        range(7000, 8000): 'Hainaut',
        range(8000, 9000): 'West Flanders',
        range(9000, 10000): 'East Flanders',
    }

    def get_province(postal_code):
        if pd.isna(postal_code):
            return None
        postal_code = int(postal_code)
        for postal_range, province in postal_code_to_province.items():
            if postal_code in postal_range:
                return province
        return 'Unknown'

    unique_rest_with_postal['province'] = unique_rest_with_postal['postalCode'].apply(get_province)

    province_counts = unique_rest_with_postal['province'].value_counts()

    all_provinces = ['Brussels-Capital Region', 'Walloon Brabant', 'Flemish Brabant', 'Antwerp', 'Limburg', 'Liège', 'Namur', 'Luxembourg', 'Hainaut', 'West Flanders', 'East Flanders']
    province_counts = province_counts.reindex(all_provinces).fillna(0).sort_values(ascending=False)

    province_counts_df = province_counts.reset_index()
    province_counts_df.columns = ['province', 'restaurant_count']
    province_counts_df['platform'] = 'Takeaway'

    return province_counts_df

# Fetch data for each plot
df_deliveroo = get_deliveroo_data()
df_ubereats = get_ubereats_data()
df_takeaway = get_takeaway_data()

# Combine all datasets into one DataFrame
combined_df = pd.concat([df_deliveroo[['province', 'restaurant_count', 'platform']],
                         df_ubereats[['province', 'province_count', 'platform']].rename(columns={'province_count': 'restaurant_count'}),
                         df_takeaway[['province', 'restaurant_count', 'platform']]])

# Group by province and platform, then sum the restaurant counts
combined_df_sorted = combined_df.groupby(['province', 'platform']).agg({'restaurant_count': 'sum'}).reset_index()

# Sort by the total restaurant count per province across all platforms
province_total_counts = combined_df_sorted.groupby('province').agg({'restaurant_count': 'sum'}).sort_values(by='restaurant_count', ascending=False).reset_index()

# Merge sorted province totals back to the combined DataFrame for plotting
combined_df_sorted['province'] = pd.Categorical(combined_df_sorted['province'], categories=province_total_counts['province'], ordered=True)

# Standardize 'Brussels' and 'Brussels-Capital Region' to a single province name
combined_df_sorted['province'] = combined_df_sorted['province'].replace({
    'Brussels': 'Brussels-Capital Region',
    'Brussels-Capital Region': 'Brussels-Capital Region',
    'Namen': 'Namur',  # Merge 'Namen' into 'Namur'
    'Namur': 'Namur',    # Ensure 'Namur' stays as 'Namur'
    'Luxemburg': 'Luxembourg',  # Merge 'Luxemburg' into 'Luxembourg'
    'Luxembourg': 'Luxembourg'  # Ensure 'Luxembourg' stays as 'Luxembourg'
})

# Recompute the counts after merging the provinces
province_counts = combined_df_sorted.groupby('province')['restaurant_count'].sum().reset_index()

# Re-sort provinces by restaurant count (highest to lowest)
province_counts = province_counts.sort_values(by='restaurant_count', ascending=False)

# Define a custom palette where Deliveroo is red, UberEats is green, and Takeaway is blue
custom_palette = {
    'Deliveroo': 'blue',
    'UberEats': 'red',
    'Takeaway': 'green'
}

# Create the bar plot for all three platforms
plt.figure(figsize=(14, 8))
ax = sns.barplot(x='restaurant_count', y='province', hue='platform', data=combined_df_sorted, palette=custom_palette)

# Move the legend to the bottom right
plt.legend(loc='lower right', bbox_to_anchor=(1, 0))

plt.title('Distribution of Restaurants by Province (Deliveroo, UberEats, Takeaway)')
plt.xlabel('Number of Restaurants')
plt.ylabel('Province')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

