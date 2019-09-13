#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Capital One

Airbnb & Zillow Data Challenge

@author: Xiaojun Yao
"""

import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import numpy as np


class Data_cleaning:
    def airbnb_cleaning(self, df):
        """ Data cleaning for the dataset provided by Airbnb
        Including filtering, subsetting, formatting, enaming and dealing with missing values"""
        
        # 1. Subset the dataframe with valuable columns
        df = df[['bedrooms','zipcode','price','neighbourhood_group_cleansed',
                      'neighbourhood_cleansed']] 
        
        # 2. Subset 2-bedrooms properties  
        revenue = df.loc[df['bedrooms']==2]
        
        # 3. Dealing with missing value
        revenue = revenue.dropna().reset_index(drop=True)
            # 'zipcode' has 50 missing values count for 0.0077 of total properties 
            # it can be assumed to have mirror effect on total result, so remove them.
        
        # 4. Format data into desired data type and fill missing values with -1
        revenue['bedrooms'] = revenue['bedrooms'].map(lambda x: int(float(x))) 
        revenue['price'] = revenue['price'].map(lambda x: int(float(str(x)[1:].replace(',',''))))
        revenue['zipcode'] = revenue['zipcode'].map(lambda x: int(float(str(x)[:5]))) # 5 digit zipcode
        
        # 5. Rename columns
        revenue.columns = ['bedrooms','zipcode','price','boroughs',
                           'neighbourhoods']
        
        # 6. Remove bedrooms columns because all properties have 2-bedrooms
        revenue = revenue.drop(['bedrooms'], axis=1).reset_index(drop=True)
        
        # 7. Remove duplicated properties and keep median price. 
        revenue = revenue.groupby(['zipcode','boroughs','neighbourhoods']
                                    ,as_index=False)['price'].median()
        
        revenue = revenue.reset_index(drop=True)
        
        # 8. Calculate NOI (Annual Net Operating Income) assuming 75% occupancy rate
        def noi_calculator(arr):
            """ calculate NOI by multiplying 'price'/night with 75% of a year """
            return np.multiply(arr,365*0.75) # assume 365 days/year
        
        revenue['Net_Operating_Income'] = revenue[['price']].apply(noi_calculator).astype(int)
        
        # 9. Save the table to local
        revenue.to_csv('Output/XYAO_revenue.csv')
        
        # 10. Return cleaned dataframe
        return revenue
    
    def zillow_cleaning(self, df):
        """ Data cleaning for the dataset provided by Zillow
        Including filtering, subsetting, formatting and renaming. """
    
        # 1. Subset with needed columns 
        cost = df[['RegionName','2017-06']]
        
        # 2. Rename columns
        cost.columns = ['zipcode','cost']
        
        # 3. Save the table to local
        cost.to_csv('Output/XYAO_cost.csv')
 
        # 4. return result
        return cost

    
    def profit_df(self, revenue, cost):
        
        # 1. Merge revenue and cost dataframe 
        profit = revenue.merge(cost,left_on='zipcode',right_on = 'zipcode',how='left')

        # 3. Calculate ROI / Capitalization Rate (percentage% as unit)
        try:
            profit['Return_On_Investment'] = (profit['Net_Operating_Income']/profit['cost']).round(4)
        except:
            profit['Return_On_Investment'] = np.nan # cost has missing value: cannot be divided
        
        # 4. Save the full table to local
        profit.to_csv('Output/XYAO_profit.csv')
        
        # 5. Return profit dataframe for visualization 
        return profit
    











    
    
    
    
    
    