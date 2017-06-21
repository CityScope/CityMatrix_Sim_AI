'''
Filename: predictor.py
Author: Kevin <mailto:kalyons@mit.edu>
Created: 2017-06-01 20:17:36
Last modified by: kalyons11
Last modified time: 2017-06-20 23:18:44
Description:
    - Generic black box ML predictor that takes in a city and runs the necessary ML predictions on it for
    all features. Right now, these features are traffic, wait (not right now) AND solar radiation.
TODO:
    - None at this time.
'''

# Get our key utils script
import sys, numpy as np
np.set_printoptions(threshold = np.nan)
sys.path.extend(['../global/'])
import config
from utils import *
import solar_regression as solar
log = logging.getLogger('__main__')

# Load traffic model file
traffic_model = pickle.load(open(LINEAR_MODEL_FILENAME, 'rb'))

def traffic_predict(input_city):
    '''Generic traffic predictor.
    
    Args:
        input_city (cityiograph.City): -
    
    Returns:
        cityiograph.City: new city instance with traffic ML prediction scores applied
    '''
    # Extract feature matrix from this city
    features = get_features(input_city)

    # Make traffic prediction using linear model and trim negative values
    # Taken https://stackoverflow.com/questions/3391843/how-to-transform-negative-elements-to-zero-without-a-loop
    traffic_output = traffic_model.predict([ features ])[0].clip(min = 0) # Type = np array, 1 x 512

    # Only care about traffic values right now
    result_data = features
    result_data[::2] = traffic_output[::2]

    # Write prediction back to the cityiograph.City structure and return
    new_city = input_city.update_traffic_wait_values(result_data)

    return new_city

def solar_predict(input_city, previous_city_heights, locations):
    '''Generic solar radiation predictor with accumulation functionality.
    
    Args:
        input_city (cityiograph.City): incoming city, likely already has traffic values - now need solar
        previous_city_heights (dict): mapping (x , y) -> height on the PREVIOUS city state
        locations (list): list of (x , y) tuples that need a solar predicton centered there
    
    Returns:
        TYPE: Description
    
    '''
    output_city = input_city.copy()

    # For every location, update values based on solar radiation deltas predictor
    for x, y in locations:
        solar.update_city(output_city, previous_city_heights, x, y)

    return output_city

def predict(input_city, previous_city_heights, move_type, move_data):
    '''Black box predictor function for our machine learning.
    
    Args:
        input_city (cityiograph.City): -
        previous_city_heights (dict): mapping (x , y) -> height on the PREVIOUS city state
        move_type (str): at this point, either DENSITY or CELL
        move_data (list): either list of (x , y) tuples where a type_id has changed OR list of indices in
            density array that have a new value
    
    Returns:
        TYPE: Description
    '''
    # First, do full traffic prediction
    traffic_city = traffic_predict(input_city)

    # Now, figure out locations where we should apply solar prediction
    locations = []

    if move_type == "DENSITY":
        indices = move_data # List of indices in density array where we have a change - likely length 1
        # Find locations with that density value
        for i in indices:
            for c in input_city.cells.values():
                if c.type_id == i:
                    locations.append(c.get_pos())

    elif move_type == "CELL":
        locations = move_data # Already have changed locations from data

    return solar_predict(traffic_city, previous_city_heights, locations)