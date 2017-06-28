"""
Filename: kevin_analysis.py
Author: Kevin Andrew Lyons
Date: 2017-06-27 21:52:26
Last modified by: kalyons11
Description:
    - Quick script to analyze results from CityMatrix user tests.
TODO:
    - None at this time.
"""

''' --- IMPORTS --- '''

import sys
import os
import time
import numpy as np
import json
import tqdm
import glob
import matplotlib.pyplot as plt
from collections import defaultdict

sys.path.append('../global/')
import cityiograph

''' --- CONFIGURATIONS --- '''

BASE_DIR = '/Users/Kevin/Documents/mit/urop/data/server_test_data/predicted_cities/'
CITY_SIZE = 16

''' --- CLASS/METHOD DEFINITIONS --- '''

def unique_city_generator(city_directory = BASE_DIR):
    """Summary

    Args:
    city_directory (TYPE, optional): Description

    Yields:
    TYPE: Description
    """
    prev_city = None

    for city_path in glob.glob(city_directory + '*.json'):
        # Read file
        with open(city_path, 'r') as f:
            full_json_string = f.read()

        # Get only the AI city
        ai_string = json.dumps(json.loads(full_json_string)['ai'])
        current_city = cityiograph.City(ai_string)

        if prev_city is None:
            # First time, just yield
            prev_city = current_city
            yield current_city

        elif not prev_city.equals(current_city):
            # Different cities - yield new
            prev_city = current_city
            yield current_city

        else:
            # Equal
            continue

def ai_move_analysis():
    """Summary
    """
    # Create generator object
    gen = unique_city_generator()

    # Keep track of AI moves
    moves = []
    density_indices = []
    density_values = []
    move_dict = defaultdict(int)
    cell_types = []

    while True:
        try:
            city = next(gen)
            move_type = city.AIMov[0]
            moves.append(move_type)
            if move_type == 'DENSITY':
                density_indices.append(city.AIMov[1])
                density_values.append(city.AIMov[2])
            elif move_type == 'CELL':
                x, y = city.AIMov[1], city.AIMov[2]
                move_dict[(x , y)] += 1
                cell_types.append(city.AIMov[3])
        except StopIteration:
            break

    # Analyze distribution
    # unique, counts = np.unique(moves, return_counts = True)
    # counts = counts / counts.sum()
    # move_dict = dict(zip(unique, counts * 100))
    # print(move_dict)

    # Create histogram
    # plt.hist(density_indices)
    # plt.title("Density Index Changes")
    # plt.xlabel("Index")
    # plt.ylabel("Frequency in Data")
    # plt.show()

    # Create another hist
    # plt.hist(density_values)
    # plt.title("Density Values")
    # plt.xlabel("Value")
    # plt.ylabel("Frequency in Data")
    # plt.show()

    # Analyze move locations
    # First, load into heatmap
    # heatmap = np.zeros((CITY_SIZE, CITY_SIZE))
    # for k, v in move_dict.items():
    # 	x, y = k
    # 	heatmap[y, x] = v

    # Show the heatmap
    # plt.imshow(heatmap, cmap = 'hot', interpolation = 'nearest')
    # plt.title("AI Cell Change Location Heatmap", fontsize = 20)
    # plt.show()

    # Create hist for cell types
    plt.hist(cell_types)
    plt.title("Cell Type ID's")
    plt.xlabel("Type ID")
    plt.ylabel("Frequency in Data")
    plt.show()

''' -- AUTOMAIN --- '''

if __name__ == '__main__':
    print("Starting process.")
    start = time.time()

    ai_move_analysis()

    print("Process complete. Took {} seconds.".format(time.time() - start))