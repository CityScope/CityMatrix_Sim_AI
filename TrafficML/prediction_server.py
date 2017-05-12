'''
    File name: predictin_server.py
    Author: Alex Aubuchon, Kevin Lyons
    Date created: 5/12/2017
    Date last modified: 5/12/2017
    Python Version: 3.5
    Purpose: Developing a simple UDP server that can send and receive City objects and run machine learning prediction algorithms. We will combine linear regression on traffic features with a CNN prediction on wait time features.
    TO DO:
   	- Get linear model pickle file and specs from Alex.
   	- Implement logging functionality.
'''

# Generic import statements
import sys, time, pickle, numpy as np

# Import local scripts for city/model functionality
sys.path.extend(['../TrafficTreeSim/', '../'])
import cityiograph, city_udp, utils, traffic_regression

# Global instance variables
LINEAR_MODEL_FILENAME = '' # Pickle file for traffic predictor
ROOT_NN_FILENAME = 'saved_model' # Root name for neural network JSON/H5
LISTENING = True # Bool to say whether or not we want our server to be "on" and listening
SERVER_NAME = 'Prediction_Server'
RECEIVE_IP = "127.0.0.1"
RECEIVE_PORT = 9000
SEND_IP = "127.0.0.1"
SEND_PORT = 9001

# Create instance of our server
server = city_udp.City_UDP(SERVER_NAME, receive_port = RECEIVE_PORT, send_port = SEND_PORT)

# Load linear and neural models, respectively
# linear_model = pickle.load(open(LINEAR_MODEL_FILENAME, 'rb'))
neural_model = utils.deserialize_model(ROOT_NN_FILENAME)

# Constantly loop and wait
while LISTENING:

	print("{} listening on ip: {}, port: {}.".format(SERVER_NAME, RECEIVE_IP, RECEIVE_PORT))

	# Breifly sleep
	time.sleep(0.1)

	# Constantly wait for new cities to be received via UDP
	# Taken directly from Alex's code for regression_server.py
	print("Waiting to receive city...")
	incoming_city = server.receive_city()
	print("City received!")

	# Extract feature matrix from this city
	features = traffic_regression.get_features(incoming_city)

	# Separate into input for linear and neural models
	linear_input = [features]
	neural_input = features.reshape((-1, 16, 16, 2))

	# Make traffic prediction using linear model
	# linear_output = linear_model.predict(linear_input) # Type = ??? - still waiting on this

	# Make wait prediction using neural model
	neural_output = neural_model.predict(neural_input)[0] # Type = np array, shape = (16, 16, 2)

	# Need to combine traffic and wait output values into a final list of length 512
	# See http://stackoverflow.com/questions/3678869/pythonic-way-to-combine-two-lists-in-an-alternating-fashion for clever combination trick
	wait_list = neural_output[: , : , 1].reshape(256).tolist() # List of size 256

	# Write prediction back to the cityiograph.City structure
	outgoing_city = incoming_city
	traffic_regression.output_to_city(outgoing_city, result_list)

	# Send the city back to Grasshopper script via UDP
	server.send_city(outgoing_city)
	print("Updated city sent!")