# 0. Load output JSON files.

import glob, json, time, numpy as np, matplotlib.pyplot as plt
from sklearn.kernel_ridge import KernelRidge
import pickle
# Utils

POP_ARR = [5, 8, 16, 16, 23, 59]

def print_array(b):
	for row in b:
		for c in row:
			print(str(c) + ",	", end='')
		print('')

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
				current_input.append(int(cell['type'] == 6))
				if 'data' in cell:
					current_output.append(cell['data']['traffic'])
					current_output.append(cell['data']['wait'])
				else:
					current_output.append(0)
					current_output.append(0)
			inp.append(np.array(current_input))
			out.append(np.array(current_output))

	inp = np.array(inp).astype(int)
	out = np.array(out).astype(int)

	return (inp, out)

# Data manager...

print('Extracting data...')

train_x, train_y = extract_data('../../../data/train/*.json')
test_x, test_y = extract_data('../../../data/test/*.json')

train_x = np.vstack((train_x, test_x))
train_y = np.vstack((train_y, test_y))

variables = {'train_x':train_x,'train_y':train_y,'test_x':test_x,'test_y':test_y}
pickle.dump(variables, open('neural_data.p','wb'))

data = pickle.load(open('neural_data.p', 'rb'))
train_x = data['train_x'].reshape((-1, 16, 16, 2))
train_y = data['train_y'].reshape((-1, 16, 16, 2))
test_x = data['test_x'].reshape((-1, 16, 16, 2))
test_y = data['test_y'].reshape((-1, 16, 16, 2))

print('Successfully extracted data.')

# # 2. Create ridge regression model and train on training data.

# # TODO. Tune gamma.

# print('Fitting data to KRR model...')

# clf = KernelRidge(kernel='rbf')

# clf.fit(train_x, train_y)

# print (clf.predict(train_x[0]))

# print(clf.score(test_x, test_y)) # Prediction score?

# Current train/test breakdown.

# Train = [1, 2, 3, 4, 5, 6] <- 6000 examples

# Test = [9, 10] <- 2000 examples

# 3x3 Conv and 5x5 and combine <- zero padding, building or road whaterver - low population

# Reshape

# FC downstream

# Try logistical first

# Init Gaussian distribution.

x = np.meshgrid(np.linspace(-2, 2, 31), np.linspace(-2, 2, 31))

x = (x[0]**2 + x[1]**2)**(1/2)

from scipy.stats import norm

r = norm.pdf(x)*-2

b = r * -1

# plt.imshow(x)

# plt.show()

def evaluate_map(grid, r, b):
	scores = np.zeros(grid.shape[0:2])

	for i in range(len(grid)):
		for j in range(len(grid[0])):
			if grid[i][j][1] == 1:
				# It's a road - update score
				scores[i][j] = evaluate_cell(i, j, grid, r, b)

	return scores

def evaluate_cell(x, y, grid, r, b):
	# Return a score here

	# Update the score at a cell

	# Just considering traffic

	score = 0

	for i in range(int(-len(r)/2), int(len(r)/2 + 1)):
		for j in range(int(-len(r[0])/2), int(len(r[0])/2 + 1)):
			if x + i >= 0 and x + i < len(grid) - 1 and y + j >= 0 and y + j < len(grid[0]) - 1:
				# Evaluate the cell
				# If road
				if grid[x + i][y + j][1] == 1:
					# we are a road
					score += r[i][j]
				else:
					score += b[i][j]*grid[x + i][y + j][0]

	return score

format_y = np.delete(train_y, 1, 3)

print(format_y[0].shape)

a = evaluate_map(train_x[0], r, b)

a /= a.max()

# plot_data(train_x[0])

# plt.imshow(a, alpha=0.5)
# plt.show('hold')