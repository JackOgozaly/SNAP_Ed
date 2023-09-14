# Import necessary libraries
import pandas as pd
import numpy as np
from functools import reduce

# Define eligibility criteria as a dictionary (state: income limit)
eligibility_df = {'Alabama': 130,
                'Arizona': 185,
                'California': 200,
                'Colorado': 200,
                'Connecticut': 200,
                'Delaware': 200,
                'District of Columbia': 200,
                'Florida': 200,
                'Georgia': 130,
                'Guam': 165,
                'Hawaii': 200,
                'Idaho': 130,
                'Illinois': 165,
                'Indiana': 130,
                'Iowa': 160,
                'Kentucky': 200,
                'Louisiana': 130,
                'Maine': 185,
                'Maryland': 200,
                'Massachusetts': 200,
                'Michigan': 200,
                'Minnesota': 200,
                'Montana': 200,
                'Nebraska': 165,
                'Nevada': 200,
                'New Hampshire': 200,
                'New Jersey': 185,
                'New Mexico': 165,
                'New York': 150,
                'North Carolina': 200,
                'North Dakota': 200,
                'Ohio': 130,
                'Oklahoma': 130,
                'Oregon': 200,
                'Pennsylvania': 200,
                'Rhode Island': 185,
                'South Carolina': 130,
                'Texas': 165,
                'Vermont': 185,
                'Virgin Islands': 175,
                'Virginia': 200,
                'Washington': 200,
                'West Virginia': 200,
                'Wisconsin': 200,
                'Alaska':185, #Imputed Value
                'Arkansas':185,  #Imputed Value
                'Kansas':185,  #Imputed Value
                'Mississippi':185,  #Imputed Value
                'Missouri':185,  #Imputed Value
                'South Dakota':185,  #Imputed Value
                'Tennessee':185,  #Imputed Value
                'Utah':185, #Imputed Value
                'Wyoming':185  #Imputed Value
                }

# Convert the dictionary to a Pandas DataFrame
eligibility_df = pd.DataFrame.from_dict(eligibility_df, orient='index').reset_index(drop=False)
eligibility_df.columns = ['State', 'Income_Limit']

# Set a minimum income limit of 185 for states with lower limits
eligibility_df.loc[eligibility_df['Income_Limit'] < 185, 'Income_Limit'] = 185

# Read a CSV file containing state FIPS codes from a URL
state_fips = pd.read_csv(r'https://gist.githubusercontent.com/dantonnoriega/bf1acd2290e15b91e6710b6fd3be0a53/raw/11d15233327c8080c9646c7e1f23052659db251d/us-state-ansi-fips.csv')

# Merge the eligibility DataFrame with the state FIPS DataFrame based on state names
eligibility_df = pd.merge(eligibility_df, state_fips,
                          how='left',
                          left_on='State',
                          right_on='stname')

# Drop rows with missing FIPS code information
eligibility_df = eligibility_df.dropna(subset=[' st'])


# Define a list of years
year_list = [2018, 2019, 2021]

# Initialize an empty list to store DataFrames
df_list = []

# Loop through each year in the year_list
for year in year_list:
    # Read data from a Census API for the specified year
    sub_api = pd.read_json(f"https://api.census.gov/data/{year}/acs/acs1/pums?get=SEX,RAC1P,POVPIP,HISP,DIS,AGEP,HHL,PWGTP&for=state:*")
    
    # Set the column names to the values in the first row
    sub_api.columns = sub_api.iloc[0]
    
    # Drop the first row (it contains column names)
    sub_api = sub_api.drop(0, axis=0)

    # Add a 'Year' column to the DataFrame to store the current year
    sub_api['Year'] = year

    # Append the DataFrame for the current year to the df_list
    df_list.append(sub_api)

# Concatenate all DataFrames in df_list into a single DataFrame
all_df = pd.concat(df_list)

# Convert the 'POVPIP' column to numeric values (assuming it contains numeric data)
all_df['POVPIP'] = pd.to_numeric(all_df['POVPIP'])

# Define a dictionary to remap race codes to descriptive names
race = {
    "3": "American Indian alone",
    "1": "White alone",
    "8": "Some Other Race alone",
    "6": "Asian alone",
    "9": "Two or More Races",
    "2": "Black or African American alone",
    "4": "Alaska Native alone",
    "7": "Native Hawaiian and Other Pacific Islander alone",
    "5": "American Indian and Alaska Native tribes specified; or American Indian or Alaska Native, not specified and no other races"
}

# Define a dictionary to remap disability codes to descriptive names
disability = {
    "1": "With a disability",
    "2": "Without a disability"
}

# Define a dictionary to remap sex codes to descriptive names
sex = {
    "1": "Male",
    "2": "Female"
}

# Define a dictionary to remap household language codes to descriptive names
HHL = {
    "3": "Other Indo-European languages",
    "0": "N/A (GQ/vacant)",
    "2": "Spanish",
    "1": "English Only",
    "4": "Asian and Pacific Island languages",
    "5": "Other Language"
}

# Create a list of unique income limit values from the eligibility_df DataFrame
pov_levels = list(eligibility_df['Income_Limit'].unique())

# Initialize an empty list to store DataFrames for each poverty level
state_dfs = []

# Loop through each poverty level (pov) in the list of poverty levels (pov_levels)
for pov in pov_levels:
    # Create a copy of the 'all_df' DataFrame
    sub_df = all_df.copy()
    
    # Filter rows where 'POVPIP' is within the range [0, pov]
    sub_df = sub_df[sub_df['POVPIP'].between(0, pov)]
    print(f"Rows in sub_df check -1: {len(sub_df)}")
    
    # Get a list of states eligible for the current poverty level
    eligible_states = list(eligibility_df[eligibility_df['Income_Limit'] == pov][' st'].astype(int).unique())
    
    # Convert the 'state' column to integers and filter rows based on eligible states
    sub_df['state'] = sub_df['state'].astype(int)
    sub_df = sub_df[sub_df['state'].isin(eligible_states)]
    print(f"Rows in sub_df check 0: {len(sub_df)}")

    # Data remapping
    # Remap the 'RAC1P' column for race
    sub_df['RAC1P'] = sub_df['RAC1P'].replace(race)
    
    # Convert 'HISP' column to a binary Y/N for Hispanic status
    sub_df['HISP'] = pd.to_numeric(sub_df['HISP'])
    sub_df['HISP'] = np.where(sub_df['HISP'] == 1, 'Not Spanish/Hispanic/Latino', 'Spanish/Hispanic/Latino')
    
    # Remap 'HHL' column for household language
    sub_df['HHL'] = sub_df['HHL'].replace(HHL)
    
    # Remap 'SEX' column for sex
    sub_df['SEX'] = sub_df['SEX'].replace(sex)
    
    # Remap 'DIS' column for disability
    sub_df['DIS'] = sub_df['DIS'].replace(disability)
    
    # Transform 'AGEP' into age buckets
    sub_df['AGEP'] = pd.to_numeric(sub_df['AGEP'])
    sub_df['Age_Group'] = np.where(sub_df['AGEP'] < 5, 'less_than_5', np.NaN)
    sub_df['Age_Group'] = np.where(sub_df['AGEP'].between(5, 17, inclusive='both'), '5_17', sub_df['Age_Group'])
    sub_df['Age_Group'] = np.where(sub_df['AGEP'].between(18, 59, inclusive='both'), '18_59', sub_df['Age_Group'])
    sub_df['Age_Group'] = np.where(sub_df['AGEP'] >= 60, 'greater_than_60', sub_df['Age_Group'])
    
    # Drop the continuous 'AGEP' column now that age groups are created
    sub_df = sub_df.drop('AGEP', axis=1)
    
    print(f"Rows in sub_df check 1: {len(sub_df)}")
    
    # Aggregate data by grouping and summing based on specific columns
    sub_df['PWGTP'] = pd.to_numeric(sub_df['PWGTP'])
    sub_df = sub_df.groupby(['SEX', 'RAC1P', 'HISP', 'Age_Group', 'HHL', 'DIS', 'Year', 'state'])['PWGTP'].sum().reset_index(drop=False)
    
    print(f"Rows in sub_df check 2: {len(sub_df)}")
    
    # Pivot values for sex and age
    sex_age = sub_df.pivot_table(index=['state', 'Year'], columns=['SEX', 'Age_Group'], values='PWGTP', aggfunc='sum').reset_index(drop=False)
    sex_age = sex_age.sort_index(axis=1, level=1)
    sex_age.columns = [f'{x}_{y}' for x, y in sex_age.columns]
    sex_age = sex_age.rename(columns={'state_': 'state', 'Year_': 'Year'})

    # Pivot values for race
    race_df = sub_df.pivot_table(index=['state', 'Year'], columns=['RAC1P'], values='PWGTP', aggfunc='sum').reset_index(drop=False)
    race_df = race_df.sort_index(axis=1, level=1)

    # Pivot values for disability
    dis_df = sub_df.pivot_table(index=['state', 'Year'], columns=['DIS'], values='PWGTP', aggfunc='sum').reset_index(drop=False)
    dis_df = dis_df.sort_index(axis=1, level=1)

    # Pivot values for Hispanic status
    hisp_df = sub_df.pivot_table(index=['state', 'Year'], columns=['HISP'], values='PWGTP', aggfunc='sum').reset_index(drop=False)
    hisp_df = hisp_df.sort_index(axis=1, level=1)

    # Pivot values for household language
    language_df = sub_df.pivot_table(index=['state', 'Year'], columns=['HHL'], values='PWGTP', aggfunc='sum').reset_index(drop=False)
    language_df = language_df.sort_index(axis=1, level=1)

    # Combine the DataFrames using reduce and merge
    dfList = [sex_age, race_df, hisp_df, language_df, dis_df]
    sub_df2 = reduce(lambda x, y: x.merge(y, on=['state', 'Year']), dfList)

    # Append the resulting DataFrame to the state_dfs list
    state_dfs.append(sub_df2)

# Concatenate all DataFrames in state_dfs into a single DataFrame
state_data = pd.concat(state_dfs)


# Initialize an empty list to store DataFrames for total population
totaL_pop_list = []

# Loop through each year in the year_list
for year in year_list:
    # Read total population data from the Census API for the specified year
    total_pop = pd.read_json(f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B01001_001E&for=state:*")
    
    # Set the column names to the values in the first row
    total_pop.columns = total_pop.iloc[0]
    
    # Drop the first row (it contains column names)
    total_pop = total_pop.drop(0, axis=0)

    # Add a 'Year' column to the DataFrame to store the current year
    total_pop['Year'] = year

    # Append the DataFrame for the current year to totaL_pop_list
    totaL_pop_list.append(total_pop)

# Concatenate all DataFrames in totaL_pop_list into a single DataFrame
total_pop = pd.concat(totaL_pop_list)

# Rename the 'B01001_001E' column to 'total_pop'
total_pop = total_pop.rename(columns={'B01001_001E': 'total_pop'})

# Convert 'state' and 'total_pop' columns to integers
total_pop['state'] = total_pop['state'].astype(int)
total_pop['total_pop'] = total_pop['total_pop'].astype(int)

# Drop the 'NAME' column
total_pop = total_pop.drop(['NAME'], axis=1)

# Merge the total population DataFrame with the state_data DataFrame based on state and year
state_data = pd.merge(state_data, total_pop,
                      how='left',
                      left_on=['state', 'Year'],
                      right_on=['state', 'Year'])

# Read tribal land data from a CSV file hosted on GitHub
tribal_land = pd.read_csv(r'https://raw.githubusercontent.com/JackOgozaly/SNAP_Ed/main/Data/tribal_land.csv')

# Merge the tribal land data with the state_data DataFrame based on the 'STATEFP' column
state_data = pd.merge(state_data, tribal_land,
                      how='left',
                      left_on='state',
                      right_on='STATEFP')

# Drop the 'STATEFP' column from the merged DataFrame
state_data = state_data.drop(['STATEFP'], axis=1)

# Create a subset DataFrame 'eligible_df2' containing 'Income_Limit' and ' st' columns from 'eligibility_df'
eligible_df2 = eligibility_df[['Income_Limit', ' st']]

# Merge the 'eligible_df2' DataFrame with the 'state_data' DataFrame based on the 'state' column
state_data = pd.merge(state_data, eligible_df2,
                      how='left',
                      left_on='state',
                      right_on=' st')

# Drop the ' st' column from the merged DataFrame
state_data = state_data.drop([' st'], axis=1)


# Read data from an Excel file hosted on the USDA website
lila_data = pd.read_excel(r'https://www.ers.usda.gov/webdocs/DataFiles/80591/FoodAccessResearchAtlasData2019.xlsx?v=6742.7', sheet_name='Food Access Research Atlas')

# Group and aggregate data by 'State', 'County', and 'Urban' columns, summing 'TractSNAP' and 'Pop2010' columns
lila_summary = lila_data.groupby(['State', 'County', 'Urban'])[['TractSNAP', 'Pop2010']].sum().reset_index(drop=False)

# Replace 'Urban' values 0 and 1 with 'Rural' and 'Urban' labels
lila_summary['Urban'] = lila_summary['Urban'].replace({0: 'Rural', 1: "Urban"})

# Pivot the 'lila_summary' DataFrame to have 'State' as the index and 'Urban' as columns
lila_summary = lila_summary.pivot_table(index=['State'], columns=['Urban'], values=['TractSNAP', 'Pop2010'], aggfunc='sum').reset_index(drop=False)

# Sort and rename columns
lila_summary = lila_summary.sort_index(axis=1, level=1)
lila_summary.columns = [f'{x}_{y}' for x, y in lila_summary.columns]
lila_summary = lila_summary.rename(columns={'State_': 'state_name'})

# Merge 'lila_summary' DataFrame with 'state_fips' based on 'state_name'
lila_summary = pd.merge(lila_summary, state_fips,
                        how='left',
                        left_on='state_name',
                        right_on='stname')

# Drop unnecessary columns from 'lila_summary'
lila_summary = lila_summary.drop(['stname', ' stusps'], axis=1)

# Merge 'state_data' DataFrame with 'lila_summary' based on 'state' column
state_data = pd.merge(state_data, lila_summary,
                      how='left',
                      left_on='state',
                      right_on=' st')

# Drop the ' st' column from 'state_data'
state_data = state_data.drop([' st'], axis=1)

# Save the final 'state_data' DataFrame to a CSV file
state_data.to_csv(r'/Users/jackogozaly/Desktop/Python_Directory/snaped_071923.csv',
                  index=False)
