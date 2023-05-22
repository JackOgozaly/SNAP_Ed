import pandas as pd
import numpy as np
from functools import reduce

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

eligibility_df = pd.DataFrame.from_dict(eligibility_df, orient='index').reset_index(drop=False)
eligibility_df.columns = ['State', 'Income_Limit']

state_fips = pd.read_csv(r'https://gist.githubusercontent.com/dantonnoriega/bf1acd2290e15b91e6710b6fd3be0a53/raw/11d15233327c8080c9646c7e1f23052659db251d/us-state-ansi-fips.csv')


eligibility_df = pd.merge(eligibility_df, state_fips,
                          how = 'left',
                          left_on = 'State', 
                          right_on = 'stname')

eligibility_df = eligibility_df.dropna(subset= [' st'])


year_list = [2018, 2019, 2021]

df_list = []

for year in year_list:
    sub_api = pd.read_json(f"https://api.census.gov/data/{year}/acs/acs1/pums?get=SEX,RAC1P,POVPIP,HISP,DIS,AGEP,HHL,PWGTP&for=state:*")
    
    sub_api.columns = sub_api.iloc[0]
    sub_api = sub_api.drop(0, axis=0)

    sub_api['Year'] = year

    df_list.append(sub_api)


all_df = pd.concat(df_list)
all_df['POVPIP'] = pd.to_numeric(all_df['POVPIP'])




#Remap for race
race = {"3": "American Indian alone",
      "1": "White alone",
      "8": "Some Other Race alone",
      "6": "Asian alone",
      "9": "Two or More Races",
      "2": "Black or African American alone",
      "4": "Alaska Native alone",
      "7": "Native Hawaiian and Other Pacific Islander alone",
      "5": "American Indian and Alaska Native tribes specified; or American Indian or Alaska Native, not specified and no other races"}


#Disability remap
disability = {"1": "With a disability",
              "2": "Without a disability"
              }


#Sex remap
sex = {"1": "Male",
      "2": "Female"}

#House hold language remap
HHL = {"3": "Other Indo-European languages",
      "0": "N/A (GQ/vacant)",
      "2": "Spanish",
      "1": "English Only",
      "4": "Asian and Pacific Island languages",
      "5": "Other Language"}

pov_levels = list(eligibility_df['Income_Limit'].unique())


state_dfs = []

for pov in pov_levels:
    sub_df = all_df.copy()
    sub_df = sub_df[sub_df['POVPIP'].between(0,pov)]
    print(f"Rows in sub_df check -1: {len(sub_df)}")
    
    eligible_states = list(eligibility_df[eligibility_df['Income_Limit'] == pov][' st'].astype(int).unique())
    sub_df['state'] = sub_df['state'].astype(int)
    sub_df = sub_df[sub_df['state'].isin(eligible_states)]
    print(f"Rows in sub_df check 0: {len(sub_df)}")

    #_____________Data remapping_________________________________
    #Remap our race column
    sub_df['RAC1P'] = sub_df['RAC1P'].replace(race)
    #Rework our hispanic column to be a binary Y/N instead of every type of hispanic
    sub_df['HISP'] = np.where(sub_df['HISP'] == '01', 'Not Spanish/Hispanic/Latino',
                            'Spanish/Hispanic/Latino')
    #Remap household language
    sub_df['HHL'] = sub_df['HHL'].replace(HHL)

    #Remap sex
    sub_df['SEX'] = sub_df['SEX'].replace(sex)
    
    #Remap disability
    sub_df['DIS'] = sub_df['DIS'].replace(disability)

    #For age, we want to transform it from a continuous variable into the buckets
    #FNS is using
    sub_df['AGEP'] = pd.to_numeric(sub_df['AGEP'])
    sub_df['Age_Group'] = np.where(sub_df['AGEP'] < 5, 'less_than_5', np.NaN)
    sub_df['Age_Group'] = np.where(sub_df['AGEP'].between(5, 17, inclusive= 'both'), '5_17', sub_df['Age_Group'])
    sub_df['Age_Group'] = np.where(sub_df['AGEP'].between(18, 59, inclusive= 'both'), '18_59', sub_df['Age_Group'])
    sub_df['Age_Group'] = np.where(sub_df['AGEP'] >= 60, 'greater_than_60', sub_df['Age_Group'])
    #Now that we have our buckets, drop the continuous variable
    sub_df = sub_df.drop('AGEP', axis = 1)
    
    print(f"Rows in sub_df check 1: {len(sub_df)}")
    
    #Now, we want to aggregate our data and sum it up
    sub_df['PWGTP'] = pd.to_numeric(sub_df['PWGTP'])
    sub_df = sub_df.groupby(['SEX', 'RAC1P', 'HISP', 'Age_Group', 'HHL','DIS', 'Year', 'state'])['PWGTP'].sum().reset_index(drop=False)

    print(f"Rows in sub_df check 2: {len(sub_df)}")
    #Pivot Values for sex and age
    sex_age = sub_df.pivot_table(index= ['state', 'Year'], columns = ['SEX', 'Age_Group'], 
                            values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
    sex_age = sex_age.sort_index(axis=1, level=1)
    sex_age.columns = [f'{x}_{y}' for x,y in sex_age.columns]
    sex_age = sex_age.rename(columns={'state_': 'state', 'Year_': 'Year'})

    #Race pivot
    race_df = sub_df.pivot_table(index= ['state', 'Year'], columns = ['RAC1P'], 
                            values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
    race_df = race_df.sort_index(axis=1, level=1)

    #Disability Pivot
    dis_df = sub_df.pivot_table(index= ['state', 'Year'], columns = ['DIS'], 
                            values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
    dis_df = dis_df.sort_index(axis=1, level=1)

    #Hispanic pivot
    hisp_df = sub_df.pivot_table(index= ['state', 'Year'], columns = ['HISP'], 
                            values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
    hisp_df = hisp_df.sort_index(axis=1, level=1)


    #Language Pivot
    language_df = sub_df.pivot_table(index= ['state', 'Year'], columns = ['HHL'], 
                            values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
    language_df = language_df.sort_index(axis=1, level=1)


    dfList = [sex_age, race_df, hisp_df, language_df, dis_df]
    sub_df2 = reduce(lambda x, y: x.merge(y, on=['state', 'Year']), dfList)
    
    
    state_dfs.append(sub_df2)


#%%

state_data = pd.concat(state_dfs)


totaL_pop_list = []

for year in year_list:
    total_pop = pd.read_json(f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B01001_001E&for=state:*")
    
    total_pop.columns = total_pop.iloc[0]
    total_pop = total_pop.drop(0, axis=0)

    total_pop['Year'] = year

    totaL_pop_list.append(total_pop)


total_pop = pd.concat(totaL_pop_list)

total_pop = total_pop.rename(columns={'B01001_001E': 'total_pop'})

total_pop['state'] = total_pop['state'].astype(int)
total_pop['total_pop'] = total_pop['total_pop'].astype(int)
total_pop = total_pop.drop(['NAME'], axis=1 )


state_data = pd.merge(state_data, total_pop,
                      how = 'left',
                      left_on = ['state', 'Year'],
                      right_on = ['state', 'Year'])





tribal_land = pd.read_csv(r'https://raw.githubusercontent.com/JackOgozaly/SNAP_Ed/main/Data/tribal_land.csv')

state_data = pd.merge(state_data, tribal_land,
                      how = 'left',
                      left_on = 'state',
                      right_on = 'STATEFP')



state_data = state_data.drop(['STATEFP'], axis=1)



eligible_df2 = eligibility_df[['Income_Limit', ' st']]

state_data = pd.merge(state_data, eligible_df2,
                      how='left',
                      left_on = 'state',
                      right_on = ' st')


state_data = state_data.drop([' st'], axis = 1)



#%%



lila_data = pd.read_excel(r'https://www.ers.usda.gov/webdocs/DataFiles/80591/FoodAccessResearchAtlasData2019.xlsx?v=6742.7', sheet_name= 'Food Access Research Atlas')


#%%


lila_summary = lila_data.groupby(['State', 'County', 'Urban'])[['TractSNAP', 'Pop2010']].sum().reset_index(drop=False)

lila_summary['Urban'] = lila_summary['Urban'].replace({0: 'Rural', 1: "Urban"})


lila_summary = lila_summary.pivot_table(index= ['State'], columns = ['Urban'], 
                        values = ['TractSNAP', 'Pop2010'], aggfunc= 'sum').reset_index(drop=False)

lila_summary = lila_summary.sort_index(axis=1, level=1)
lila_summary.columns = [f'{x}_{y}' for x,y in lila_summary.columns]
lila_summary = lila_summary.rename(columns={'State_': 'state_name'})


lila_summary = pd.merge(lila_summary, state_fips,
                        how = 'left', 
                        left_on = 'state_name',
                        right_on = 'stname')


lila_summary = lila_summary.drop(['stname', ' stusps'], axis =1 )


state_data = pd.merge(state_data, lila_summary,
                      how = 'left',
                      left_on = 'state',
                      right_on = ' st')


state_data = state_data.drop([' st'], axis = 1)


state_data.to_csv(r'/Users/jackogozaly/Desktop/Python_Directory/snaped_050723.csv',
                  index=False)


#%%



