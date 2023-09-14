'''
Tribal Land Calculation

For this section, we want to grab the shapefile for tribal organizations in the US
and US State shapefiles. From there, we'll find where they overlap and what 
percent of each state is tribal.
'''

# Import necessary libraries
import geopandas as gpd
import pandas as pd
import warnings

# Ignore warnings to keep the output clean
warnings.filterwarnings('ignore')

# Load the Tribal Organizations Shapefile from the Census Bureau website
tribal_maps = gpd.read_file('https://www2.census.gov/geo/tiger/TIGER2020/AIANNH/tl_2020_us_aiannh.zip')

# Load the State map shapefiles from the Census Bureau website
state_maps = gpd.read_file('https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_500k.zip')

# Get the overlay of our state map and tribal shapefiles
merged = gpd.overlay(state_maps, tribal_maps, how='intersection')

# Sum up tribal land by state
state_land = merged.dissolve(by='STATEFP')

# Grab the area of tribal land within each state
indian_area = (state_land.area).reset_index(drop=False)
indian_area.columns = ['STATEFP', 'indian_area']

# Grab the total area in a state
state_area = state_maps.dissolve(by='STATEFP').area.reset_index(drop=False)
state_area.columns = ['STATEFP', 'state_area']

# Join our dataframes together
area_df = pd.merge(indian_area, state_area,
                   how='outer',
                   on='STATEFP')

# Create our percent calculation
area_df['Percent_Tribal_Land'] = area_df['indian_area'] / area_df['state_area']