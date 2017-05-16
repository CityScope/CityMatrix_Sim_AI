'''
    File name: utils.py
    Author(s): Kevin Lyons, Alex Aubuchon
    Date created: 5/12/2017
    Date last modified: 5/16/2017
    Python Version: 3.5
    Purpose: Simple utils script to be used alongside prediction_server, among other files. Various tasks, including model serialization and math operations.
    TODO:
    	- Determine filename format.
    	- Determine JSON output format.
'''

# General imports
import sys, json, time, os, numpy as np

# Keras import for JSON functionality
from keras.models import model_from_json

# Custom imports
import cityiograph

# Global variables
ROAD_ID = 6

# Serializes a Keras model to a JSON and h5 data file
def serialize_model(model, root_filename):

	# Convert to JSON
	model_in_json = model.to_json()

	# Write to file
	with open(root_filename + ".json", "w") as json_file:
		json_file.write(model_in_json)

    # Save weights
	model.save_weights(root_filename + ".h5")

	print("Successfully serialized model to local files {}.".format(root_filename))

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
	print("Successfully deserialized our model.")
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
	def __init__(self, name, output_dir = None):
		self.name = name
		self.output_dir = output_dir

		# Create output directory if needed
		# Taken from http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
		if not os.path.exists(self.output_dir):
			os.makedirs(self.output_dir)

	def write_city(self, city, filename):
		'''
		Input: city - instance of cityiograph.City - city to be logged
			   filename - raw prefix string of filename - need to format
		Output: None - write city as JSON to specified filename for later ML purposes
		'''
		# Convert to dictionary object for editing
		d = city.to_dict()

		# Add UNIX timestamp to JSON
		# Taken from https://timanovsky.wordpress.com/2009/04/09/get-unix-timestamp-in-java-python-erlang/
		d['objects']['timestamp'] = int(time.time())

		# Write dictionary to JSON
		full_name = self.output_dir + self.format(filename) + ".json"
		with open(full_name, 'w') as f:
			f.write(json.dumps(d))

		print("Successfully wrote city to file {}.".format(full_name))

	def format(self, filename):
		'''
		Input: filename - raw prefix string of filename - need to format
		Output: formatted_filename - properly updated to reflect filename format for later ML prediction
		'''
		return filename