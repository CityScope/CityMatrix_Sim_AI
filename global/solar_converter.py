'''
Filename: solar_converter.py
Author: kalyons11 <mailto:kalyons@mit.edu>
Created: 2017-06-07 21:40:00
Last modified by: kalyons11
Description:
    - Quick script to convert raw text data to pickle file containing solar radiation linear regression model.
        NOTE: This script did not work as expected. Keeping for reference.
TODO:
    - None at this time.
'''

# Imports
import os
import pandas as pd
import pickle
from sklearn import linear_model

# Configurations
RAW_TEXT_FILENAME = '../../../data/raw_solar_weights.txt'
# OUTPUT_MODEL_FILENAME = '../CityPrediction/model_files/solar_model.pkl'

print("Starting solar conversion process.")

# Load text file as pandas dataframe
df = pd.read_table(RAW_TEXT_FILENAME, header = None, sep = ',')
# [1225 rows x 25 columns]

# Get the weight matrix associated with this data
weights = df.as_matrix()
# (1225, 25)
print(weights)

'''

# Create lin reg model with these weights
reg = linear_model.LinearRegression()
reg.coef_ = weights

# Pickle it
pickle.dump(reg, open(OUTPUT_MODEL_FILENAME, 'wb'))

print("Process complete. Solar model pickle file saved at {}.".format(os.path.abspath(OUTPUT_MODEL_FILENAME)))

'''

print('Process complete.')