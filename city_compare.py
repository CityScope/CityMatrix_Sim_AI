# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 17:22:44 2017

@author: Alex
"""
import sys
import os

import numpy as np

sys.path.insert(0, 'TrafficTreeSim/')
import cityiograph

sys.path.insert(0, 'TrafficML/')
import traffic_regression as TR

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
    
"""
City focused functions.

"""

CITY_STATS = [("residuals", residuals),
              ("norm_residuals", normalized_residuals)]

def get_data(city):
    return np.array(TR.get_results(city)).astype(float)
    
def city_stats(expectedCity, predictedCity):
    stats = {}
    for name, fun in CITY_STATS:
        stats[name] = fun(expectedCity, predictedCity)
    return stats
    
    
if __name__ == "__main__":
    output_dir = "./TrafficML/data/output/"
    prediction_dir = "./TrafficML/data/prediction/linear/"
    
    stats = []

    expected_vals = []
    predicted_vals = []

    for filename in os.listdir(output_dir):
        expectedCity = cityiograph.City(open(output_dir + filename).read())
        predictedCity = cityiograph.City(open(prediction_dir + filename).read())
        
        expected = get_data(expectedCity)
        predicted = get_data(predictedCity)
        
        expected_vals.append(expected)
        predicted_vals.append(predicted)
        
        stats.append(city_stats(expected, predicted))
    
    r_squared = R_squared(expected_vals, predicted_vals)
        
        


    
