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

import sys, numpy as np
np.set_printoptions(threshold = np.nan)
sys.path.extend(['../global/'])
import config
from utils import *
import solar_regression as solar
log = logging.getLogger('__main__')

# Load traffic model file
traffic_model = pickle.load(open(LINEAR_MODEL_FILENAME, 'rb'))
solar_model = pickle.load(open(SOLAR_MODEL_FILENAME), 'rb')

def predict(input_city):
    '''Generic traffic/solar predictor.
    
    Args:
        input_city (cityiograph.City): -
    
    Returns:
        cityiograph.City: new city instance with traffic ML prediction scores applied
    '''
    # Let's run traffic first
    # Extract feature matrix from this city
    features = get_features(input_city, 'traffic')

    # Make traffic prediction using linear model
    traffic_output = traffic_model.predict([ features ])[0] # Type = np array, 1 x 512

    # Write prediction back to the cityiograph.City structure
    traffic_city = input_city.update_values(data_array = traffic_output, mode = 'traffic')

    # Now, let's run solar
    # Extract feature matrix from this city
    features = get_features(traffic_city, 'solar')

    # Make solar prediction using linear model
    solar_output = solar_model.predict([ features ])[0] # Type = np array, 1 x 256
    print(solar_output.shape)
    sys.exit(0)

    # Write prediction back to the cityiograph.City structure
    final_city = traffic_city.update_values(data_array = solar_output, mode = 'solar')

    return final_city