'''
This python script calls the ACS microdata and queries it for the total population by:
    
    age
    Race
    Sex
    Household Language
    Hispanic/ Not Hispanic
    

From there, we have to pivot the data into a usable format for our analysis.

'''

#General python data shennanigans
import pandas as pd
#For doing some of our calculations
import numpy as np
from functools import reduce


#_______API Call________
#If we do read json we can just slap this into a dataframe to start
api_df = pd.read_json("https://api.census.gov/data/2021/acs/acs5/pums?get=SEX,RAC1P,POVPIP,HISP,AGEP,HHL,PWGTP&for=state:*")

#JSON file format sucks so we have to reformat our columns
api_df.columns = api_df.iloc[0]
api_df = api_df.drop(0, axis=0)

#__________________ACS Microdata Remaps__________________________________

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

#Sex remape
sex = {"1": "Male",
      "2": "Female"}

#House hold language remap
HHL = {"3": "Other Indo-European languages",
      "0": "N/A (GQ/vacant)",
      "2": "Spanish",
      "1": "English Only",
      "4": "Asian and Pacific Island languages",
      "5": "Other Language"}



#____________185% of poverty level_________________________
'''
Some states set SNAP Eligibility at 185% of the poverty level so we'll start
by figuring out those numbers for states
'''

#Copy our api dataframe
df_185 = api_df.copy()

#Cast to numeric so we can filter our poverty % column
df_185['POVPIP'] = pd.to_numeric(df_185['POVPIP'])
df_185 = df_185[df_185['POVPIP'].between(0,185)]

#_____________Data remapping_________________________________
#Remap our race column
df_185['RAC1P'] = df_185['RAC1P'].replace(race)
#Rework our hispanic column to be a binary Y/N instead of every type of hispanic
df_185['HISP'] = np.where(df_185['HISP'] == '01', 'Not Spanish/Hispanic/Latino',
                        'Spanish/Hispanic/Latino')
#Remap household language
df_185['HHL'] = df_185['HHL'].replace(HHL)

#Remape sex
df_185['SEX'] = df_185['SEX'].replace(sex)

#For age, we want to transform it from a continuous variable into the buckets
#FNS is using
df_185['AGEP'] = pd.to_numeric(df_185['AGEP'])
df_185['Age_Group'] = np.where(df_185['AGEP'] < 5, 'less_than_5', np.NaN)
df_185['Age_Group'] = np.where(df_185['AGEP'].between(5, 17, inclusive= 'both'), '5_17', df_185['Age_Group'])
df_185['Age_Group'] = np.where(df_185['AGEP'].between(18, 59, inclusive= 'both'), '18_59', df_185['Age_Group'])
df_185['Age_Group'] = np.where(df_185['AGEP'] >= 60, 'greater_than_60', df_185['Age_Group'])
#Now that we have our buckets, drop the continuous variable
df_185 = df_185.drop('AGEP', axis = 1)


#Now, we want to aggregate our data and sum it up
df_185['PWGTP'] = pd.to_numeric(df_185['PWGTP'])
df_185 = df_185.groupby(['SEX', 'RAC1P', 'HISP', 'Age_Group', 'HHL', 'state'])['PWGTP'].sum().reset_index(drop=False)


#Pivot Values for sex and age
sex_age = df_185.pivot_table(index= ['state'], columns = ['SEX', 'Age_Group'], 
                        values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
sex_age = sex_age.sort_index(axis=1, level=1)
sex_age.columns = [f'{x}_{y}' for x,y in sex_age.columns]
sex_age = sex_age.rename(columns={'state_': 'state'})

#Race pivot
race_df = df_185.pivot_table(index= ['state'], columns = ['RAC1P'], 
                        values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
race_df = race_df.sort_index(axis=1, level=1)


#Hispanic pivot
hisp_df = df_185.pivot_table(index= ['state'], columns = ['HISP'], 
                        values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
hisp_df = hisp_df.sort_index(axis=1, level=1)


#Language Pivot
language_df = df_185.pivot_table(index= ['state'], columns = ['HHL'], 
                        values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
language_df = language_df.sort_index(axis=1, level=1)


dfList = [sex_age, race_df, hisp_df, language_df]
df_185 = reduce(lambda x, y: x.merge(y, on='state'), dfList)
df_185.columns = [x.lower() for x in df_185.columns]
df_185 = df_185.add_suffix('_185')


df_185.to_csv(r'/Users/jackogozaly/Desktop/Python_Directory/acs_185_df.csv', index=False)


#____________200% of poverty level_________________________
'''
Some states set SNAP Eligibility at 185% of the poverty level so we'll start
by figuring out those numbers for states
'''

#Copy our api dataframe
df_200 = api_df.copy()

#Cast to numeric so we can filter our poverty % column
df_200['POVPIP'] = pd.to_numeric(df_200['POVPIP'])
df_200 = df_200[df_200['POVPIP'].between(0,200)]

#_____________Data remapping_________________________________
#Remap our race column
df_200['RAC1P'] = df_200['RAC1P'].replace(race)
#Rework our hispanic column to be a binary Y/N instead of every type of hispanic
df_200['HISP'] = np.where(df_200['HISP'] == '01', 'Not Spanish/Hispanic/Latino',
                        'Spanish/Hispanic/Latino')
#Remap household language
df_200['HHL'] = df_200['HHL'].replace(HHL)

#Remape sex
df_200['SEX'] = df_200['SEX'].replace(sex)

#For age, we want to transform it from a continuous variable into the buckets
#FNS is using
df_200['AGEP'] = pd.to_numeric(df_200['AGEP'])
df_200['Age_Group'] = np.where(df_200['AGEP'] < 5, 'less_than_5', np.NaN)
df_200['Age_Group'] = np.where(df_200['AGEP'].between(5, 17, inclusive= 'both'), '5_17', df_200['Age_Group'])
df_200['Age_Group'] = np.where(df_200['AGEP'].between(18, 59, inclusive= 'both'), '18_59', df_200['Age_Group'])
df_200['Age_Group'] = np.where(df_200['AGEP'] >= 60, 'greater_than_60', df_200['Age_Group'])
#Now that we have our buckets, drop the continuous variable
df_200 = df_200.drop('AGEP', axis = 1)


#Now, we want to aggregate our data and sum it up
df_200['PWGTP'] = pd.to_numeric(df_200['PWGTP'])
df_200 = df_200.groupby(['SEX', 'RAC1P', 'HISP', 'Age_Group', 'HHL', 'state'])['PWGTP'].sum().reset_index(drop=False)


#Pivot Values for sex and age
sex_age = df_200.pivot_table(index= ['state'], columns = ['SEX', 'Age_Group'], 
                        values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
sex_age = sex_age.sort_index(axis=1, level=1)
sex_age.columns = [f'{x}_{y}' for x,y in sex_age.columns]
sex_age = sex_age.rename(columns={'state_': 'state'})

#Race pivot
race_df = df_200.pivot_table(index= ['state'], columns = ['RAC1P'], 
                        values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
race_df = race_df.sort_index(axis=1, level=1)


#Hispanic pivot
hisp_df = df_200.pivot_table(index= ['state'], columns = ['HISP'], 
                        values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
hisp_df = hisp_df.sort_index(axis=1, level=1)


#Language Pivot
language_df = df_200.pivot_table(index= ['state'], columns = ['HHL'], 
                        values = 'PWGTP', aggfunc= 'sum').reset_index(drop=False)
language_df = language_df.sort_index(axis=1, level=1)



dfList = [sex_age, race_df, hisp_df, language_df]

df_200 = reduce(lambda x, y: x.merge(y, on='state'), dfList)
df_200.columns = [x.lower() for x in df_200.columns]
df_200 = df_200.add_suffix('_200')


df_200.to_csv(r'/Users/jackogozaly/Desktop/Python_Directory/acs_200_df.csv', index=False)

