# 0. Load output JSON files.

import glob, json, time, numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Reshape
from keras.constraints import maxnorm
from keras.optimizers import SGD
from keras.layers.convolutional import Conv2D
from keras.utils import np_utils
from keras import backend as K
K.set_image_dim_ordering('th')

directory = '../../../data/train/*.json'

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
			current_input.append(int(cell['type'] == 6))
			if 'data' in cell:
				current_output.append(cell['data']['traffic'])
				current_output.append(cell['data']['wait'])
			else:
				current_output.append(0)
				current_output.append(0)
		train_inp.append(np.array(current_input))
		train_out.append(np.array(current_output))

# Reshaping data into 2D matrix form

train_inp = np.array(train_inp)
train_out = np.array(train_out)

train_inp = train_inp.reshape((-1, 16, 16, 2))
train_out = train_out.reshape((-1, 16, 16, 2))

# 2. Create model. Convolutional neural network.

start_time = time.time()
print('Compiling Model ... ')

model = Sequential()
model.add(Conv2D(64, 3, input_shape=(16, 16, 2), nb_col=1))
model.add(Dropout(0.2))
# model.add(MaxPooling1D(pool_length=4))
model.add(Flatten())
# model.add(Dense(512, activation='relu', W_constraint=maxnorm(3)))
# model.add(Dropout(0.5))
model.add(Dense(512, activation='linear'))
model.add(Reshape((16, 16, 2)))

# 3. Compile model.

epochs = 25
lrate = 0.01
decay = lrate/epochs
sgd = SGD(lr=lrate, momentum=0.9, decay=decay, nesterov=False)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
print(model.summary())

print('Model compield in {0} seconds'.format(time.time() - start_time))

# 4. Train the network.
start_time = time.time()
print('Training model...')

model.fit(train_inp, train_out, nb_epoch=200, batch_size=20, verbose=1)

print("Training duration : {0}".format(time.time() - start_time))

# 5. Test network on new data. Make predictions and compare cities. ***

# score = model.evaluate(X_test, y_test, batch_size=16)

# print("Network's test score [loss, accuracy]: {0}".format(score))