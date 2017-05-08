'''
    File name: normalizer.py
    Author: Kevin Lyons, Alex Aubuchon
    Date created: 5/8/2017
    Date last modified: 5/8/2017
    Python Version: 3.5
    Purpose: Developing a simple linear regression model that can re-normalize all ouputs of the CityMatrix TrafficML CNN to more closely match those of actual simulation outputs. The overall structure will be quite  simple. We will take in predicted cities as X, actual cities as Y, and learn a scalar mapping X -> Y. I will use sklearn framework here for its simplicity and functionality.
'''

# Global import statements
import glob, pickle, sys

# Learning imports
from sklearn import linear_model

# Custom imports
sys.path.insert(0, '../TrafficTreeSim/')
import cityiograph

# Gobal latent parameters
NB_EPOCH = 50
BATCH_SIZE = 32
VERBOSE = 1

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
regressor = linear_model.Lasso(positive = True) # Force all coefficients to be positive

# Now, fit the model to our X and Y data
print("Fitting model to our dataset.")
regressor.fit(X, Y)

# Analyze results
weights = regressor.coef_
print(weights)
print(weights.shape)
test = regressor.predict(X[1])
print(test)
print(test.shape)

# Original results are not great, but promising. I am getting some negative weights, which we do not want for our application. I am looking for solutions to this *constrained* linear regression problem, one of which is the linear_model.Lasso option from sklearn. Consulting with Alex on this.

print("Process complete.")