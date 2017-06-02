'''
	File name: utils.py
	Author(s): Kevin Lyons, Alex Aubuchon
	Date created: 5/12/2017
	Date last modified: 6/1/2017
	Python Version: 3.5
	Purpose: Simple utils script to be used alongside our server, among other files. Various \
		tasks, including model serialization and math operations.
	TODO:
	- None at this time.
'''

# General imports
import sys, json, os, time, pickle, atexit, traceback, logging, subprocess, threading, copy, glob, numpy as np
from enum import Enum

# Prevent TensorFlow log statements
# Taken from https://github.com/tensorflow/tensorflow/issues/8340
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Keras import for JSON functionality
from keras.models import model_from_json

# Custom imports
import cityiograph
from config import *

def serialize_model(model, root_filename):
	'''
	Serializes a Keras model to a JSON and h5 data file
	Input: 	model - instance of Keras model to be serialized
	root_filename - string representing root of JSON and h5 data file for model
	Output:	None - simply write the model to the files
	'''

	# Convert to JSON
	model_in_json = model.to_json()

	# Write to file
	with open(root_filename + ".json", "w") as json_file:
		json_file.write(model_in_json)

	# Save weights
	model.save_weights(root_filename + ".h5")

def deserialize_model(root_filename):
	'''
	Deserialze data in .json and .h5 files into a Keras model that can be used for ML prediction
	Input: 	root_filename - string representing root of JSON and h5 data file for model
	Output:	model - instance of Keras model taken from data
	'''

	# Read JSON string
	with open(root_filename + '.json', 'r') as f:
		model_in_json = f.read()

	# Load model with architecture and weights
	model = model_from_json(model_in_json)
	model.load_weights(root_filename + '.h5')

	# Compile the model with loss, optimizer and metrics and return
	model.compile(loss = LOSS_FUNCTION, optimizer = OPTIMIZER, metrics = KERAS_METRICS)
	return model

def compute_accuracy(true, pred):
	'''
	Compute percent accuracy between 2 input matrices (true and predicted values)
	Input: 	a, b - np array n x ( )
	Output: accuracy - scalar that represents (1 - percent error) between a and b, in range [0, 1]
	'''

	# Simple solution taken from http://stackoverflow.com/questions/20402109/calculating-percentage-error-by-comparing-two-arrays
	return 1 - np.mean(true != pred)

def cell_features(cell):
	'''
	Get the 2 input features for a given cell
	Currently using population and is road
	Input: 	cell - instance of cityiograph.Cell
	Output:	feats - list of input features for this cell
	'''
	feats = [ cell.population ]
	feats.append(0) if (cell.type_id == ROAD_ID) else feats.append(1)
	return feats

def cell_results(cell):
	'''
	Get the 2 output features for a given cell
	Currently using traffic score and wait time
	Input: 	cell - instance of cityiograph.Cell
	Output:	feats - list of output features for this cell
	'''
	return [ cell.data["traffic"], cell.data["wait"] ]

def get_features(city):
	'''
	Get the input feature vector for a given city
	Input: 	city - instance of cityiograph.City
	Output:	feats - np array of input features for this city
	'''
	features = []
	for i in range(city.width):
		for j in range(city.height):
			cell = city.cells.get((i, j))
			features += cell_features(cell)
	return np.array(features)

def get_results(city):
	'''
	Get the output feature vector for a given city
	Input: 	city - instance of cityiograph.City
	Output:	feats - np array of output features for this city
	'''
	results = []
	for i in range(city.width):
		for j in range(city.height):
			cell = city.cells.get((i, j))
			results += cell_results(cell)
	return np.array(results)

def output_to_city(city, output):
	'''
	Custom method to write new data to city object for later serialization
	Input:	city - instance of cityiograph.City
	output - list of traffic and wait scores, alternating
	Output:	city - simply write this data to the existing city object and return
	'''
	i = 0
	for x in range(city.width):
		for y in range(city.height):
			cell = city.cells.get((x, y))
			cell.data["traffic"] = int(round(output[i]))
			cell.data["wait"] = int(round(output[i + 1]))
			i += 2	
	return city

# Create custom logging class for file I/O
class CityLogger:
	def __init__(self, name, log_filename):
		self.name = name # Name of our logger for ID purposes

		# First time log file initialized
		# Taken from http://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-using-python
		if not os.path.isfile(log_filename):
			first = True
		else:
			first = False

		# Set up logger to file AND console
		# Taken from multiple sources
		# http://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
		# https://docs.python.org/2/howto/logging.html
		logFormatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s", '%m/%d/%Y %I:%M:%S %p')
		self.logger = logging.getLogger(self.name)
		self.logger.setLevel(logging.DEBUG)

		fileHandler = logging.FileHandler(log_filename)
		fileHandler.setFormatter(logFormatter)
		self.logger.addHandler(fileHandler)

		consoleHandler = logging.StreamHandler(sys.stdout)
		consoleHandler.setFormatter(logFormatter)
		self.logger.addHandler(consoleHandler)

		if first:
			self.info("Successfully initialized log file at {}.".format(log_filename))

	def write_city(self, city):
		'''
		Write a city to a JSON file
		Input: 	city - instance of simCity - city to be logged
		Output: None - write city as JSON to specified filename for later ML purposes
		'''
		# Convert to dictionary object for editing
		d = city.cityObject.to_dict()

		# Add UNIX timestamp to JSON
		d['objects']['timestamp'] = city.timestamp

		# Write dictionary to JSON
		with open(city.filename, 'w') as f:
			f.write(json.dumps(d))

	# Simple log methods to avoid having to write log.logger.info - a bit counterintuitive
	def info(self, message):
		self.logger.info(message)

	def debug(self, message):
		self.logger.debug(message)

	def warn(self, message):
		self.logger.warning(message)

	def error(self, message):
		self.logger.error(message)

	# Methods to write to log file AND console
	# Taken from http://stackoverflow.com/questions/14906764/how-to-redirect-stdout-to-both-file-and-console-with-scripting
	def write(self, message):
		self.info(message)

	def flush(self):
		pass # Nothing to do here

# Create instance of our custom logger class and connect to output stream
log = CityLogger(LOGGER_NAME, LOGGER_FILENAME)
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

class CityChange(Enum):
	NO = -1,
	FIRST = 0,
	DENSITY = 1,
	CELL = 2

def diff_cities(current_city):
	'''
	Determine if a new city is different from the existing one in memory, and if so, how?
	Input: 	city - instance of cityiograph.City object - incoming city to server
	Output: Return the difference between current city and previouly saved one
	'''

	# First, get the most recent city from our saved set
	# Taken from http://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python
	files = glob.glob(INPUT_CITIES_DIRECTORY + '*')

	# If this is the first city, return need for prediction
	if len(files) == 0: return ( CityChange.FIRST , True )

	# Run comparison on this city and most recent one
	with open(max(files, key = os.path.getctime), 'r') as f:
		# Load prev_city from JSON
		j = f.read()
		prev_city = cityiograph.City(j)
		
		# Now, compare directly for densities, size and cells
		if prev_city.equals(current_city): return ( CityChange.NO, False )
		else: # Yes, we have a difference, let's explore
			result = []
			if prev_city.densities != current_city.densities:
				for i, d in enumerate(prev_city.densities):
					if current_city.densities[i] != d:
						result.append(i)
				return ( CityChange.DENSITY , [ result, prev_city ] )
			else:
				# We likely have some cell mismatch(es) - need to find
				for x in range(prev_city.width):
					for y in range(prev_city.height):
						old = prev_city.cells.get((x, y))
						new = current_city.cells.get((x, y))
						if not old.equals(new):
							result.append( (x, y) )
				return ( CityChange.CELL , [ result, prev_city ] )

# Set up our exception handler on this new thread
# Taken from https://bugs.python.org/issue1230540
run_old = threading.Thread.run
def run(*args, **kwargs):
	try:
		run_old(*args, **kwargs)
	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		sys.excepthook(*sys.exc_info())
		threading.Thread.run = run

def async_process(commands, hook, log, city):
	'''
	Custom method to run process on new thread and notify with hook when returned
	Taken from http://stackoverflow.com/questions/2581817/python-subprocess-callback-when-cmd-exits
	Input: 	commands - list of strings of commands to be send to subprocess module
	hook - function to be called once simulation is complete
	log - instance of CityLogger that we can write to on new thread
	city - instance of sim.SimCity that we are simulating
	Output:	None - simply run the process and notify when complete
	'''
	def run(commands, hook, log, city):
		# Run process with commands and streams
		p = subprocess.Popen(commands, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		# Taken from http://stackoverflow.com/questions/15535240/python-popen-write-to-stdout-and-log-file-simultaneously
		# Also, rstrip from http://stackoverflow.com/questions/275018/how-can-i-remove-chomp-a-newline-in-python
		for line in p.stdout: log.info(line.decode('utf-8').rstrip())
		
		status = p.wait() # Wait for command to complete
		hook(city, status) # Call our hook with city object
		return

	# Set up threading functionality
	thread = threading.Thread(target = run, args = (commands, hook, log, city))
	thread.start()