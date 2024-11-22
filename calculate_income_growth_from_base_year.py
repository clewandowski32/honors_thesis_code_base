import pandas as pd

income_yearly = pd.read_csv('../MHIOH39035A052NCEN.csv')

# Filter to include only the dates of interest
years = [f"{year}-01-01" for year in range(2007, 2023)]
income_yearly = income_yearly[income_yearly['DATE'].isin(years)]

# Ensure the 'MHIOH39035A052NCEN' column is of numeric type
income_yearly['MHIOH39035A052NCEN'] = pd.to_numeric(income_yearly['MHIOH39035A052NCEN'], errors='coerce')

# Set the DATE column as the index for easier calculation
income_yearly.set_index('DATE', inplace=True)

# Select the base year (2012-01-01) income data
base_year_income = income_yearly.at['2012-01-01', 'MHIOH39035A052NCEN']

# Calculate the percentage change from the base year
growth_data = ((income_yearly['MHIOH39035A052NCEN'] - base_year_income) / base_year_income) * 100

# Round the growth data to 3 decimal places
growth_data = growth_data.round(3)

growth_data.to_csv('../yearly_income_growth_for_cuyahoga.csv', header=['Income Growth %'])

