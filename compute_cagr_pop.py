import pandas as pd

# Load the datasets
pop_2012 = pd.read_csv('ACSDT5Y2012.B01003-2024-11-05T203926.csv', index_col=0)
pop_2022 = pd.read_csv('ACSDT5Y2022.B01003-2024-11-05T203911.csv', index_col=0)

# Filter columns to only include those that match the pattern "ZCTA5 <ZipCode>!!Households!!Estimate"
pattern = r'ZCTA5 \d{5}!!Estimate'
pop_2012_filtered = pop_2012.filter(regex=pattern)
pop_2022_filtered = pop_2022.filter(regex=pattern)

# Extract the median income row
pop_2012 = pop_2012_filtered.loc['Total']
pop_2022 = pop_2022_filtered.loc['Total']

# Function to convert string to float, stripping commas
def parse_income(income_str):
    return float(income_str.replace(',', ''))

# Initialize a dictionary to store the results
cagr_results = {'Zip Code': [], 'Population 2012': [], 'Population 2022': [], 'CAGR': []}

# Iterate over columns to compute CAGR
for column_2012 in pop_2012.index:
    # Extract the zip code from the column name
    zip_code = column_2012.split()[1].split('!!')[0]
    
    # Corresponding column in 2022
    column_2022 = f"ZCTA5 {zip_code}!!Estimate"
    
    if column_2022 in pop_2022.index:
        # Get the values for 2012 and 2022
        pop_2012_str = pop_2012[column_2012]
        pop_2022_str = pop_2022[column_2022]
        
        # Convert the income strings to floats
        pop_2012_val = parse_income(pop_2012_str)
        pop_2022_val = parse_income(pop_2022_str)
        
        # Calculate CAGR
        cagr = round((((pop_2022_val / pop_2012_val) ** (1 / 10)) - 1) * 100, 3)
        
        # Store the results
        cagr_results['Zip Code'].append(zip_code)
        cagr_results['Population 2012'].append(pop_2012_val)
        cagr_results['Population 2022'].append(pop_2022_val)
        cagr_results['CAGR'].append(cagr)

# Convert results into a DataFrame
cagr_df = pd.DataFrame(cagr_results)

# Display the result
cagr_df.to_csv('cagr_population.csv')