import glob, json, time, numpy as np, sys, os, pickle

sys.path.insert(0, '../TrafficTreeSim/')

import cityiograph

from traffic_regression import get_features, get_results

# Utils

POP_ARR = [5, 8, 16, 16, 23, 59]
TRAIN_GOOD_DIR = '../../../data/train_good/*.json'
TEST_GOOD_DIR = '../../../data/test_good/*.json'

def print_array(b):
	for row in b:
		for c in row:
			print(str(c) + ",	", end='')
		print('')

def get_population(t, density_array):
	if t not in range(0, 6):
		return 0
	return density_array[t] * POP_ARR[t]

def extract_features(directory):

	cities = []
	filenames = []
	input_features = []
	output_features = []

	files = glob.glob(directory)

	for name in files:
		with open(name, 'r') as f:
			city = cityiograph.City(f.read())
			cities.append(city)
			input_features.append(get_features(city))
			output_features.append(get_results(city))

	input_features = np.array(input_features).astype('int32')
	output_features = np.array(output_features).astype('int32')

	return cities, input_features, output_features

	# This funciton has been giving me some trouble when it comes to training the neural model - sticking with my custom extract_data functin below...

def extract_data(directory):

	files = glob.glob(directory)

	cities = [] # City objects list
	filenames = [] # List of raw filenames
	inp = [] # Input feature matrix
	out = [] # Output feature matrix

	for name in files:
		with open(name, 'r') as f:
			current_input = []
			current_output = []
			s = f.read()
			city = cityiograph.City(s)
			cities.append(city)
			raw = os.path.splitext(os.path.basename(name))[0]
			filenames.append(raw)
			d = json.loads(s)
			max_traffic = max([cell['data']['traffic'] for cell in d['grid'] if 'data' in cell])
			max_wait = max([cell['data']['wait'] for cell in d['grid'] if 'data' in cell])
			if max_traffic == 0 or max_wait == 0:
				continue
			for i in range(city.width):
				for j in range(city.height):
					cell = city.cells.get((i, j))
					current_input.append(cell.population)
					current_input.append(0) if (cell.type_id == 6) else current_input.append(1)
					current_output.append(cell.data["traffic"])
					current_output.append(cell.data["wait"])
			inp.append(np.array(current_input))
			out.append(np.array(current_output))

	inp = np.array(inp).astype(int)
	out = np.array(out).astype(int)

	return cities, filenames, inp, out

# Data manager...

print('Extracting data...')

train_data = extract_data(TRAIN_GOOD_DIR)
test_data = extract_data(TEST_GOOD_DIR)

pickle.dump(train_data, open('latest_data_train.p', 'wb'))
pickle.dump(test_data, open('latest_data_test.p', 'wb'))

# train_x = np.vstack((train_x, test_x))
# train_y = np.vstack((train_y, test_y))

# variables = {'train_x':train_x,'train_y':train_y,'test_x':test_x,'test_y':test_y}
# pickle.dump(variables, open('neural_data.p','wb'))

# data = extract_features(TEST_GOOD_DIR)

# pickle.dump(data, open('latest_data_test.p', 'wb'))

print('Successfully extracted test data. Wrote to local pickle files. Process complete.')