# 0. Load output JSON files.

import glob, json, numpy as np, pickle, os, matplotlib.pyplot as plt, tensorflow as tf
from keras.models import Model, model_from_json
from keras.layers import Input, Dense, Flatten, Reshape
from keras.layers.merge import Concatenate
from keras.layers.convolutional import Conv2D
import keras.backend as K

from neural_server import serialize_model

DATA_FILENAME = './neural_data.p'

"""
Statistical extraction functions.

Each expect raw data, nothing to do with the city structure
"""
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

data = pickle.load(open(DATA_FILENAME, 'rb'))
train_x = data['train_x'].reshape((-1, 16, 16, 2))
train_y = data['train_y'].reshape((-1, 16, 16, 2))
test_x = data['test_x'].reshape((-1, 16, 16, 2))
test_y = data['test_y'].reshape((-1, 16, 16, 2))

print(train_x.shape)
print(train_y.shape)

# 2. Create model. Convolutional neural network.

print('Compiling Model ... ')

inp = Input(shape=(16, 16, 2), name='input_layer')
x = Conv2D(128, (5, 5), activation='relu', input_shape=(16, 16, 2))(inp)
# x = Conv2D(32, (3, 3), activation='relu', input_shape=(12, 12, 128))(x)
x = Flatten()(x)
x = Dense(512, activation='relu')(x)
x = Reshape((16, 16, 2))(x)
y = Concatenate()([x, inp])

model = Model(inputs=inp, outputs=y)
print(model.summary())

# 3. Compile model.

def custom_loss(y_true, y_pred):
	y_pred, inp = tf.split(y_pred, 2, 3)
	# y_true is (16, 16, 2) - traffic and wait for each cell
	# y_pred is (16, 16, 2) - traffic and wait for each cell
	# inp is (16, 16, 2) - population and isroad for each cell
	_, road = tf.split(inp, 2, 3)
	# road is (16, 16, 1) - 1 if road, else 0
	# now, repeat road once along axis dim = 2
	road = tf.tile(road, [1, 1, 1, 2])
	# road is now (16, 16, 2)
	diff = tf.subtract(y_true, y_pred)
	sq = tf.square(diff)
	mul = tf.multiply(road, sq)
	error = tf.reduce_sum(mul) / tf.reduce_sum(road)
	return error

def custom_accuracy(y_true, y_pred):
	y_pred, inp = tf.split(y_pred, 2, 3)
	# y_true is (16, 16, 2) - traffic and wait for each cell
	# y_pred is (16, 16, 2) - traffic and wait for each cell
	# inp is (16, 16, 2) - population and isroad for each cell
	_, road = tf.split(inp, 2, 3)
	# road is (16, 16, 1) - 1 if road, else 0
	# now, repeat road once along axis dim = 2
	road = tf.tile(road, [1, 1, 1, 2])
	# road is now (16, 16, 2)
	sim = tf.to_float(tf.multiply(road, y_true))
	pred = tf.to_float(tf.multiply(road, y_pred))
	diff = tf.abs(tf.subtract(sim, pred))
	denom_raw = tf.maximum(sim, pred)
	cond = tf.equal(tf.zeros_like(denom_raw), denom_raw)
	ones = tf.ones_like(denom_raw)
	denom = tf.where(cond, ones, denom_raw)
	errors = tf.divide(diff, denom)
	return 1 - tf.reduce_mean(errors)

print("Compiling model.")

model.compile(loss=custom_loss, optimizer='adam', metrics=[custom_accuracy])

# 4. Train the network.

print("Fitting model.")

model.fit(train_x, train_y, epochs=10, batch_size=128, verbose=1)

# pickle.dump(model, open('./neural_model.pkl', 'wb'))

# Write the model to a local file.

serialize_model(model)

print("Serialized!!!")

# 5. Test network on train data. Check that everything is okay. ***

index = 256

# predicted_first_city = model.predict(train_x[index].reshape(-1, 16, 16, 2))[0]

def compare(inp, one, two):
	# Get R^2 between two cities, only based on road cells...
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
	return (R_squared(first_traffic, second_traffic), R_squared(first_wait, second_wait))

# a, b = compare(train_x[0], train_y[0], predicted_first_city)

# print(a, b)

def plot_results(inp, train, predicted):

	# Goal - compare the traffic scores of train data and predicted data...

	pop_matrix = np.zeros((16, 16))
	train_matrix = np.zeros((16, 16))
	p_matrix = np.zeros((16, 16))

	maxPop = float(inp.max())
	maxTraffic_train = float(train.max())
	maxTraffic_predicted = float(predicted.max())

	print(predicted.shape)

	for i in range(16):
		for j in range(16):
			if inp[i][j][1] == 1:
				# Road cell - we want to plot traffic data here
				pop_matrix[i][j] = -1
				train_matrix[i][j] = train[i][j][0] / maxTraffic_train
				p_matrix[i][j] = predicted[i][j][0] / maxTraffic_predicted
			else:
				pop_matrix[i][j] = inp[i][j][0] / maxPop
				train_matrix[i][j], p_matrix[i][j] = -1, -1

	_, one = plt.subplots()
	one.imshow(pop_matrix, interpolation='nearest')

	_, two = plt.subplots()
	two.imshow(train_matrix, interpolation='nearest')

	_, three = plt.subplots()
	three.imshow(p_matrix, interpolation='nearest')

# plot_results(train_x[index], np.delete(train_y[index], 0, 2), np.delete(predicted_first_city, 0, 2))

# plt.show('hold')

# score = model.evaluate(X_test, y_test, batch_size=16)

# print("Network's test score [loss, accuracy]: {0}".format(score))

print("Process complete!")