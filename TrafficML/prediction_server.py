'''
    File name: predictin_server.py
    Author: Alex Aubuchon, Kevin Lyons
    Date created: 5/12/2017
    Date last modified: 5/16/2017
    Python Version: 3.5
    Purpose: Developing a simple UDP server that can send and receive City objects and run machine learning prediction algorithms. We will combine linear regression on traffic features with a CNN prediction on wait time features. Implements the base city_udp class and applies custom logic in loop format to make predictions.
    TO DO:
   		- None at this time.
'''

# Generic import statements
import sys, time, pickle, numpy as np

# Import local scripts for city/model functionality
sys.path.extend(['../TrafficTreeSim/', '../'])
import cityiograph, city_udp, utils, traffic_regression

# Global instance variables

# ML variables
LINEAR_MODEL_FILENAME = './model_files/linear_model.pkl' # Pickle file for traffic predictor
ROOT_NN_FILENAME = './model_files/neural_model' # Root name for neural network JSON/H5
NUM_FEATURES = 512 # Traffic and wait for 256 cells = 512
MATRIX_SHAPE = (-1, 16, 16, 2) # 3D matrix representation of our city grid as "image" for CNN

# Server variables
LISTENING = True # Bool to say whether or not we want our server to be "on" and listening
SERVER_NAME = 'Prediction_Server'
RECEIVE_IP = "127.0.0.1"
RECEIVE_PORT = 9000
SEND_IP = "127.0.0.1"
SEND_PORT = 9001

# Log variables
LOGGER_NAME = 'CityLog'
LOGGER_DIRECTORY = './log/'

# Create instance of our server
server = city_udp.City_UDP(SERVER_NAME, receive_port = RECEIVE_PORT, send_port = SEND_PORT)

# Create instance of our custom logger class
log = utils.CityLogger(LOGGER_NAME, LOGGER_DIRECTORY)

# Load linear and neural models, respectively
linear_model = pickle.load(open(LINEAR_MODEL_FILENAME, 'rb'))
neural_model = utils.deserialize_model(ROOT_NN_FILENAME)

# Constantly loop and wait for new city packets to reach the UDP server
# Taken directly from Alex's code for regression_server.py
while LISTENING:

	print("{} listening on ip: {}, port: {}.".format(SERVER_NAME, RECEIVE_IP, RECEIVE_PORT))

	# Breifly sleep
	time.sleep(0.1)
	
	print("Waiting to receive city...")
	city = server.receive_city()
	print("City received!")

	# Write city to local file
	log.write_city(city, "test")

	# Extract feature matrix from this city
	features = traffic_regression.get_features(city)

	# Separate into input for linear and neural models
	linear_input = [features]
	neural_input = features.reshape(MATRIX_SHAPE)

	# Make traffic prediction using linear model
	linear_output = linear_model.predict(linear_input)[0] # Type = np array, 1 x 512
	linear_output[linear_output < 0] = 0. # Trim negative values from regression

	# Make wait prediction using neural model
	neural_output = neural_model.predict(neural_input)[0] # Type = np array, shape = (16, 16, 2)

	# Split on traffic and wait values
	traffic_list = linear_output[::2].tolist() # List of size 256
	wait_list = neural_output[: , : , 1].reshape(NUM_FEATURES // 2).tolist() # List of size 256

	# Need to combine traffic and wait output values into a final list of length 512
	# See http://stackoverflow.com/questions/3678869/pythonic-way-to-combine-two-lists-in-an-alternating-fashion for clever combination trick
	result = np.zeros(NUM_FEATURES)
	result[::2] = traffic_list
	result[1::2] = wait_list

	# Write prediction back to the cityiograph.City structure
	traffic_regression.output_to_city(city, result)

	# Send the city object directly back to Grasshopper script via UDP server
	server.send_city(city)
	print("Predicted city sent!")