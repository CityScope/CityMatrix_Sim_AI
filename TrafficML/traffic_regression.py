# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 23:03:34 2017

@author: Alex
"""
import os
import shutil
import pickle

import sys
sys.path.insert(0, '../TrafficTreeSim/')
import cityiograph
import traffictreesim

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn import tree
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsRegressor

ROAD_ID = 6

def cell_features(cell):
    feats = []
    feats.append(cell.population)
    #feats.append(0) if (cell.type_id == ROAD_ID) else feats.append(1)
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
    #return get_features_treesim(city)
    
    features = []
    #treesim_features = get_features_treesim(city)
    for i in range(city.width):
        for j in range(city.height):
            cell = city.cells.get((i, j))
            features += cell_features(cell)
            #features.append(treesim_features[i * city.height + j])
    features += city_features(city)
    return np.array(features)
    
    
def get_features_treesim(city):
    features = []
    traffictreesim.traffic_sim(city)
    for i in range(city.width):
        for j in range(city.height):
            features.append(city.cells.get((i,j)).data["traffic"])
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
    return in_city.equals(out_city)

    
if __name__ == "__main__":
        
    log = []
        
    cities = []
    input_vectors = []
    output_vectors = []
    
    input_dir = "./data/input/"
    output_dir = "./data/output/"
    prediction_dir = "./data/prediction/"
    
    estimators = [('linear', LinearRegression()),
                  #('polynomial_2deg', make_pipeline(PolynomialFeatures(degree=2), 
                  #                             LinearRegression())),
                  ('decision_tree', tree.DecisionTreeRegressor()),
                  #('kNN_uniform', KNeighborsRegressor()),
                  ('kNN_distance', KNeighborsRegressor(weights="distance"))]
    
    
    input_files = os.listdir(input_dir)
    output_files = os.listdir(output_dir)
    
    log.append("Preparing training features/results")
    print log[-1]
    
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
        
        cities.append((input_files[i], in_city))
        input_vectors.append(features)
        output_vectors.append(results)
        
    input_vectors = np.array(input_vectors)
    output_vectors = np.array(output_vectors)
    
    log.append("Input size:" + str(input_vectors.shape))
    print log[-1]  
    log.append("Output size:" + str(output_vectors.shape))
    print log[-1]  
    
    log.append("Splitting dataset")
    print log[-1]
    
    X_train, X_test, y_train, y_test = train_test_split(
             input_vectors, output_vectors, test_size=0.25, random_state=0)
    
    log.append("Training models")
    print log[-1]
    

    
    for name, estimator in estimators:
        log.append("Training: " + str(name))
        print log[-1]
        estimator.fit(X_train, y_train)
        score = estimator.score(X_test, y_test)
        results = estimator.predict(input_vectors)
        log.append("Score: " + str(score))
        print log[-1]
        i = 0
        log.append("Outputting files: " + str(name))
        print log[-1]
        if os.path.exists(prediction_dir + name):
            shutil.rmtree(prediction_dir + name)
        os.makedirs(prediction_dir + name)
        for filename, city in cities:
            output_to_city(city, results[i])
            f = open(prediction_dir + name + "/" + filename, 'w')
            f.write(city.to_json())
            f.close()
            i += 1
    
    f = open(prediction_dir + "log.txt", 'w')
    f.write("\n".join(log))
    f.close()
    
    pickle.dump(estimators, open(prediction_dir + "models.pkl", 'wb'))



    
    
    