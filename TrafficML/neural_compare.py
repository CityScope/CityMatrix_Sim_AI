'''
File name: neural_compare.py
Author: Kevin Lyons
Date created: 4/17/2017
Date last modified: 4/17/2017
Python Version: 3.5
Purpose: Compare the outputs of my CNN to get R^2 results. Much of this code is taken directly from Alex's city_compare file.
'''

import sys

sys.path.append('../')

from city_compare import *

def compare_outputs(sim, pred):
	'''

	Inputs:
	
	sim - (None, 512) np matrix of simulation outputs
	pred - (None, 512) np matrix of neural network predicted outputs

	Outputs:

	Data regarding the integrity of our CNN predictions, of the following form.

	lines = [
	"R Squared:" + str(R_squared(expected_vals, predicted_vals)),
	"Residuals:", "\tMean: " + str(np.average(res)),
	"\tCity Sum Mean: " + str(np.mean([np.sum(c) for c in res])),
	"\tMax: " + str(np.max(res)), "\tMin: " + str(np.min(res)),
	"\tSum: " + str(np.sum(res)),
	"\tStandard Deviation: " + str(np.std(res)),
	"Normalized Residuals:", "\tMean: " + str(np.average(norm_res)),
	"\tCity Sum Mean: " + str(np.mean([np.sum(c) for c in norm_res])),
	"\tMax: " + str(np.max(norm_res)),
	"\tMin: " + str(np.min(norm_res)),
	"\tSum: " + str(np.sum(norm_res)),
	"\tStandard Deviation: " + str(np.std(norm_res))
	]

	'''

	r_sqrd = R_squared(sim, pred)
	res = np.array([residuals(e, p) for e, p in zip(sim, pred)])
	norm_res = np.array([normalized_residuals(e, p) for e, p in zip(sim, pred)])
	norm_res = norm_res[~np.isnan(norm_res).any(axis=1)]

	result = [
		"R Squared:" + str(R_squared(sim, pred)),
		"Residuals:", "\tMean: " + str(np.average(res)),
		"\tCity Sum Mean: " + str(np.mean([np.sum(c) for c in res])),
		"\tMax: " + str(np.max(res)), "\tMin: " + str(np.min(res)),
		"\tSum: " + str(np.sum(res)),
		"\tStandard Deviation: " + str(np.std(res)),
		"Normalized Residuals:", "\tMean: " + str(np.average(norm_res)),
		"\tCity Sum Mean: " + str(np.mean([np.sum(c) for c in norm_res])),
		"\tMax: " + str(np.max(norm_res)),
		"\tMin: " + str(np.min(norm_res)),
		"\tSum: " + str(np.sum(norm_res)),
		"\tStandard Deviation: " + str(np.std(norm_res))
	]

	print('\n'.join(result))