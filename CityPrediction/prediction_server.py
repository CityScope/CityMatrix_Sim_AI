'''
    File name: predictin_server.py
    Author: Alex Aubuchon, Kevin Lyons
    Date created: 5/12/2017
    Date last modified: 5/19/2017
    Python Version: 3.5
    Purpose: Developing a simple UDP server that can send and receive City objects and run machine learning prediction algorithms. We will combine linear regression on traffic features with a CNN prediction on wait time features. Implements the base city_udp class and applies custom logic in loop format to make predictions.
    TO DO:
    	- Handle False output from diff function. What do we send back to the server?
'''

# Generic import statements
import sys, os, time, pickle, time, atexit, traceback, numpy as np

# Prevent TensorFlow log statements
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Import local scripts for city/model functionality, as well as configuration variables
sys.path.append('../global/')
import cityiograph, city_udp, utils, sim as simulator
from config import *

# Create instance of our server
server = city_udp.City_UDP(SERVER_NAME, receive_port = RECEIVE_PORT, send_port = SEND_PORT)

# Create instance of our custom logger class and connect to output stream
log = utils.CityLogger(LOGGER_NAME, LOGGER_FILENAME)
sys.stdout = log

# Need to log when server stopped
# Taken from https://docs.python.org/2/library/atexit.html
@atexit.register
def end():
    log.warn(SERVER_NAME + " has been stopped.")

# Configure log to handle all uncaught exceptions
# Taken from http://stackoverflow.com/questions/8050775/using-pythons-logging-module-to-log-all-exceptions-and-errors
# Also from http://stackoverflow.com/questions/4564559/get-exception-description-and-stack-trace-which-caused-an-exception-all-as-a-st
def handler(type, value, tb):
	log.error(str(value) + "\n" + "\n".join(traceback.format_tb(tb)))

sys.excepthook = handler

# First, ensure that all directories exist
# Taken from http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
DIRECTORY_LIST = [INPUT_CITIES_DIRECTORY, OUTPUT_CITIES_DIRECTORY, GAMA_OUTPUT_DIRECTORY, XML_DIRECTORY]

for d in DIRECTORY_LIST:
	if not os.path.exists(d):
		log.warn("Creating directory {}.".format(d))
		os.makedirs(d)

# Create instance of our simulator
sim = simulator.CitySimulator(SIM_NAME, log)

# Load linear and neural models, respectively
linear_model = pickle.load(open(LINEAR_MODEL_FILENAME, 'rb'))
neural_model = utils.deserialize_model(ROOT_NN_FILENAME)

log.info("{} listening on ip: {}, port: {}.".format(SERVER_NAME, RECEIVE_IP, RECEIVE_PORT))
log.info("Waiting to receive city...")

# Constantly loop and wait for new city packets to reach our UDP server
# Taken directly from Alex's code for regression_server.py
while LISTENING:
	# Get city from server
	city = server.receive_city()

	# Only consider new city if it is different from most recent
	if utils.diff_cities(city):
		# Write city to local file
		# Taken from https://timanovsky.wordpress.com/2009/04/09/get-unix-timestamp-in-java-python-erlang/
		timestamp = str(int(time.time()))
		log.info("New city received @ timestamp {}.".format(timestamp))
		simCity = simulator.SimCity(city, timestamp)
		log.write_city(simCity)

		# Extract feature matrix from this city
		features = utils.get_features(city)

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
		# Taken from http://stackoverflow.com/questions/3678869/pythonic-way-to-combine-two-lists-in-an-alternating-fashion for clever combination trick
		result = np.zeros(NUM_FEATURES)
		result[::2] = traffic_list
		result[1::2] = wait_list

		# Write prediction back to the cityiograph.City structure
		utils.output_to_city(city, result)

		# Send the city object directly back to Grasshopper script via UDP server
		server.send_city(city)
		log.info("Predicted city sent back to client!")

		# Now, run the GAMA simulation "async" on this city and save the resulting JSON for later use
		sim.simulate(simCity)

		log.info("Waiting to receive city...")

	else:
		# This new city is no different from the previous one
		# Do not send prediction back to server client
		continue