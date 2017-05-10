# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 17:22:44 2017

@author: Alex
"""
import sys
import os

import numpy as np
from sklearn.metrics import r2_score

sys.path.insert(0, './TrafficTreeSim/')
import cityiograph

sys.path.insert(0, './TrafficML/')
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
    #sumRes = residual_sum_squares(expectedVals, predictedVals)
    #sumTot = total_sum_squares(expectedVals)

    #return 1 - (sumRes / sumTot)
    return r2_score(expectedVals, predictedVals)


"""
City focused functions.

"""

CITY_STATS = [("residuals", residuals), ("norm_residuals",
                                         normalized_residuals)]


def get_data(city):
    return np.array(TR.get_results(city)).astype(float)


def city_stats(expectedCity, predictedCity):
    stats = {}
    for name, fun in CITY_STATS:
        stats[name] = fun(expectedCity, predictedCity)
    return stats


def cities_R_squared(expected_cities, predicted_cities):
    assert len(expected_cities) == len(predicted_cities)
    expected_vals = []
    predicted_vals = []
    for i in len(expected_cities):
        expected_vals.append(get_data(expected_cities[i]))
        predicted_vals.append(get_data(predicted_cities[i]))

    return R_squared(expected_vals, predicted_vals)


if __name__ == "__main__":
    expected_dir = "./TrafficML/data/test/"
    predicted_dir = "./TrafficML/data/prediction-population-isroad-treesim/prediction/"

    expected_vals = []

    print("Parsing expected citites")
    for filename in os.listdir(expected_dir):
        if filename.endswith(".json"):
            city = cityiograph.City(open(expected_dir + filename).read())
            expected_vals.append(get_data(city))
    expected_vals = np.array(expected_vals)

    print("Traversing predicted directory")
    for dirname, dirs, files in os.walk(predicted_dir):
        print("Parsing " + dirname)
        predicted_vals = []
        for filename in files:
            if filename.endswith(".json"):
                city = cityiograph.City(open(dirname + "/" + filename).read())
                predicted_vals.append(get_data(city))
        predicted_vals = np.array(predicted_vals)
        if len(predicted_vals) == 0:
            continue

        r_sqrd = R_squared(expected_vals, predicted_vals)
        res = np.array(
            [residuals(e, p) for e, p in zip(expected_vals, predicted_vals)])
        norm_res = np.array([
            normalized_residuals(e, p)
            for e, p in zip(expected_vals, predicted_vals)
        ])
        norm_res = norm_res[~np.isnan(norm_res).any(axis=1)]

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
        print('\n'.join(lines))

        log_name = dirname.replace('\\', '/').split('/')
        log_name = log_name[-2] + '_' + log_name[-1]
        log_name = log_name + "_analysis.txt"
        log = open(predicted_dir + "analysis/" + log_name, 'w')
        log.write('\n'.join(lines))
        log.close()


