# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 23:03:34 2017

@author: Alex
"""
import os
import shutil
import pickle
import sys
from tqdm import tqdm

sys.path.insert(0, '../global/')
import cityiograph, city_compare # Changes made by Kevin, 5/28/2017

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
    #return get_features_treesim(city)

    features = []
    # treesim_features = get_features_treesim(city)
    for i in range(city.width):
        for j in range(city.height):
            cell = city.cells.get((i, j))
            features += cell_features(cell)
            # features.append(treesim_features[i * city.height + j])
    features += city_features(city)
    return np.array(features)


def get_features_treesim(city):
    features = []
    traffictreesim.traffic_sim(city)
    for i in range(city.width):
        for j in range(city.height):
            features.append(city.cells.get((i, j)).data["traffic"])
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
            cell = city.cells.get((x, y))
            cell.data["traffic"] = int(round(output[i]))
            cell.data["wait"] = int(round(output[i + 1]))
            i += 2


def verify_samecity(in_city, out_city):
    return in_city.equals(out_city)

if __name__ == "__main__":

    log = []

    cities = []
    train_features = []
    train_results = []
    test_features = []
    test_results = []

    train_dir = "../../../data/train/"
    test_dir = "../../../data/test/"
    # prediction_dir = "../../../data/prediction/"

    estimators = [
        ('linear', LinearRegression()),
        #('polynomial_2deg', make_pipeline(PolynomialFeatures(degree=2),
        #                             LinearRegression())),
        ('decision_tree', tree.DecisionTreeRegressor()),
        ('kNN_uniform', KNeighborsRegressor()),
        #('kNN_distance', KNeighborsRegressor(weights="distance"))
    ]

    TRAIN_DATA_FILENAME = '../../../data/no_wandering_data_train.p'
    TEST_DATA_FILENAME = '../../../data/no_wandering_data_test.p'
    prediction_dir = './no_wandering_linear_predictions/'

    # Create prediction dir if does not already exist
    if not os.path.exists(prediction_dir):
        os.makedirs(prediction_dir)

    # train_files = os.listdir(train_dir)
    # test_files = os.listdir(test_dir)

    # log.append("Preparing training features/results")
    # print(log[-1])

    # for train_file in train_files:
    #     city = cityiograph.City(open(train_dir + train_file).read())
    #     features = get_features(city)
    #     results = get_results(city)

    #     cities.append((train_dir + train_file, city))
    #     train_features.append(features)
    #     train_results.append(results)


    # log.append("Preparing testing features/results")
    # print(log[-1])

    # for test_file in test_files:
    #     city = cityiograph.City(open(test_dir + test_file).read())
    #     features = get_features(city)
    #     results = get_results(city)

    #     cities.append((test_dir + test_file, city))
    #     test_features.append(features)
    #     test_results.append(results)

    cities, filenames, train_features, train_results = pickle.load(open(TRAIN_DATA_FILENAME, 'rb'))
    test_cities, test_filenames, test_features, test_results = pickle.load(open(TEST_DATA_FILENAME, 'rb'))

    cities.extend(test_cities)
    filenames.extend(test_filenames)

    log.append("Training features size:" + str(train_features.shape))
    print(log[-1])
    log.append("Training results size:" + str(train_results.shape))
    print(log[-1])
    log.append("Training models")
    print(log[-1])

    for name, estimator in estimators:
        log.append("Training: " + str(name))
        print(log[-1])
        estimator.fit(train_features, train_results)

        test_prediction = estimator.predict(test_features)
        score = city_compare.R_squared(test_results, test_prediction)
        log.append("R^2 score on test files: " + str(score))
        print(log[-1])

        i = 0
        log.append("Outputting files: " + str(name))
        print(log[-1])
        if os.path.exists(prediction_dir + name):
            shutil.rmtree(prediction_dir + name)
        os.makedirs(prediction_dir + name)
        os.makedirs(prediction_dir + name + "/test")
        os.makedirs(prediction_dir + name + "/train")
        train_prediction = estimator.predict(train_features)
        print(train_prediction.shape, test_prediction.shape)
        all_predictions = np.concatenate((train_prediction, test_prediction))

        # Minor changes made by Kevin to write to files.
        for i, city in tqdm(enumerate(cities)):
            output_to_city(city, all_predictions[i])
            with open(prediction_dir + name + "/" + filenames[i] + "_prediction.json", 'w') as f:
                f.write(city.to_json())

    f = open(prediction_dir + "log.txt", 'w')
    f.write("\n".join(log))
    f.close()

    for name, estimator in estimators:
        pickle.dump(estimator, open(prediction_dir + name + ".pkl", 'wb'))