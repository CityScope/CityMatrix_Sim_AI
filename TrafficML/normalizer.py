'''
    File name: normalizer.py
    Author: Kevin Lyons
    Date created: 5/8/2017
    Date last modified: 5/10/2017
    Python Version: 3.5
    Purpose: Developing a simple linear regression model that can re-normalize all ouputs of the CityMatrix TrafficML CNN to more closely match those of actual simulation outputs. The overall structure will be quite  simple. We will take in predicted cities as X, actual cities as Y, and learn a scalar mapping X -> Y. I will use sklearn framework here for its simplicity and functionality.
'''

# Global import statements
import glob, pickle, sys
from tqdm import tqdm

# Learning imports
from sklearn import linear_model
from sklearn.metrics import r2_score # From https://iwatobipen.wordpress.com/2016/12/13/build-regression-model-in-keras/
from keras.models import Sequential
from keras.layers import Dense, Activation

# Custom imports
sys.path.insert(0, '../TrafficTreeSim/')
import cityiograph

from traffic_regression import output_to_city

# Gobal latent parameters
NB_EPOCH = 50
BATCH_SIZE = 32
VERBOSE = 1
MODEL_TYPE = 'simple_linear' # simple_linear, lasso, neural_normalizer, neural_normalizer_pos
LOAD_MODEL = True
OUTPUT_PATH = './normalized_outputs/'
MAX_OUTPUT_NUM = 200

# First, load train and test data from saved pickle files
X_TRAIN_PICKLE_FILE = './pred.p'
Y_TRAIN_PICKLE_FILE = './latest_data_test.p'

print("Loading data from pickle files.")
X_train = pickle.load(open(X_TRAIN_PICKLE_FILE, 'rb'))
Y_train = pickle.load(open(Y_TRAIN_PICKLE_FILE, 'rb'))

# Both are tuples with structure (cities, filenames, inp, out) - we want last elements
print("Reformatting data.")
X = X_train[3]
Y = Y_train[3]

# Both X and Y have shape (None, 512)
# Now, simply learn linear scale factors between every feature of input and outuput
# General structure for lin reg taken from the following sources:
# http://scikit-learn.org/stable/auto_examples/linear_model/plot_ols.html
# http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html#sklearn.linear_model.Lasso
print("Creating model.")
if LOAD_MODEL and MODEL_TYPE != 'neural_normalizer' and MODEL_TYPE != 'neural_normalizer_pos':
	model = pickle.load(open(MODEL_TYPE + '.p', 'rb'))
else:
	model = Sequential()
	model.add(Dense(512, input_shape = (512, ), activation = 'linear', kernel_constraint = 'non_neg'))
	model.compile(loss = 'mean_squared_error', optimizer = 'adam', metrics = ['accuracy'])

	# Now, fit the model to our X and Y data
	print("Fitting model to our dataset.")
	model.fit(X, Y, epochs = NB_EPOCH, batch_size = BATCH_SIZE, verbose = VERBOSE)

# Evaluate again on train data
print("Scoring model for validation.")
if MODEL_TYPE == 'neural_normalizer' or MODEL_TYPE == 'neural_normalizer_pos':
	pred = model.predict(X)
	score = r2_score(pred, Y)
else:
	# We are going with regression for this normalization
	score = model.score(X, Y)
	pred = model.predict(X)
	# pred object is n x 512 np matrix
	# Now, need to write to JSON
	train_cities = X_train[0]
	filenames = Y_train[1]
	# Need to write this data to train_cities
	for i, city in tqdm(enumerate(train_cities)):
		# Get new data and filename to write
		new_data, filename = list(pred[i]), filenames[i]
		# Add normalized data to the city structure itself
		output_to_city(city, new_data)
		# Write to JSON
		j = city.to_json()
		# Write this to new filename and output
		with open(OUTPUT_PATH + filename + '_normalized.json', 'w') as f:
			f.write(j)
		if i == MAX_OUTPUT_NUM: # Just to keep things small
			break
print(score)

# Simple lin reg = 0.521035143549
# Lasso = 0.295294099448
# 1 layer neural normalizer = -0.449191600532
# 1 layer with positive weights = -1.47146662043

# Write to pickle file for later retreival
print("Saving model locally.")
if MODEL_TYPE != 'neural_normalizer' and MODEL_TYPE != 'neural_normalizer_pos':
	pickle.dump(model, open(MODEL_TYPE + '.p', 'wb'))

print("Process complete.")