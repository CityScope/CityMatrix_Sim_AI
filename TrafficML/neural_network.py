# 0. Load output JSON files.

import glob, json, numpy as np, pickle, os, matplotlib.pyplot as plt, tensorflow as tf
from keras.models import Model, model_from_json
from keras.layers import Input, Dense, Flatten, Reshape
from keras.layers.merge import Concatenate
from keras.layers.convolutional import Conv2D
import keras.backend as K

# Custom file imports

from neural_server import serialize_model, deserialize_model
from data_manager import CITIES_PICKLE_FILENAME, FEATURES_PICKLE_FILENAME, extract_train_test

# 1. Load data from pickle file.

# print("Loading data from pickle file.")

# cities_dictionary = pickle.load(open(CITIES_PICKLE_FILENAME, 'rb'))

# train_cities = cities_dictionary['train_cities']
# test_cities = cities_dictionary['test_cities']

print("Extracting features from cities.")

# train_x, train_y = extract_train_test(train_cities)
# test_x, test_y = extract_train_test(test_cities)

# features_tuple = (train_x, train_y, test_x, test_y)

# pickle.dump(features_tuple, open(FEATURES_PICKLE_FILENAME, 'wb'))

train_x, train_y, test_x, test_y = pickle.load(open(FEATURES_PICKLE_FILENAME, 'rb'))

print("Successfully extracted features from cities.")

print(train_x[0])
print(train_y[0])

# train_x = data['train_x'].reshape((-1, 16, 16, 2))
# train_y = data['train_y'].reshape((-1, 16, 16, 2))
# test_x = data['test_x'].reshape((-1, 16, 16, 2))
# test_y = data['test_y'].reshape((-1, 16, 16, 2))

# 2. Create model. Convolutional neural network.

print('Compiling Model ... ')

inp = Input(shape=(16, 16, 2), name='input_layer')
x = Conv2D(128, (5, 5), activation='relu', input_shape=(16, 16, 2))(inp)
x = 
x = Conv2D(32, (3, 3), activation='relu', input_shape=(12, 12, 128))(x)
x = Flatten()(x)
# x = Dense(512, activation='relu')(x)
x = Dense(512, activation='relu')(x)
x = Reshape((16, 16, 2))(x)
y = Concatenate()([x, inp])

model = Model(inputs=inp, outputs=x)
# print(model.summary())

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

model.compile(loss='mse', optimizer='sgd', metrics=['accuracy']) # custom_accuracy

print("Successfully compiled model.")

# 4. Train the network.

print("Fitting model.")

model.fit(train_x, train_y, epochs=1, batch_size=128, verbose=1)

# Serialize model to file

serialize_model(model)

print("Serialized!!!")

# Deserialize model from file

# model = deserialize_model()

# model.compile(loss=custom_loss, optimizer='adam', metrics=[custom_accuracy])

# print("Deserialized!!!")

first_city = model.predict(train_x[1:2])[0]

first_city = np.delete(first_city, [2, 3], 2).astype(int)

print(first_city)

print(first_city.shape)

print(train_y[1])

mse = ((first_city - train_y[1]) ** 2).mean(axis=None)

print("Mean squared error = {}.".format(mse))

loss = custom_loss(train_x[1], first_city)

print("Custom loss function = {}.".format(loss))

train_score = model.evaluate(train_x, train_y, batch_size=16)

print("Network's train score [loss, accuracy]: {0}".format(train_score))

score = model.evaluate(test_x, test_y, batch_size=16)

print("Network's test score [loss, accuracy]: {0}".format(score))

print("Process complete!")