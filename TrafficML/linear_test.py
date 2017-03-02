# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 23:03:34 2017

@author: Alex
"""
import os

import sys
sys.path.insert(0, '../TrafficTreeSim/')
import cityiograph

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression

ROAD_ID = 6

def cell_features(cell):
    feats = []
    feats.append(cell.density)
    feats.append(0) if (cell.type_id == ROAD_ID) else feats.append(1)
    return feats

def cell_results(cell):
    results = []
    results.append(cell.data["traffic"])
    results.append(cell.data["wait"])
    return results
    
def city_features(city):
    feats = []
    return feats
    
def city_results(city):
    results = []
    return results

input_vectors = []
output_vectors = []

input_dir = "./data/input/"
output_dir = "./data/output/"

print "Preparing input vectors"
for filename in os.listdir(input_dir):
    json = open(input_dir + filename).read()
    city = cityiograph.City(json)
    
    new_vector = []
    
    for i in range(city.width):
        for j in range(city.height):
            cell = city.cells.get((i, j))
            new_vector += cell_features(cell)

    new_vector += city_features(city)
    input_vectors.append(new_vector)

input_vectors = np.array(input_vectors)
print "Input size: " + str(input_vectors.shape)    

print "Preparing output vectors"
for filename in os.listdir(output_dir):
    json = open(output_dir + filename).read()
    city = cityiograph.City(json)
    
    new_vector = []
    
    for i in range(city.width):
        for j in range(city.height):
            cell = city.cells.get((i, j))
            new_vector += cell_results(cell)

    new_vector += city_results(city)
    output_vectors.append(new_vector)
    
output_vectors = np.array(output_vectors)
print "Output size: " + str(output_vectors.shape)    

print "Splitting dataset"
X_train, X_test, y_train, y_test = train_test_split(
         input_vectors, output_vectors, test_size=0.25, random_state=0)

print "Training linear model"
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
"""
print "Training logistic model"
logistic_model = LogisticRegression()
logistic_model.fit(X_train, y_train)
"""
linear_score = linear_model.score(X_test, y_test)
#logistic_score = logistic_model.score(X_test, y_test)
print "Linear Score: ", linear_score
#print "Logistic Score: ", logistic_score








    
    
    