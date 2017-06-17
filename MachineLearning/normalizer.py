'''
    File name: normalizer.py
    Author: Kevin Lyons
    Date created: 5/8/2017
    Date last modified: 5/13/2017
    Python Version: 3.5
    Purpose: Developing a simple linear regression model that can re-normalize all ouputs of the CityMatrix TrafficML CNN to more closely match those of actual simulation outputs. The overall structure will be quite  simple. We will take in predicted cities as X, actual cities as Y, and learn a scalar mapping X -> Y. I will use sklearn framework here for its simplicity and functionality. Also looking at global scale factor.
    TODO:
        - Choose best normalizing method and create function to be used in prediction_server.py.
'''

# Global import statements
import glob, pickle, sys, numpy as np, os # For general functionality
from tqdm import tqdm # Used to measure large loop progress

# Learning imports
from sklearn import linear_model
from sklearn.metrics import r2_score # From https://iwatobipen.wordpress.com/2016/12/13/build-regression-model-in-keras/
from keras.models import Sequential
from keras.layers import Dense, Activation

# Custom imports
sys.path.insert(0, '../global/')
import cityiograph, utils

# Gobal latent parameters
NB_EPOCH = 50 # Number of training iterations for NN
BATCH_SIZE = 32
VERBOSE = 1 # Logging setting
MODEL_TYPE = 'global' # simple_linear, lasso, neural_normalizer, neural_normalizer_pos, global, matrix
OUTPUT_PATH = './normalized_outputs_' + MODEL_TYPE + '/' # For renormalizing test cities
MAX_OUTPUT_NUM = 200 # Limiting for Ryan's analysis
DO_LEARN = True # Actually recompute city values
WRITE_FILES = False # Overwrite JSON
TRAFFIC_SCALE, WAIT_SCALE = 1.34227926669, 4.297754804071 # Taken directly from numpy sum averages
SCALE_MATRIX_FILENAME = './matrix.p'
X_TRAIN_PICKLE_FILE = './pred.p'
Y_TRAIN_PICKLE_FILE = './latest_data_test.p'

# Create output directory if needed
# Taken from http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

# First, load train and test data from saved pickle files
print("Loading data from pickle files.")
X_train = pickle.load(open(X_TRAIN_PICKLE_FILE, 'rb'))
Y_train = pickle.load(open(Y_TRAIN_PICKLE_FILE, 'rb'))

# Both are tuples with structure (cities, filenames, inp, out) - we want last elements
print("Reformatting data.")
X = X_train[3]
Y = Y_train[3]

# Get shape for later use
n, d = X.shape

if DO_LEARN:
    # Both X and Y have shape (None, 512)
    # Now, simply learn linear scale factors between every feature of input and outuput
    # General structure for lin reg taken from the following sources:
    # http://scikit-learn.org/stable/auto_examples/linear_model/plot_ols.html
    # http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html#sklearn.linear_model.Lasso
    print("Creating model for type {}.".format(MODEL_TYPE))
    if MODEL_TYPE != 'neural_normalizer' and MODEL_TYPE != 'neural_normalizer_pos':
        # Load from pickle file to save training time
        try:
            model = pickle.load(open(MODEL_TYPE + '.p', 'rb'))
        except:
            # No model needed here - continue
            pass

    else:
        # Create neural network, simple one layer
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

    elif MODEL_TYPE == 'simple_linear' or MODEL_TYPE == 'lasso':
        # We are going with regression for this normalization
        score = model.score(X, Y)
        pred = model.predict(X)

        # Trim all negative values for our purposes here
        pred[pred < 0] = 0

    elif MODEL_TYPE == 'global':
        # Apply traffic and wait scale factors to matrix
        # First, create this alternating factor matrix
        matrix = np.tile(np.array([TRAFFIC_SCALE, WAIT_SCALE]), d // 2)

        # Need to repeat for multiplication
        matrix = np.repeat(matrix, n, axis = 0).reshape((n, d))

        # Run our prediction
        pred = np.multiply(matrix, X)
        score = r2_score(pred, Y)

    elif MODEL_TYPE == 'matrix':
        # Load matrix from local pickle file
        matrix = pickle.load(open(SCALE_MATRIX_FILENAME, 'rb'))

        # Need to repeat for multiplication
        matrix = np.repeat(matrix, n, axis = 0).reshape((n, d))

        # Run our prediction
        pred = np.multiply(matrix, X)
        score = r2_score(pred, Y)

    # Show R^2 and accuracy values
    accuracy = utils.compute_accuracy(Y, pred)
    print("R^2 score:", score)
    print("Percent accuracy:", accuracy)

    if WRITE_FILES:
        # pred object is n x 512 np matrix
        # Now, need to write to JSON
        train_cities = X_train[0]
        filenames = Y_train[1]
        # Need to write this data to train_cities
        for i, city in tqdm(enumerate(train_cities)):
            # Get new data and filename to write
            new_data, filename = pred[i], filenames[i]
            # Add normalized data to the city structure itself
            utils.output_to_city(city, new_data)
            j = city.to_json()
            # Write this JSON to new filename and output
            with open(OUTPUT_PATH + filename + '_normalized.json', 'w') as f:
                f.write(j)
            if i == MAX_OUTPUT_NUM:
                break

    # Write to pickle file for later retreival
    # print("Saving model locally.")
    # if MODEL_TYPE != 'neural_normalizer' and MODEL_TYPE != 'neural_normalizer_pos':
    #   pickle.dump(model, open(MODEL_TYPE + '.p', 'wb'))
else:
    # Calculate sums of predicted and simulation data
    # But, need traffic and wait sums separately
    # Use np array splicing here
    pred_traffic = X[:, ::2].sum()
    pred_wait = X[:, 1::2].sum()
    sim_traffic = Y[:, ::2].sum()
    sim_wait = Y[:, ::2].sum()

    # Calculate scale factors for traffic and wait
    traffic_scale = sim_traffic / pred_traffic
    wait_scale = sim_wait / pred_wait
    print("Traffic scale factor:", traffic_scale)
    print("Wait scale factor:", wait_scale)

    # Testing with more complex one...
    # Try to get 1 x 512 sum vector for each component
    pred_sum_new = X.sum(axis = 0)
    sim_sum_new = Y.sum(axis = 0)

    # Divide two (512, ) matrices to get multiplicative factor
    scale_new = sim_sum_new / pred_sum_new
    scale_new[pred_sum_new == 0] = 1 # Replace 0 values to prevent division errors

    # Write scale_matrix to pickle file
    print("Writing to pickle file.")
    pickle.dump(scale_new, open(SCALE_MATRIX_FILENAME, 'wb'))

print("Process complete.")