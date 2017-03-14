# 0. Load output JSON files.

import glob, json, time, numpy as np
from sklearn.kernel_ridge import KernelRidge

directory = ''

# Utils

POP_ARR = [5, 8, 16, 16, 23, 59]

def get_population(t, density_array):
	if t not in range(0, 6):
		return 0
	return density_array[t] * POP_ARR[t]

def extract_data(directory):

	files = glob.glob(directory)

	inp = [] # Input feature matrix
	out = [] # Output feature matrix

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
				if 'data' in cell:
					current_output.append(cell['data']['traffic'])
					current_output.append(cell['data']['wait'])
				else:
					current_output.append(0)
					current_output.append(0)
			inp.append(np.array(current_input))
			out.append(np.array(current_output))

	inp = np.array(inp)
	out = np.array(out)

	return (inp, out)

train_x, train_y = extract_data('../../../data/train/*.json')
test_x, test_y = extract_data('../../../data/test/*.json')

# 2. Create ridge regression model and train on training data.

# TODO. Tune gamma.

clf = KernelRidge(kernel='rbf', gamma=0.1, alpha = 1.0)

clf.fit(train_x, train_y)

# 3. Run predictions on test data.

# y = clf.predict(test_x)

# print(y)

print(clf.score(test_x, test_y)) # Prediction score?

# Current train/test breakdown.

# Train = [1, 2, 3, 4, 5] <- 5000

# Test = [9, 10] <- 2000