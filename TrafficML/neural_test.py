# 0. Load output JSON files.

import glob, json, time, numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.constraints import maxnorm
from keras.optimizers import SGD
from keras.layers.convolutional import Convolution1D
from keras.layers.convolutional import MaxPooling1D
from keras.utils import np_utils
from keras import backend as K
K.set_image_dim_ordering('th')

directory = '../../../data/machine_1/*.json'

files = glob.glob(directory)

# 1. Convert files to input and output feature vectors.

train_inp = []
train_out = []

POP_ARR = [5, 8, 16, 16, 23, 59]

def get_population(t, density_array):
	if t not in range(0, 6):
		return 0
	return density_array[t] * POP_ARR[t]

for name in files:
	with open(name, 'r') as f:
		current_input = []
		current_output = []
		d = json.loads(f.read())
		max_traffic = max([cell['data']['traffic'] for cell in d['grid'] if 'data' in cell])
		max_wait = max([cell['data']['wait'] for cell in d['grid'] if 'data' in cell])
		if max_traffic == 0 or max_wait == 0:
			continue
		for cell in d['grid']:
			current_input.append(get_population(cell['type'], d['objects']['density']))
			# current_input.append(int(cell['type'] == 6))
			if 'data' in cell:
				current_output.append(cell['data']['traffic']/max_traffic)
				current_output.append(cell['data']['wait']/max_wait)
			else:
				current_output.append(0)
				current_output.append(0)
		train_inp.append(np.array(current_input))
		train_out.append(np.array(current_output))

train_inp = np.array(train_inp)
train_out = np.array(train_out)

print(train_inp.shape)

# 2. Create model. Convolutional neural network.

start_time = time.time()
print('Compiling Model ... ')

model = Sequential()
model.add(Convolution1D(64, 4, input_dim=256, border_mode='same', activation='relu', W_constraint=maxnorm(3)))
model.add(Dropout(0.2))
model.add(Convolution1D(64, 4, activation='relu', border_mode='same', W_constraint=maxnorm(3)))
model.add(MaxPooling1D(pool_length=4))
# model.add(Flatten())
model.add(Dense(512, activation='relu', W_constraint=maxnorm(3)))
model.add(Dropout(0.5))
model.add(Dense(512, activation='linear'))
# Compile model
epochs = 25
lrate = 0.01
decay = lrate/epochs
sgd = SGD(lr=lrate, momentum=0.9, decay=decay, nesterov=False)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
print(model.summary())

print('Model compield in {0} seconds'.format(time.time() - start_time))

# 3. Train the network.
start_time = time.time()
print('Training model...')

model.fit(train_inp, train_out, nb_epoch=200, batch_size=20, verbose=1)

print("Training duration : {0}".format(time.time() - start_time))

# score = model.evaluate(X_test, y_test, batch_size=16)

# print("Network's test score [loss, accuracy]: {0}".format(score))