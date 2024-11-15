import pandas as pd
from tabulate import tabulate

# Load the CSV file
file_path = "output_2022.csv"
df = pd.read_csv(file_path)

# Ensure the relevant columns are treated as strings
df['ZipCode'] = df['deed situs zip code - static [28]'].astype(str).str[:5]
df['Year'] = df['sale derived date [43]'].astype(str).str[:4]
df['sale_amount'] = df['sale amount [42]'].astype(float)

# Filter the data where property indicator code - static equals 10
filtered_df = df[df['property indicator code - static [14]'].isin([10, 11, 21])]

# Define the years and zip codes of interest
years_of_interest = list(map(str, range(2007, 2023)))
zipcodes_of_interest = list(map(str, range(44102, 44150))) + ['44017', '44022', '44040', '44070']

# Further filter the dataframe based on the years and zip codes of interest
filtered_df = filtered_df[filtered_df['Year'].isin(years_of_interest) & filtered_df['ZipCode'].isin(zipcodes_of_interest)]

#exclude purchases where sale amount is NA or <10000
filtered_df = filtered_df[filtered_df['sale_amount'].notna() & (filtered_df['sale_amount'] >= 10000)]

#exclude purchases identified as foreclosures
filtered_df = filtered_df[(filtered_df['foreclosure reo indicator [60]'] == 0)]

# Calculate total purchase amounts per year and zip code
total_purchases = filtered_df.groupby(['Year', 'ZipCode'])['sale_amount'].sum().reset_index()

#print(total_purchases)


#excluding banks, nonprofits, mortgage lenders, government entities, etc
excluded_corporate_entities = ['CITY OF CLEVELAND','SISTERS OF THE HOLY SPIRIT',
                               'CUYAHOGA CNTY LAND REUTILIZATI', 'CHURCH'
                               'CLEVELAND HOUSING NETWORK', 'BANK'
                               'HOME RELIEF PROVIDERS LLC', 'LOAN TRUST'
                               'MTG', 'MORTGAGE', 'CREDIT'
                               'NORTHEAST OHIO NEIGHBORHOOD HE',
                               'ST CLAIR SUPERIOR COALITION'
                               'WESTERN RESERVE REVITALIZATION'
                               'CITY OF CLEVELAND LAND REUTILIZAT',
                               'CLEVELAND CLINIC',
                               'CASE WESTERN RESERVE UNIV',
                               'CLEVELAND HOUSING NETWORK',
                               'CHN HOUSING PARTNERS',
                               'CHN HSNG PTRS',
                               'FAMILY TRUST',
                               'CITY OF EAST CLEVELAND LAND REUTI',
                               'EAST CLEVELAND LAND REUTILIZAT',
                               'HUD-HOUSING OF URBAN DEV',
                               'SECRETARY OF VETERANS AFFAIRS',
                               'HABITAT FOR HUMANITY',
                               'S & L',
                               'CATHOLIC CU INC',
                               'CATHOLIC DIOCESE OF CLEVELAND',
                               'HOSPITAL',
                               'RELOCATION',
                               'CONSTRUCTION',
                               'REUTILIZATI',
                               'STATE OF OHIO',
                               'DEPARTMENT',
                               'HUD-HOUSING OF URBAN DEV',
                               'SECRETARY OF HUD',
                               'CMNTY DEV',
                               'HOME REPAIR RESOURCE CENTER',
                               'CLINIC',
                               'FOUNDATION',
                               'BK',
                               'LOAN',
                               'HOMELESS',
                               'HSNG AUT',
                               'SOCIETY',
                               'CITY OF',
                               'CMNTY',
                               'VILLAGE OF',
                               'SLAVIC VILLAGE RECOVERY LLC',
                               'CREDIT',
                               'HUD',
                               'PENTECOSTAL',
                               'ISLAM',
                               'CHRISTIAN',
                               'HEALTH',
                               'MISSIONARY',
                               'DIOCESE',
                               'LAND REUTILIZ',
                               'ACADEMY',
                               'SCHOOL',
                               'HEBREW',
                               'JEWISH',
                               'HISPANIC',
                               'COMMUNITY',
                               'REINVESTMENT',
                               'CHASE',
                               'OHIO TITLE CORP',
                               'EDUCATION',
                               'LAND TRUST',
                               'BOARD OF',
                               'BUILDERS',
                               'CHILD',
                               'FINANCIAL']

# Create a single regular expression pattern
pattern = '|'.join([f"({entity})" for entity in excluded_corporate_entities])

# Calculate total purchase amounts by investors per year and zip code
condition_investor_purchase = (filtered_df['investor purchase indicator [55]'] == 1)
#condition_occupancy_code = filtered_df['buyer occupancy code [82]'].isin(['A', 'T'])
condition_corporate_indicator = (
    (filtered_df['buyer 1 corporate indicator [68]'] == 'Y') |
    (filtered_df['buyer 2 corporate indicator [69]'] == 'Y') |
    (filtered_df['buyer 3 corporate indicator [73]'] == 'Y') |
    (filtered_df['buyer 4 corporate indicator [77]'] == 'Y')
)
condition_full_name = (
    ~filtered_df['buyer 1 full name [62]'].str.contains(pattern, case=False, na=False) &
    ~filtered_df['buyer 2 full name [65]'].str.contains(pattern, case=False, na=False) &
    ~filtered_df['buyer 3 full name [70]'].str.contains(pattern, case=False, na=False) &
    ~filtered_df['buyer 4 full name [74]'].str.contains(pattern, case=False, na=False)
)

# Combine conditions
conditions = (
    condition_investor_purchase |
    #condition_occupancy_code |
    (condition_corporate_indicator & condition_full_name)
)

identified_investors = filtered_df[conditions]

# Export to CSV
identified_investors.to_csv('output_2022_id_inv.csv', na_rep='NA', index=False)

#investor_purchases = filtered_df[conditions].groupby(['Year', 'ZipCode'])['sale_amount']\
#                                             .sum().reset_index()

investor_purchases = filtered_df[conditions]\
    .groupby(['Year', 'ZipCode'])['sale_amount']\
    .sum()\
    .reset_index()
investor_purchases.rename(columns={'sale_amount': 'investor_sales_amount'}, inplace=True)
#print(investor_purchases)

# Merge the two dataframes to compute the percentage
merged_df = pd.merge(total_purchases, investor_purchases, on=['Year', 'ZipCode'], how='left').fillna(0)
merged_df['investor_presence_percentage'] = round((merged_df['investor_sales_amount'] / merged_df['sale_amount']) * 100, 3)

# Pivot the table for a better display
pivot_table = merged_df.pivot_table(index='ZipCode', columns='Year', values='investor_presence_percentage', fill_value=0)

pivot_table['Average_Investor_Presence'] = round(pivot_table.mean(axis=1), 3)

# Optionally, save the pivot table to a new CSV file
pivot_table.to_csv("investor_presence_by_zip_and_year_all_res_flow.csv")