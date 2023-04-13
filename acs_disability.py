#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 11:10:53 2023

@author: jackogozaly
"""



import pandas as pd

subject_cols = pd.read_html('https://api.census.gov/data/2021/acs/acs5/subject/groups/S1810.html')[0]


disability_cols = subject_cols[~(subject_cols['Name'].str[-2:]=='MA')]
disability_cols = disability_cols[~(disability_cols['Name'].str[-2:]=='EA')]
disability_cols = disability_cols[~(disability_cols['Name'].str[-1:]=='M')].reset_index(drop=True)
disability_cols = disability_cols[(disability_cols['Label'].str.contains("With a disability", regex=False))].reset_index(drop=True)
disability_cols = disability_cols.iloc[:18]
disability_cols = disability_cols[['Name', 'Label']]




my_dict = dict(zip(disability_cols['Name'],disability_cols['Label']))
api_list = list(disability_cols['Name'].str.strip())

api_df = pd.read_json(f"https://api.census.gov/data/2021/acs/acs5/subject?get=NAME,{','.join(api_list)}&for=state:*")
api_df.columns = api_df.iloc[0]
api_df = api_df.drop(0, axis=0)


api_df.columns = ['State', 'total_disabled', 'total_disabled_male', 'total_disabled_female', 'total_disabled_white',
                  'total_disabled_black', 'total_disabled_indian', 'total_disabled_asian', 'total_disabled_hawaiian',
                  'total_disabled_other_race', 'total_disabled_two_or_more', 'total_disabled_not_hispanic', 'total_disabled_hispanic',
                  'total_disaled_under_5', 'total_disabled_5_17', 'total_disabled_18_34', 'total_disabled_35_64', 
                  'total_disabled_65_74', 'total_disabled_75+', 'STATEFP']

api_df.to_csv(r'/Users/jackogozaly/Desktop/Python_Directory/2021_acs_disability.csv', index=False)
