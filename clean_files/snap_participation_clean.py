# Import the pandas library as 'pd'
import pandas as pd

# Define a list of years
year_list = [2018, 2019, 2021]

# Initialize an empty list to store DataFrames
df_list = []

# Loop through each year in the year_list
for year in year_list:
    # Construct the API URL for Census data for the specific year
    api_url = f'https://api.census.gov/data/{year}/acs/acs5/subject?get=NAME,S2201_C01_001E,S2201_C01_021E&for=county:*&in=state:*'
    
    # Read data from the API URL into a DataFrame
    df = pd.read_json(api_url)
    
    # Set the column names to the values in the first row
    df.columns = df.iloc[0]
    
    # Drop the first row, which contains the column names, as it's no longer needed
    df = df.drop(0, axis=0)
    
    # Rename columns for clarity
    df.columns = ['county_name', 'total_households', 'receiving_snap', 'state_code', 'county_code']
    
    # Add a 'Year' column to the DataFrame and set it to the current year
    df['Year'] = year
    
    # Append the DataFrame for the current year to df_list
    df_list.append(df)

# Concatenate all the DataFrames in df_list into a single DataFrame
all_df = pd.concat(df_list)

# Write the concatenated DataFrame to a CSV file without the index column
all_df.to_csv(r'/Users/jackogozaly/Desktop/Python_Directory/snap_participation.csv', index=False)
