import pandas as pd

file_path_transfer = "output_2022.csv"  # replace with your actual file path
df_transfer = pd.read_csv(file_path_transfer)

file_path_tax = "output_2022_tax.csv"
df_tax = pd.read_csv(file_path_tax)

df_transfer['ZipCode'] = df_transfer['deed situs zip code - static [28]'].astype(str).str[:5]
df_transfer['Year'] = df_transfer['sale derived date [43]'].astype(str).str[:4]
df_transfer['sale_amount'] = df_transfer['sale amount [42]'].astype(float)

filtered_df = df_transfer[df_transfer['property indicator code - static [14]'].isin([10, 11, 21, 22])]

# Define the years and zip codes of interest
years_of_interest = list(map(str, range(2007, 2023)))
zipcodes_of_interest = list(map(str, range(44102, 44150))) + ['44017', '44022', '44040', '44070']

filtered_df = filtered_df[filtered_df['Year'].isin(years_of_interest) & filtered_df['ZipCode'].isin(zipcodes_of_interest)]

filtered_df['Year'] = filtered_df['Year'].astype(int)
filtered_df = filtered_df.sort_values(by=['Year'])

# Calculate total purchase amounts by investors per year and zip code

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

investor_purchases = filtered_df[conditions]\
    .groupby(['Year', 'ZipCode'])['sale_amount']\
    .sum()\
    .reset_index()
investor_purchases.rename(columns={'sale_amount': 'investor_sales_amount'}, inplace=True)
#print(investor_purchases)

cumulative_purchases_investor = investor_purchases.groupby(['ZipCode', 'Year'])['investor_sales_amount'].sum().groupby(level=0).cumsum().reset_index()

print(cumulative_purchases_investor)

df_tax['ZipCode'] = df_tax[' situs zip code [59]'].astype(str).str[:5]

# Convert the ' total value calculated [112]' column to numeric, setting errors='coerce' to handle non-numeric values
df_tax['total_value'] = pd.to_numeric(df_tax[' total value calculated [112]'], errors='coerce')

# Drop rows with NaN values in the 'total_value' column
df_tax = df_tax.dropna(subset=['total_value'])

# Sum the total values by Zip Code
total_value = df_tax.groupby(['ZipCode'])['total_value'].sum().reset_index()

# Print the resulting DataFrame
print(total_value)

merged_df = cumulative_purchases_investor.merge(total_value, on='ZipCode', how='left')

print(merged_df)

# Calculate investor presence
merged_df['investor_presence_percentage'] = round((merged_df['investor_sales_amount'] / merged_df['total_value']) * 100, 3)

print(merged_df)

merged_df.to_csv("summary_investor_purchases.csv")

pivot_table = merged_df.pivot_table(index='ZipCode', columns='Year', values='investor_presence_percentage', fill_value=0)

# Print the resulting DataFrame
pivot_table.to_csv("investor_presence_by_zip_and_year_all_res_stock.csv")