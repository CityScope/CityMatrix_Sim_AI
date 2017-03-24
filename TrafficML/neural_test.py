# 0. Load output JSON files.

import glob, json, time, numpy as np, pickle, os, tensorflow as tf
from keras.models import Sequential, model_from_json
from keras.layers import Dense, Dropout, Flatten, Reshape
from keras.layers.convolutional import Convolution2D

init = tf.initialize_all_variables()
sess = tf.Session()
sess.run(init)

# Data methods

def normalize(data):
    return np.array(data) / max(np.max(data), np.abs(np.min(data)))

def residuals(expected, predicted):
    return expected - predicted
    
def normalized_residuals(expected, predicted):
    return residuals(normalize(expected), normalize(predicted))
    
def total_sum_squares(expectedVals):
    mean = np.mean(expectedVals)
    
    diffSum = [np.sum(expected - mean)**2 for expected in expectedVals]
    return np.sum(diffSum)
    
def residual_sum_squares(expectedVals, predictedVals):
    assert len(expectedVals) == len(predictedVals)
    
    res = []
    for i in range(len(expectedVals)):
        res.append(residuals(expectedVals[i], predictedVals[i]))
    return np.sum(np.array(res)**2)
    
def R_squared(expectedVals, predictedVals):
    sumRes = residual_sum_squares(expectedVals, predictedVals)
    sumTot = total_sum_squares(predictedVals)
    
    return 1 - (sumRes / sumTot)

# 1. Load data from pickle file.

data = pickle.load(open('data.p', 'rb'))
train_x = data['train_x'].reshape((-1, 16, 16, 2))
train_y = data['train_y'].reshape((-1, 16, 16, 2))
test_x = data['test_x'].reshape((-1, 16, 16, 2))
test_y = data['test_y'].reshape((-1, 16, 16, 2))

# 2. Create model. Convolutional neural network.

start_time = time.time()
print('Compiling Model ... ')

model = Sequential()
model.add(Convolution2D(64, 3, input_shape=(16, 16, 2), nb_col=1))
# model.add(Dropout(0.5))
model.add(Flatten())
model.add(Dense(512, activation='relu'))
model.add(Reshape((16, 16, 2)))

# 3. Compile model.

def loss(y_true, y_pred):
	with sess.as_default():
		print(y_true.get_shape())

model.compile(loss=loss, optimizer='adam', metrics=['accuracy'])

print('Model compield in {0} seconds'.format(time.time() - start_time))

# 4. Train the network.

start_time = time.time()
print('Training model...')

model.fit(train_x, train_y, nb_epoch=5, batch_size=128, verbose=1)

print("Training duration : {0}".format(time.time() - start_time))

# Serialize model to JSON
# Taken from http://machinelearningmastery.com/save-load-keras-deep-learning-models/



model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# Serialize weights to HDF5
model.save_weights("model.h5")
print("Saved model to disk.")



# Load model from JSON

json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model.h5")
print("Loaded model from disk.")

# 5. Test network on train data. Check that everything is okay. ***

predicted_first_city = model.predict(train_x[0].reshape(-1, 16, 16, 2))[0]

def compare(inp, one, two):
	# Get R^2 between two cities, only based on road cells...
	print(inp.shape)
	print(one.shape)
	print(two.shape)
	first_traffic = []
	second_traffic = []
	first_wait = []
	second_wait = []
	for row in range(inp.shape[0]):
		for col in range(inp.shape[1]):
			if inp[row][col][1] == 1:
				# Is a road.
				first_traffic.append(one[row][col][0])
				second_traffic.append(two[row][col][0])
				first_wait.append(one[row][col][1])
				second_wait.append(two[row][col][1])
	print(first_traffic)
	print(second_traffic)
	return (R_squared(first_traffic, second_traffic), R_squared(first_wait, second_wait))

a, b = compare(train_x[0], train_y[0], predicted_first_city)

print(a, b)

# score = model.evaluate(X_test, y_test, batch_size=16)

# print("Network's test score [loss, accuracy]: {0}".format(score))

print("Process complete!")