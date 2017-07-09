'''
Filename: predictor.py
Author: Kevin <mailto:kalyons@mit.edu>
Created: 2017-06-01 20:17:36
Last modified by: kalyons11
Description:
    - Generic black box ML predictor that takes in a city and runs the necessary ML predictions on it for
    all features. Right now, these features are traffic, wait (not right now) AND solar radiation.
TODO:
    - None at this time.
'''

import sys

import numpy as np
np.set_printoptions(threshold=np.nan)
sys.path.extend(['../global/'])

from utils import *
from cityiograph import get_features

log = logging.getLogger('__main__')

# Load traffic model file
traffic_model = pickle.load(open(config.LINEAR_MODEL_FILENAME, 'rb'))
solar_model = pickle.load(open(config.SOLAR_MODEL_FILENAME, 'rb'))


def predict(input_city):
    '''Generic traffic/solar predictor.

    Args:
        input_city (cityiograph.City): -

    Returns:
        cityiograph.City: new city instance with traffic ML prediction scores applied
    '''
    # Make running copy of city
    output_city = input_city.copy()

    # Let's run traffic first
    # Extract feature matrix from this city
    traffic_features = get_features(input_city, 'traffic')

    # Make traffic prediction using linear model
    traffic_output = traffic_model.predict([traffic_features])[
        0]  # Type = np array (512, )

    # Write prediction back to the cityiograph.City structure
    output_city.update_values(data_array=traffic_output, mode='traffic')

    # Now, let's run solar
    # Extract feature matrix from this city
    solar_features = get_features(input_city, 'solar')

    # Make solar prediction using linear model
    solar_output = solar_model.predict([solar_features])[
        0]  # Type = np array (256, )

    # Write prediction back to the cityiograph.City structure
    output_city.update_values(data_array=solar_output, mode='solar')

    return output_city
