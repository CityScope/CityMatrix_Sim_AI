'''
Filename: predictor.py
Author: Kevin <mailto:kalyons@mit.edu>
Created: 2017-06-01 20:17:36
Last modified by: kalyons11
Last modified time: 2017-06-15 23:37:24
Description:
    - Generic black box ML predictor that takes in a city and runs the necessary ML predictions on it for
    all features. Right now, these features are traffic, wait (not right now) AND solar radiation.
TODO:
    - Remove redundancies.
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
    result = features
    result[::2] = traffic_output[::2]

    # Write prediction back to the cityiograph.City structure and return
    new_city = output_to_city(city, result)
    return new_city

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
        next_prev = result.copy() # TODO need to figure out wether this next prev stuff is good or not
        result = solar.update_city(prev, result, x, y)
        prev = next_prev # Maybe???
        # np.set_printoptions(threshold = np.nan)
        # print(result.get_data_matrix('solar'))

    return result

def predict(city, change_key, change_data): # TODO next/prev update
    '''
    Black box predictor function for our machine learning.
    Input:     city - instance of cityiograph.City to be predicted
            change_key - instance of utils.CityChange - descibes the change made
            change_value - arguments telling us what makes this new city unique from the previous
            force_predict - default False value; used for AI predictor
    Output: result_city - instance of cityiograph.City, with updated cell data values
    '''

    if isinstance(change_data, bool) or city.startFlag == 1:
        # First city OR same city - just want traffic update
        # evaluate and update scores
        return traffic_predict(city)

    # Parse our change data
    l, prev = tuple(change_data) # TODO next/prev update
    # print(prev.densities, "prev")

    # First, do full traffic prediction
    current = traffic_predict(city)
    # print(id(city), "city")
    # print(id(current), "current")
    # print(id(prev), "prev")
    locations = []

    if change_key == CityChange.DENSITY:
        indices = l # List of indices in density array where we have a change - likely length 1
        # Find locations with that density value in PREVIOUS *** city
        for i in indices:
            for c in prev.cells.values():
                if c.type_id == i:
                    locations.append(c.get_pos()) # TODO keep an eye on how this is working

    elif change_key == CityChange.CELL:
        locations = l # Already have changed locations from data

    return solar_predict(current, prev, locations)
