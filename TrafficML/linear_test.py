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

def cell_features(cell):
    feats = []
    feats.append(cell.population)
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
    
def get_features(city):
    features = []
    for i in range(city.width):
        for j in range(city.height):
            cell = city.cells.get((i, j))
            features += cell_features(cell) 
    features += city_features(city)
    return np.array(features)
    
def get_results(city):
    results = []
    for i in range(city.width):
        for j in range(city.height):
            cell = city.cells.get((i, j))
            results += cell_results(cell) 
    results += city_results(city)
    return np.array(results)

def output_to_city(city, output):
    i = 0
    for x in range(city.width):
        for y in range(city.height):
            cell = city.cells.get((x,y))
            cell.data["traffic"] = int(round(output[i]))
            cell.data["wait"] = int(round(output[i + 1]))
            i += 2
            
def verify_samecity(in_city, out_city):
    return np.array_equal(get_features(in_city), get_features(out_city))

def residuals(expected, predicted):
    return predicted - expected
    
def residual_plot(input_vectors, output_vectors, model):
    import pyqtgraph as pg
    assert len(input_vectors) == len(output_vectors)
    pred = model.predict(input_vectors)
    res = []
    for i in range(len(input_vectors)):
        res.append(residuals(output_vectors[i], pred[i]).sum())
    
    pg.plot(res)
    
    
cities = []    
input_vectors = []
output_vectors = []

input_dir = "./data/input/"
output_dir = "./data/output/"

input_files = os.listdir(input_dir)
output_files = os.listdir(output_dir)

print "Preparing training features/results"
for i in range(len(input_files)):
    in_city = cityiograph.City(open(input_dir + input_files[i]).read())
    out_city = cityiograph.City(open(output_dir + output_files[i]).read())
    features = get_features(in_city)
    results = get_results(out_city)
    if not verify_samecity(in_city, out_city):
        print input_files[i], output_files[i]
        print features
        print get_features(out_city)
        raise RuntimeError("Mismatched input and output files!")
    
    input_vectors.append(features)
    output_vectors.append(results)
    
input_vectors = np.array(input_vectors)
output_vectors = np.array(output_vectors)
print "Output size:", output_vectors.shape  

print "Splitting dataset"
X_train, X_test, y_train, y_test = train_test_split(
         input_vectors, output_vectors, test_size=0.25, random_state=0)

print "Training models"

estimators = [('linear', LinearRegression()),
              ('polynomial-1', make_pipeline(PolynomialFeatures(degree=1), 
                                           LinearRegression())),
              ('polynomial-2', make_pipeline(PolynomialFeatures(degree=2), 
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





    
    
    