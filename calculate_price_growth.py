import pandas as pd

data = pd.read_csv('Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')

# Filter data for Cuyahoga County
cuyahoga_data = data[data['CountyName'] == 'Cuyahoga County']

# Extract the columns for January of each relevant year
years = list(range(2006, 2023))
jan_columns = [f"{year}-12-31" for year in years]
selected_columns = ['RegionID', 'RegionName', 'RegionType', 'StateName', 'State', 'City', 'Metro', 'CountyName'] + jan_columns
cuyahoga_data_jan = cuyahoga_data[selected_columns]

# Calculate year-over-year price growth for each ZIP code
cuyahoga_data_jan.set_index('RegionID', inplace=True)
growth_data = cuyahoga_data_jan[jan_columns].pct_change(axis=1) * 100

growth_data = growth_data.round(3)

#print(cuyahoga_data_jan)

# Extract growth rates for the relevant years (2007 to 2022, because growth for 2007 needs 2006 data, which we do not use)
growth_data_filtered = growth_data.loc[:, f'{years[1]}-12-31':f'{years[-1]}-12-31']

#print(growth_data_filtered)

# Re-add the identifying columns to the growth data
growth_data_filtered = growth_data_filtered.reset_index()
final_data = cuyahoga_data.loc[:, ['RegionID', 'RegionName', 'RegionType', 'StateName', 'State', 'City', 'Metro', 'CountyName']].merge(growth_data_filtered, on='RegionID')

# Compute average growth for each ZIP code
growth_columns = [column for column in growth_data_filtered.columns if column.endswith('-12-31')]
final_data['Average_Growth'] = final_data[growth_columns].mean(axis=1).round(3)

# Export the data to a CSV file
final_data.to_csv('cuyahoga_county_price_growth.csv', index=False)

