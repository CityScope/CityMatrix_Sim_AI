'''
Filename:   		predictor.py
Author: 	        Kevin <mailto:kalyons@mit.edu>
Created:       		2017-06-01 20:17:36
Last modified by:   kalyons11 
Last modified time: 2017-06-01 21:39:33
Description:
	- Generic black box ML predictor that takes in a city and runs the necessary ML predictions on it for \
	all features. Right now, these features are traffic, wait (not right now) AND solar radiation.
TODO:
	- Get solar model working, with support of Alex. Try to keep as much of his code intact as possible.
	- Once this is all working, optimize. Fix weird import statement dependencies.
'''

# Get our key utils script
import sys
sys.path.extend(['../global/', '../MachineLearning/'])
from utils import *
# import solar_regression as solar

# Load 2 model files
traffic_model = pickle.load(open(LINEAR_MODEL_FILENAME, 'rb'))
# solar_model = pickle.load(open(SOLAR_MODEL_FILENAME), 'rb')

def traffic_predict(city):
	'''
	Generic traffic predictor.
	Input: 	city - instance of cityiograph.City to be predicted
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
	out_city = output_to_city(city, result)
	return out_city

def solar_predict(city, prev, locations):
	'''
	Generic solar radiation predictor with accumulation functionality.
	Input: 	city - instance of cityiograph.City to be predicted
			prev - instance of cityiograph.City that represents our prior state
			locations - list of (x, y) cell coordinates where we need to run solar analysis
	Output: out_city - instance of cityiograph.City, with updated cell data values for solar after we apply deltas
	'''

	# Keep a running accumulated city
	result = city

	# For every location, update values based on solar radiation deltas predictor
	for x, y in locations:
		# result = solar.update_city(prev, result, x, y)
		continue

	return result

def predict(city, change_key, change_data):
	'''
	Black box predictor function for our machine learning.
	Input: 	city - instance of cityiograph.City to be predicted
			change_key - instance of utils.CityChange - descibes the change made
			change_value - arguments telling us what makes this new city unique from the previous
	Output: result_city - instance of cityiograph.City, with updated cell data values
	'''

	# Parse our change data
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

if __name__ == '__main__':
	log.debug("We made it.")