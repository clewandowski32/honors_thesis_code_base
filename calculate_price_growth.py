import pandas as pd

data = pd.read_csv('../Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv')

# Filter data for Cuyahoga County
cuyahoga_data = data[data['CountyName'] == 'Cuyahoga County']
# Change RegionName identifier to zip code
cuyahoga_data['ZipCode'] = cuyahoga_data['RegionName']

# Extract the columns for December of each relevant year
years = list(range(2006, 2023))
dec_columns = [f"{year}-12-31" for year in years]
selected_columns = ['ZipCode'] + dec_columns
cuyahoga_data_dec = cuyahoga_data[selected_columns]

# Calculate year-over-year price growth for each ZIP code
cuyahoga_data_dec.set_index('ZipCode', inplace=True)
growth_data = cuyahoga_data_dec[dec_columns].pct_change(axis=1) * 100

growth_data = growth_data.round(3)

# Extract growth rates for the relevant years (2007 to 2022, because growth for 2007 needs 2006 data, which we do not use)
growth_data_filtered = growth_data.loc[:, f'{years[1]}-12-31':f'{years[-1]}-12-31']

growth_data_filtered = growth_data_filtered.reset_index()

# Melt the DataFrame to long format for growth data
long_format_growth_df = growth_data_filtered.melt(id_vars=['ZipCode'],
                                                  var_name='Year',
                                                  value_name='Price_Growth')
# Adding the 'Year' column for clarity
long_format_growth_df['Year'] = long_format_growth_df['Year'].str[:4]

long_format_growth_df = long_format_growth_df.sort_values(by=['ZipCode', 'Year'])

# Also melt the price data to long format
cuyahoga_data_dec.reset_index(inplace=True)
long_format_price_df = cuyahoga_data_dec.melt(id_vars=['ZipCode'],
                                              var_name='Year',
                                              value_name='Price')
long_format_price_df['Year'] = long_format_price_df['Year'].str[:4]

long_format_price_df = long_format_price_df.sort_values(by=['ZipCode', 'Year'])

long_format_price_df['Price'] = long_format_price_df['Price'].round(2)

# Merge the growth data and price data
final_long_df = pd.merge(long_format_growth_df, long_format_price_df, on=['ZipCode', 'Year'])

final_long_df.to_csv('../cuyahoga_county_price_growth_and_prices_2007_to_2022.csv', index=False)

