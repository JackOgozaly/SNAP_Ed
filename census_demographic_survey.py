import pandas as pd
import numpy as np

'''

https://data.census.gov/table?q=DP02&g=0100000US$0400000,$0500000&tid=ACSDP1Y2021.DP02


'''



lila = pd.read_excel(r'C:\Users\jack.ogozaly\Downloads\FoodAccessResearchAtlasData2019 (1).xlsx', 
                     sheet_name = 'Food Access Research Atlas')



#%%


col_list = lila.columns
sub_lila = lila[['PovertyRate', 'TractSNAP', 'CensusTract', 'State', 'County', 'Urban', 'Pop2010']]


#%%


raw_data = pd.read_csv(r'C:\Users\jack.ogozaly\Downloads\ACSDP1Y2021.DP02-2023-03-02T162704.csv')

#%%


df = raw_data.copy()

df = df.drop(2, axis=0)

col_list = list(df.columns)


start = col_list.index('Alabama!!Estimate')
end = col_list.index('Puerto Rico!!Percent Margin of Error')

df = df.drop(df.iloc[:, start:end], axis=1)

col_list = df.columns


estimate_cols = [s for s in col_list if "Estimate" in s]
estimate_df = df[['Label (Grouping)'] + estimate_cols]
estimate_df = estimate_df.T
estimate_df = estimate_df.reset_index(drop=False)
estimate_df.columns = estimate_df.iloc[0]
estimate_df = estimate_df.drop(0, axis=0)
estimate_df = estimate_df.dropna(axis=1, how= "all")
estimate_df['Label (Grouping)'] = estimate_df['Label (Grouping)'].str.replace('!!Estimate', '')
estimate_df[['County', 'State']] = estimate_df['Label (Grouping)'].str.split(',', expand= True)

#Shift column order
first_column = estimate_df.pop('County')
estimate_df.insert(0, 'County', first_column)
second_column = estimate_df.pop('State')
estimate_df.insert(1, 'State', second_column)
estimate_df = estimate_df.drop('Label (Grouping)', axis = 1)


#To lowercase
estimate_df['County'] = estimate_df['County'].str.lower().str.strip()
estimate_df['State'] = estimate_df['State'].str.lower().str.strip()



fips = pd.read_csv('https://raw.githubusercontent.com/kjhealy/us-county/master/data/census/fips-by-state.csv',  encoding='unicode_escape')
fips_state = pd.read_csv('https://gist.githubusercontent.com/dantonnoriega/bf1acd2290e15b91e6710b6fd3be0a53/raw/11d15233327c8080c9646c7e1f23052659db251d/us-state-ansi-fips.csv',  encoding='unicode_escape')

print(fips_state.columns)

fips_state[' stusps'] = fips_state[' stusps'].str.strip()


fips = pd.merge(fips, fips_state,
                left_on = 'state',
                right_on = ' stusps',
                how = 'left')


fips.columns = ['FIPS', 'County', 'state_abv', 'State', 'state_code', 'stusps']


fips['County'] = fips['County'].str.lower().str.strip()
fips['State'] = fips['State'].str.lower().str.strip()


county_df = pd.merge(fips,
                     estimate_df,
                     how= 'right',
                     left_on = ['State', 'County'],
                     right_on = ['State', 'County'])

county_df = county_df.replace('N', np.nan)


for col in county_df.columns:
    print(f"'{col}',")



#%%
county_df.columns = county_df.columns.str.strip()




#%%


test = county_df[['Total population']]


#%%
county_df.columns = 

[
 
 'FIPS',
 'County',
 'state_abv',
 'State',
 'state_code',
 'stusps',
 'Total households',
 'With children of the householder under 18 years',
 'Cohabiting couple household',
 'With children of the householder under 18 years',
 'Male householder, no spouse/partner present',
 'With children of the householder under 18 years',
 'Householder living alone',
 '65 years and over',
 'Female householder, no spouse/partner present',
 'With children of the householder under 18 years',
 'Householder living alone',
 '65 years and over',
 'Households with one or more people under 18 years',
 'Households with one or more people 65 years and over',
 'Average household size',
 'Average family size',
 'Population in households',
 'Householder',
 'Spouse',
 'Unmarried partner',
 'Child',
 'Other relatives',
 'Other nonrelatives',
 'Males 15 years and over',
 'Never married',
 'Now married, except separated',
 'Separated',
 'Widowed',
 'Divorced',
 'Females 15 years and over',
 'Never married',
 'Now married, except separated',
 'Separated',
 'Widowed',
 'Divorced',
 'Number of women 15 to 50 years old who had a birth in the past 12 months',
 'Unmarried women (widowed, divorced, and never married)',
 'Per 1,000 unmarried women',
 'Per 1,000 women 15 to 50 years old',
 'Per 1,000 women 15 to 19 years old',
 'Per 1,000 women 20 to 34 years old',
 'Per 1,000 women 35 to 50 years old',
 'Number of grandparents living with own grandchildren under 18 years',
 'Grandparents responsible for grandchildren',
 'Less than 1 year',
 '1 or 2 years',
 '3 or 4 years',
 '5 or more years',
 'Number of grandparents responsible for own grandchildren under 18 years',
 'Who are female',
 'Who are married',
 'Population 3 years and over enrolled in school',
 'Nursery school, preschool',
 'Kindergarten',
 'Elementary school (grades 1-8)',
 'High school (grades 9-12)',
 'College or graduate school',
 'Population 25 years and over',
 'Less than 9th grade',
 '9th to 12th grade, no diploma',
 'High school graduate (includes equivalency)',
 'Some college, no degree',
 'Associate's degree',
 'Bachelor's degree',
 'Graduate or professional degree',
 'High school graduate or higher',
 'Bachelor's degree or higher',
 'Civilian population 18 years and over',
 'Civilian veterans',
 'Total Civilian Noninstitutionalized Population',
 'With a disability',
 'Under 18 years',
 'With a disability',
 '18 to 64 years',
 'With a disability',
 '65 years and over',
 'With a disability',
 'Population 1 year and over',
 'Same house',
 'Different house (in the U.S. or abroad)',
 'Different house in the U.S.',
 'Same county',
 'Different county',
 'Same state',
 'Different state',
 'Abroad',
 'Total population',
 'Native',
 'Born in United States',
 'State of residence',
 'Different state',
 'Born in Puerto Rico, U.S. Island areas, or born abroad to American parent(s)',
 'Foreign born',
 'Foreign-born population',
 'Naturalized U.S. citizen',
 'Not a U.S. citizen',
 'Population born outside the United States',
 'Native',
 'Entered 2010 or later',
 'Entered before 2010',
 'Foreign born',
 'Entered 2010 or later',
 'Entered before 2010',
 'Foreign-born population, excluding population born at sea',
 'Europe',
 'Asia',
 'Africa',
 'Oceania',
 'Latin America',
 'Northern America',
 'Population 5 years and over',
 'English only',
 'Language other than English',
 'Speak English less than "very well"',
 'Spanish',
 'Speak English less than "very well"',
 'Other Indo-European languages',
 'Speak English less than "very well"',
 'Asian and Pacific Islander languages',
 'Speak English less than "very well"',
 'Other languages',
 'Speak English less than "very well"',
 'Total population',
 'American',
 'Arab',
 'Czech',
 'Danish',
 'Dutch',
 'English',
 'French (except Basque)',
 'French Canadian',
 'German',
 'Greek',
 'Hungarian',
 'Irish',
 'Italian',
 'Lithuanian',
 'Norwegian',
 'Polish',
 'Portuguese',
 'Russian',
 'Scotch-Irish',
 'Scottish',
 'Slovak',
 'Subsaharan African',
 'Swedish',
 'Swiss',
 'Ukrainian',
 'Welsh',
 'West Indian (excluding Hispanic origin groups)',
 'Total households',
 'With a computer',
 'With a broadband Internet subscription'
 
 
 
 
 
 
 ]


#%%

for col in county_df.columns:
    print(f"'{col}',")





#%%
#col_list2 = county_df.columns

pd.set_option('display.max_rows', None)
pd.options.display.max_columns = None
pd.set_option('display.expand_frame_repr', False)

print(county_df.columns)















#%%
fips = pd.read_html('https://en.wikipedia.org/wiki/List_of_United_States_FIPS_codes_by_county')
fips = fips[1]
fips.columns = ['FIPS', 'County', 'State']
fips['County'] = fips['County'].str.lower()
fips['State'] = fips['State'].str.lower()

fips['County'] = fips['County'].str.partition('[')


#%%
fips['County'] = fips['County'].str.replace('[a]', '', regex=False)
fips['County'] = fips['County'].str.replace('[b]', '', regex=False)
fips['County'] = fips['County'].str.replace('[c]', '', regex=False)





#%%
df = df.melt(id_vars= 'Label (Grouping)')



#%%
:, 1:69