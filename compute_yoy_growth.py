import pandas as pd
import numpy as np

# Read the CSV file
file_path = "investor_presence_by_zip_and_year.csv"
df = pd.read_csv(file_path, index_col='ZipCode')

# Replace zeros with NaN to handle division by zero
df.replace(0, np.nan, inplace=True)

# Calculate YoY growth using percentage change
yoy_growth = df.pct_change(axis=1) * 100

# Replace 'inf' values resulting from division by zero with NaN
yoy_growth.replace([np.inf, -np.inf], np.nan, inplace=True)

# Calculate the average YoY growth for each ZipCode, skipping NaN values
average_yoy_growth = yoy_growth.mean(axis=1)

# Append the average YoY growth as a new column to the original DataFrame
df['Average_YoY_Growth'] = average_yoy_growth

# Save the updated DataFrame to a new CSV file
df.to_csv("investor_presence_by_zip_and_year_with_avg_yoy_growth.csv")