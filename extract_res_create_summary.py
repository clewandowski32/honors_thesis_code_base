import pandas as pd
from tabulate import tabulate

# Load the CSV file
file_path = "output_2022.csv"  # replace with your actual file path
df = pd.read_csv(file_path)

# Filter the data where property indicator code - static equals 10
filtered_df = df[df['          property indicator code - static [14]'].isin([10, 11, 21, 22])]

# Extract the year from the sale derived date [43]
filtered_df['Year'] = filtered_df['         sale derived date [43]'].astype(str).str[:4].astype(int)

# Extract the first 5 characters of the zip code
filtered_df['ZipCode'] = filtered_df[' deed situs zip code - static [28]'].astype(str).str[:5]

# Filter ZipCodes of interest
zipcodes_of_interest = [str(zipcode) for zipcode in list(range(44102, 44150)) + [44017, 44022, 44040, 44070]]
filtered_df = filtered_df[filtered_df['ZipCode'].isin(zipcodes_of_interest)]

# Filter Years of interest
years_of_interest = list(range(2000, 2023))
filtered_df = filtered_df[filtered_df['Year'].isin(years_of_interest)]

# Create a pivot table with the counts of purchases
pivot_table = filtered_df.pivot_table(index='ZipCode', columns='Year', aggfunc='size', fill_value=0)

# Display the pivot table (nicely formatted)
print(tabulate(pivot_table, headers='keys', tablefmt='github'))

# Save the pivot table to a new CSV file (optional)
pivot_table.to_csv("filtered_purchases_by_zip_and_year_all_residential.csv")