import pandas as pd

# Load the datasets
income_2012 = pd.read_csv('../ACSST5Y2012.S1901-2024-11-05T203537.csv', index_col=0)
income_2022 = pd.read_csv('../ACSST5Y2022.S1901-2024-11-05T203357.csv', index_col=0)

# Filter columns to only include those that match the pattern "ZCTA5 <ZipCode>!!Households!!Estimate"
pattern = r'ZCTA5 \d{5}!!Households!!Estimate'
income_2012_filtered = income_2012.filter(regex=pattern)
income_2022_filtered = income_2022.filter(regex=pattern)

# Extract the median income row
median_income_2012 = income_2012_filtered.loc['Median income (dollars)']
median_income_2022 = income_2022_filtered.loc['Median income (dollars)']

# Function to convert string to float, stripping commas
def parse_income(income_str):
    return float(income_str.replace(',', ''))

# Initialize a dictionary to store the results
cagr_results = {'Zip Code': [], 'Income 2012': [], 'Income 2022': [], 'CAGR': []}

# Iterate over columns to compute CAGR
for column_2012 in median_income_2012.index:
    # Extract the zip code from the column name
    zip_code = column_2012.split()[1].split('!!')[0]
    
    # Corresponding column in 2022
    column_2022 = f"ZCTA5 {zip_code}!!Households!!Estimate"
    
    if column_2022 in median_income_2022.index:
        # Get the values for 2012 and 2022
        income_2012_str = median_income_2012[column_2012]
        income_2022_str = median_income_2022[column_2022]
        
        # Convert the income strings to floats
        income_2012_val = parse_income(income_2012_str)
        income_2022_val = parse_income(income_2022_str)
        
        # Calculate CAGR
        cagr = round((((income_2022_val / income_2012_val) ** (1 / 10)) - 1) * 100, 3)
        
        # Store the results
        cagr_results['Zip Code'].append(zip_code)
        cagr_results['Income 2012'].append(income_2012_val)
        cagr_results['Income 2022'].append(income_2022_val)
        cagr_results['CAGR'].append(cagr)

# Convert results into a DataFrame
cagr_df = pd.DataFrame(cagr_results)

# Display the result
cagr_df.to_csv('../cagr_median_income.csv')