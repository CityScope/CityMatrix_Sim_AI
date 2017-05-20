'''
    File name: utils.py
    Author(s): Kevin Lyons, Alex Aubuchon
    Date created: 5/12/2017
    Date last modified: 5/19/2017
    Python Version: 3.5
    Purpose: Simple utils script to be used alongside prediction_server, among other files. Various tasks, including model serialization and math operations.
    TODO:
    	- None at this time.
'''

# General imports
import sys, json, os, logging, subprocess, threading, glob, numpy as np

# Keras import for JSON functionality
from keras.models import model_from_json

# Custom imports
import cityiograph
from config import *

# Serializes a Keras model to a JSON and h5 data file
def serialize_model(model, root_filename):

	# Convert to JSON
	model_in_json = model.to_json()

	# Write to file
	with open(root_filename + ".json", "w") as json_file:
		json_file.write(model_in_json)

    # Save weights
	model.save_weights(root_filename + ".h5")

# Deserialze data in .json and .h5 files into a Keras model that can be used for ML prediction
def deserialize_model(root_filename):

	# Read JSON string
	json_file = open(root_filename + '.json', 'r')
	model_in_json = json_file.read()
	json_file.close()

	# Load model with architecture and weights
	model = model_from_json(model_in_json)
	model.load_weights(root_filename + '.h5')

	# Compile the model with loss, optimizer and metrics
	model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

	# Return the final model
	return model

# Compute percent accuracy between 2 input matrices (true and predicted values)
def compute_accuracy(true, pred):
	'''
	Input: a, b - np array n x ( )
	Output: accuracy - scalar that represents (1 - percent error) between a and b, in range [0, 1]
	'''

	# Simple solution taken from http://stackoverflow.com/questions/20402109/calculating-percentage-error-by-comparing-two-arrays
	return 1 - np.mean(true != pred)

# Get the 2 input features for a given cell
# Currently using population and is road
def cell_features(cell):
    feats = []
    feats.append(cell.population)
    feats.append(0) if (cell.type_id == ROAD_ID) else feats.append(1)
    return feats

# Get the 2 input features for a given cell
# Currently using traffic and wait time
def cell_results(cell):
    results = []
    results.append(cell.data["traffic"])
    results.append(cell.data["wait"])
    return results

# Get the input feature vector for a given city
def get_features(city):
    features = []
    for i in range(city.width):
        for j in range(city.height):
            cell = city.cells.get((i, j))
            features += cell_features(cell)
    return np.array(features)

# Get the output feature vector for a given city
def get_results(city):
    results = []
    for i in range(city.width):
        for j in range(city.height):
            cell = city.cells.get((i, j))
            results += cell_results(cell)
    return np.array(results)

# Custom method to write new data to city object for later serialization
def output_to_city(city, output):
    i = 0
    for x in range(city.width):
        for y in range(city.height):
            cell = city.cells.get((x, y))
            cell.data["traffic"] = int(round(output[i]))
            cell.data["wait"] = int(round(output[i + 1]))
            i += 2	

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

		# Set up logger to file and console
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
		Input: city - instance of simCity - city to be logged
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
		pass

def diff_cities(current_city):
	'''
	Input: city - instance of cityiograph.City object - incoming city to server
	Output: Return True if we should consider the incoming city and predict/simulate; false otherwise
	'''

	# First, get the most recent city from our saved set
	# Taken from http://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python
	files = glob.glob(INPUT_CITIES_DIRECTORY + '*')

	# If this is the first city, return True
	if len(files) == 0:
		return True

	# Run comparison on this city and most recent one
	with open(max(files, key = os.path.getctime), 'r') as f:
		# Load prev_city from JSON
		j = f.read()
		prev_city = cityiograph.City(j)
		
		# Now, compare directly for densities, size and cells
		return not prev_city.equals(current_city)

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

# Custom method to run process on new thread and notify when returned
# Taken from http://stackoverflow.com/questions/2581817/python-subprocess-callback-when-cmd-exits
def async_process(commands, hook, log, city):
	def run(commands, hook, log, city):
		p = subprocess.Popen(commands, stdout = subprocess.PIPE, stderr = subprocess.STDOUT) # Initialize process
		
		# Taken from http://stackoverflow.com/questions/15535240/python-popen-write-to-stdout-and-log-file-simultaneously
		# Also, rstrip from http://stackoverflow.com/questions/275018/how-can-i-remove-chomp-a-newline-in-python
		for line in p.stdout:
		    log.info(line.decode('utf-8').rstrip())
		
		p.wait() # Wait for command to complete
		hook(city) # Call our hook with city object
		return

	# Set up threading functionality
	thread = threading.Thread(target = run, args = (commands, hook, log, city))
	thread.start()
	return thread