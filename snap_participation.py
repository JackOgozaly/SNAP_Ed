#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 15:42:45 2023

@author: jackogozaly
"""


import pandas as pd

year_list = [2018, 2019, 2021]


df_list = []
for year in year_list:
    df = pd.read_json(f'https://api.census.gov/data/{year}/acs/acs5/subject?get=NAME,S2201_C01_001E,S2201_C01_021E&for=county:*&in=state:*')
    df.columns = df.iloc[0]
    df = df.drop(0, axis=0)
    df.columns = ['county_name', 'total_households', 'receiving_snap', 'state_code', 'county_code']
    df['Year'] = year
    df_list.append(df)
    


all_df = pd.concat(df_list)

all_df.to_csv(r'/Users/jackogozaly/Desktop/Python_Directory/snap_participation.csv', index=False)