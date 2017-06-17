# Global imports
import glob, json, numpy as np, pickle, os, tensorflow as tf, sys, os

# Keras imports
from keras.models import Model, model_from_json
from keras.layers import Input, Dense, Flatten, Reshape
from keras.layers.merge import Concatenate
from keras.layers.convolutional import Conv2D
import keras.backend as K

# Custom local imports
sys.path.append('../global/')
import utils
from config import *
# from neural_server import serialize_model, deserialize_model
# from traffic_regression import output_to_city

# Variable declarations
TRAIN_DATA_FILENAME = '../../../data/no_wandering_data_train.p'
TEST_DATA_FILENAME = '../../../data/no_wandering_data_test.p'
PREDICTION_OUTPUT_DIR = 'no_wandering_neural_predictions/'
DO_RUN = False
ROOT_FILENAME = "no_wandering_cnn"

# Create prediction dir if does not already exist
if not os.path.exists(PREDICTION_OUTPUT_DIR):
    os.makedirs(PREDICTION_OUTPUT_DIR)

# 1. Load data from pickle files.
print("Loading data...")

train_cities, train_filenames, train_x, train_y = pickle.load(open(TRAIN_DATA_FILENAME, 'rb'))
test_cities, test_filenames, test_x, test_y = pickle.load(open(TEST_DATA_FILENAME, 'rb'))

print(len(test_cities), len(test_filenames), len(test_x), len(test_y))

train_x = train_x.reshape((-1, 16, 16, 2))
train_y = train_y.reshape((-1, 16, 16, 2))
test_x = test_x.reshape((-1, 16, 16, 2))
test_y = test_y.reshape((-1, 16, 16, 2))

print("Successfully loaded data.")

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

if DO_RUN:
    # 2. Create model. Convolutional neural network.
    print('Compiling Model ... ')

    inp = Input(shape=(16, 16, 2), name='input_layer')
    x = Conv2D(128, (5, 5), activation='relu', input_shape=(16, 16, 2))(inp)
    # x = Conv2D(32, (3, 3), activation='relu', input_shape=(12, 12, 128))(x)
    x = Flatten()(x)
    x = Dense(512, activation='relu')(x)
    x = Reshape((16, 16, 2))(x)
    # y = Concatenate()([x, inp])

    model = Model(inputs=inp, outputs=x)
    print(model.summary())

    # 3. Compile model.
    print("Compiling model.")
    model.compile(loss = LOSS_FUNCTION, optimizer = OPTIMIZER, metrics = KERAS_METRICS)

    # 4. Train the network.
    print("Fitting model.")
    model.fit(train_x, train_y, epochs = 12, batch_size = 128, verbose = 1)

    # Serialize model to file
    # utils.serialize_model(model, ROOT_FILENAME)
    # print("Serialized!!!")
else:
    # Or, deserialize model from file
    model = utils.deserialize_model(ROOT_FILENAME)
    model.compile(loss = LOSS_FUNCTION, optimizer = OPTIMIZER, metrics = KERAS_METRICS)
    print("Deserialized!!!")

# score = model.evaluate(test_x, test_y, batch_size = 16)
# print("Network's test score [loss, accuracy]: {0}".format(score))

print("Predicting test cities...")

predictions = model.predict(test_x)

print(predictions.shape)

# Write predictions to new JSON files in PREDICTION_OUTPUT_DIR

for i, city in enumerate(test_cities):
    output_filename = PREDICTION_OUTPUT_DIR + test_filenames[i] + '_prediction.json' # Filename formatting
    output_list = predictions[i].reshape(512).tolist() # Convert matrix to list
    utils.output_to_city(city, output_list) # Update city with these values
    json_string = city.to_json() # Convert to JSON string
    with open(output_filename, 'w') as f: # Write new JSON prediction to file
        f.write(json_string)

print("Wrote all predictions to {}.".format(PREDICTION_OUTPUT_DIR))

# Compare results with R^2 analysis

# from neural_compare import *

# sim = test_y.reshape((-1, 512))
# pred = predictions.reshape((-1, 512))
# compare_outputs(sim, pred)

print("Process complete!")