'''
Filename: predictor.py
Author: Kevin <mailto:kalyons@mit.edu>
Created: 2017-06-01 20:17:36
Last modified by: kalyons11
Last modified time: 2017-06-11 00:19:17
Description:
    - Generic black box ML predictor that takes in a city and runs the necessary ML predictions on it for
    all features. Right now, these features are traffic, wait (not right now) AND solar radiation.
TODO:
    - Get solar model working, with support of Alex. Try to keep as much of his code intact as possible!
'''

# Get our key utils script
import sys; sys.path.extend(['../global/', '../MachineLearning/'])
import config
from utils import *
import solar_regression as solar
log = logging.getLogger('__main__')

# Load traffic model file
traffic_model = pickle.load(open(LINEAR_MODEL_FILENAME, 'rb'))

def traffic_predict(city):
    '''
    Generic traffic predictor.
    Input:     city - instance of cityiograph.City to be predicted
    Output: out_city - instance of cityiograph.City, with updated cell data values for traffic after lin reg
    '''

    # Extract feature matrix from this city
    features = get_features(city)

    # Make traffic prediction using linear model and trim negative values
    # Taken https://stackoverflow.com/questions/3391843/how-to-transform-negative-elements-to-zero-without-a-loop
    traffic_output = traffic_model.predict([ features ])[0].clip(min = 0) # Type = np array, 1 x 512

    # Only care about traffic values right now
    result = features; result[::2] = traffic_output[::2]

    # Write prediction back to the cityiograph.City structure and return
    return output_to_city(city, result)

def solar_predict(new_city, prev, locations):
    '''
    Generic solar radiation predictor with accumulation functionality.
    Input:     city - instance of cityiograph.City to be predicted
            prev - instance of cityiograph.City that represents our prior state
            locations - list of (x, y) cell coordinates where we need to run solar analysis
    Output: out_city - instance of cityiograph.City, with updated cell data values for solar after we apply deltas
    '''

    # Keep a running accumulated city
    result = new_city

    # For every location, update values based on solar radiation deltas predictor
    for x, y in locations:
        result = solar.update_city(prev, result, x, y)

    return result

def predict(city, change_key, change_data, force_predict = config.FORCE_PREDICTION):
    '''
    Black box predictor function for our machine learning.
    Input:     city - instance of cityiograph.City to be predicted
            change_key - instance of utils.CityChange - descibes the change made
            change_value - arguments telling us what makes this new city unique from the previous
            force_predict - default False value; used for AI predictor
    Output: result_city - instance of cityiograph.City, with updated cell data values
    '''

    if not change_data and force_predict:
        # Same city, just want traffic update
        return traffic_predict(city)

    if change_key == CityChange.FIRST or city.startFlag == 1:
        # First city, just want traffic update
        return traffic_predict(city)

    # Parse our change data
    #RZ 170614 print(change_data)
    l, prev = tuple(change_data)
        
    # First, do full traffic prediction
    current = traffic_predict(city)
    locations = []

    if change_key == CityChange.DENSITY:
        indices = l # List of indices in density array where we have a change - likely length 1
        # Find locations with that density value in PREVIOUS *** city
        for i in indices:
            for c in prev.cells.values():
                if c.type_id == i:
                    locations.append((c.x, c.y))

    elif change_key == CityChange.CELL:
        locations = l # Already have changed locations from data

    return solar_predict(current, prev, locations)