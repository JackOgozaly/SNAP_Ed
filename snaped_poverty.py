#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 10:59:05 2023

@author: jackogozaly
"""

import pandas as pd

subject_cols = pd.read_html('https://api.census.gov/data/2021/acs/acs5/subject/groups/S1701.html')[0]

poverty_cols = subject_cols[~(subject_cols['Name'].str[-2:]=='MA')]
poverty_cols = poverty_cols[~(poverty_cols['Name'].str[-2:]=='EA')]
poverty_cols = poverty_cols[~(poverty_cols['Name'].str[-1:]=='M')].reset_index(drop=True)
poverty_cols = poverty_cols[(poverty_cols['Label'].str.contains("Below", regex=False))].reset_index(drop=True)
poverty_cols = poverty_cols.iloc[:21]
poverty_cols = poverty_cols[['Name', 'Label']]
poverty_cols.loc[len(poverty_cols.index)] = ['S1701_C01_001E', 'Estimate!!Total!!Population for whom poverty status is determined']


my_dict = dict(zip(poverty_cols['Name'],poverty_cols['Label']))


api_list = list(poverty_cols['Name'].str.strip())



api_df = pd.read_json(f"https://api.census.gov/data/2021/acs/acs5/subject?get=NAME,{','.join(api_list)}&for=state:*")


api_df.columns = api_df.iloc[0]
api_df = api_df.drop(0, axis=0)

numeric_cols = [col for col in api_df if col.startswith('S1701')]
api_df[numeric_cols] = api_df[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

clean_df = api_df[['NAME', 'S1701_C01_001E', 'S1701_C02_001E', 'S1701_C02_003E', 'S1701_C02_004E', 'S1701_C02_006E',
                   'S1701_C02_009E', 'S1701_C02_011E', 'S1701_C02_012E',
                   'S1701_C02_013E', 'S1701_C02_014E', 'S1701_C02_015E', 
                   'S1701_C02_016E', 'S1701_C02_017E', 'S1701_C02_020E',
                   'S1701_C02_021E']].copy()


clean_df.columns = ['State', 'total_pop', 'total_povety', 'under_5', '5_17', '18_64', '60+', 'male_poverty',
                    'female_poverty', 'white_poverty', 'black_poverty', 'indian_poverty',
                    'asian_poverty', 'hawaiian_poverty', 'hispanic_poverty',
                    'white_nonhispanic']

race_cols = ['white_poverty', 'black_poverty', 'indian_poverty', 'asian_poverty',
             'hawaiian_poverty']


clean_df['poverty_percent'] = clean_df['total_povety'] / clean_df['total_pop']
clean_df['male_percent'] = clean_df['male_poverty'] / clean_df['total_povety']
clean_df['female_percent']  = 1 - clean_df['male_percent']
clean_df['white_percent'] = clean_df['white_poverty'] / clean_df[race_cols].sum(axis=1)
clean_df['black_percent'] = clean_df['black_poverty'] / clean_df[race_cols].sum(axis=1)
clean_df['indian_percent'] = clean_df['indian_poverty'] / clean_df[race_cols].sum(axis=1)
clean_df['asian_percent'] = clean_df['asian_poverty'] / clean_df[race_cols].sum(axis=1)
clean_df['hawaiian_percent'] = clean_df['hawaiian_poverty'] / clean_df[race_cols].sum(axis=1)
clean_df['hispanic_percent'] = clean_df['hispanic_poverty'] / clean_df['total_povety']
clean_df['white_nonhispanic_percent'] = clean_df['white_nonhispanic'] / clean_df['total_povety']
clean_df['under_5_percent'] = clean_df['under_5'] / clean_df['total_povety']
clean_df['5_17_percent'] = clean_df['5_17'] / clean_df['total_povety']
clean_df['18_64_percent'] = clean_df['18_64'] / clean_df['total_povety']
clean_df['60+_percent'] = clean_df['60+'] / clean_df['total_povety']



clean_df.to_csv(r'/Users/jackogozaly/Desktop/Python_Directory/2021_acs_poverty.csv', index=False)

