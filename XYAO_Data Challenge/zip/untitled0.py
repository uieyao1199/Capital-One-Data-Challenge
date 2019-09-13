#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 14:10:58 2019

@author: uieyao
"""

import pandas as pd
import warnings
warnings.filterwarnings("ignore")

###############################################################################

# 1. Data Quality 

###############################################################################

file_1 = '/Users/uieyao/Desktop/C1_Data Challenge/listings.csv'
airbnb = pd.read_csv(file_1) 

file_2 = '/Users/uieyao/Desktop/C1_Data Challenge/Zip_Zhvi_2bedroom.csv'
zillow = pd.read_csv(file_2) 


# Check airbnb dataset quality
airbnb.info()
airbnb.shape
airbnb.columns
airbnb.isnull().sum()


airbnb.price.unique()
airbnb.smart_location.unique()
airbnb.city.unique()
airbnb.state.unique()
airbnb.neighbourhood_group_cleansed.unique()
airbnb.neighbourhood_cleansed.unique()
airbnb.zipcode.unique()
airbnb.property_type.unique()
airbnb.room_type.unique()
airbnb.bedrooms.unique()
airbnb.bathrooms.unique()

# Check zillow dataset quality
zillow.info()
zillow.shape
zillow.columns
zillow.isnull().sum()


zillow.price.unique()
zillow.smart_location.unique()
zillow.city.unique()
zillow.state.unique()
zillow.neighbourhood_group_cleansed.unique()
zillow.neighbourhood_cleansed.unique()
zillow.zipcode.unique()
zillow.property_type.unique()
zillow.room_type.unique()
zillow.bedrooms.unique()
zillow.bathrooms.unique()

###############################################################################

# 2. Data Cleaning 

###############################################################################
# Final Dataframe 
revenue = revenue.loc[revenue['bedrooms']==2]



























