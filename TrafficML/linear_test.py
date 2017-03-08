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
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn import tree
from sklearn.pipeline import make_pipeline

ROAD_ID = 6
POP_ARR = [5, 8, 16, 16, 23, 59]

def density_to_pop(type_id, density):
    if type_id not in range(len(POP_ARR)):
        return 0
    return density * POP_ARR[type_id]

def cell_features(cell):
    feats = []
    feats.append(density_to_pop(cell.type_id, cell.density))
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

def output_to_city(city, output):
    i = 0
    for x in range(city.width):
        for y in range(city.height):
            cell = city.cells.get((x,y))
            cell.data["traffic"] = int(round(output[i]))
            cell.data["wait"] = int(round(output[i + 1]))
            i += 2
        
cities = []    
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
    cities.append(city)

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
print "Output size:", output_vectors.shape  

print "Splitting dataset"
X_train, X_test, y_train, y_test = train_test_split(
         input_vectors, output_vectors, test_size=0.25, random_state=0)

print "Training models"

estimators = [('linear', LinearRegression()),
              ('polynomial', make_pipeline(PolynomialFeatures(degree=2), 
                                           LinearRegression())),
              ('tree', tree.DecisionTreeRegressor())]

prediction_dir = "./data/prediction/"
              
for name, estimator in estimators:
    print "Training:", name
    estimator.fit(X_train, y_train)
    score = estimator.score(X_test, y_test)
    results = estimator.predict(input_vectors)
    print "Score:", score
    i = 0
    print "Outputting files:", name
    for city in cities:
        output_to_city(city, results[i])
        f = open(prediction_dir + name + "/" + "city_" + str(i) + ".json", 'w')
        f.write(city.to_json())
        f.close()
        i += 1





    
    
    