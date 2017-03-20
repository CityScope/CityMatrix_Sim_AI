# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 17:22:44 2017

@author: Alex
"""
import sys
import os

import numpy as np

sys.path.insert(0, 'TrafficTreeSim/')
from cityiograph import *

sys.path.insert(0, 'TrafficML/')
import traffic_regression as TR

"""
Statistical extraction functions.

Each expect raw data, nothing to do with the city structure
"""

def residuals(expected, predicted):
    return expected - predicted
            
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
    sumRes = residual_sum_squares(expectedVals)
    sumTot = total_sum_squares(predictedVals)
    
    return 1 - (sumRes / sumTot)
    
"""
City focused functions.

"""

def get_data(city):
    return TR.get_results(city)
    

    
