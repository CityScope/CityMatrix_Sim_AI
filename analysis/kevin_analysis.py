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
import pandas as pd
import json
import tqdm
import glob
import matplotlib.pyplot as plt
from collections import defaultdict

sys.path.append('../global/')
import cityiograph

''' --- CONFIGURATIONS --- '''

BASE_DIR = '/Users/Kevin/Documents/mit/urop/data/server_test_data/'
CITY_SIZE = 16

''' --- CLASS/METHOD DEFINITIONS --- '''

def unique_city_generator(city_directory, key = 'ai'):
    """Generator instance to give us cities that are different based on equals().
    
    Args:
        city_directory (str): directory (relative or absolute) with .json city *output* files
        key (str, optional): describes whether we want predict/ai city from result
    
    Yields:
        cityiograph.City: unique City instance that can be used for analysis
    """
    prev_city = None

    for city_path in glob.glob(city_directory + '*.json'):
        # Read file
        with open(city_path, 'r') as f:
            full_json_string = f.read()

        # Get only the AI city
        d = json.loads(full_json_string)[key]
        j_string = json.dumps(d)
        current_city = cityiograph.City(j_string)

        if prev_city is None:
            # First time, just yield
            prev_city = current_city
            yield current_city, d

        elif not prev_city.equals(current_city):
            # Different cities - yield new
            prev_city = current_city
            yield current_city, d

        else:
            # Equal
            continue

def ai_move_analysis():
    """Looking the city's AI params.
    """
    # Iterate over the tests
    for test in glob.glob(BASE_DIR + '*'):
        print("Working on test = {}...".format(test))
        # Create gen
        gen = unique_city_generator(test + '/')

        # Keep track of weights
        # weights = []
        # total_scores = []
        metric_names = [ "Density" , "Diversity" , "Energy" , "Traffic" , "Solar" ]
        df = pd.DataFrame(columns = metric_names)

        while True:
            try:
                city, d = next(gen)
                # total_scores.append(sum(city.scores))
                # Get dict of scores
                city_metrics = d["objects"]["metrics"]
                metrics_dict = { k : city_metrics[k][0] * city_metrics[k][1] for k in city_metrics }
                df = df.append(pd.Series(metrics_dict), ignore_index = True)

            except StopIteration:
                break

        # Here...

        '''
        # Plot scores
        x = np.arange(len(total_scores))
        plt.figure(figsize = (8, 8))
        plt.plot(x, total_scores, lw = 3, color = 'green')
        plt.title("sum(city.scores), {}".format(test.replace(BASE_DIR, '')))
        plt.savefig('data/' + test.replace(BASE_DIR, '').replace('/', '|') + '_total_scores.png')
        
        # Convert to np
        weights = np.array(weights)

        # Plot columns
        x = np.arange(weights.shape[0])
        fig = plt.figure(figsize = (8, 12))
        colormap = plt.cm.gist_ncar
        colors = [ colormap(i) for i in np.linspace(0, 1, 5) ]

        for i, col in enumerate(weights.T):
            # Make plot
            ax = fig.add_subplot(int('51' + str(i + 1)))
            ax.plot(x, col, label = metric_names[i], lw = 1, marker = 'o', color = colors[i])
        
        # Save
        plt.savefig('data/' + test.replace(BASE_DIR, '').replace('/', '|') + '_ai_weights.png')
        '''

    ''' 
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
    
    '''

''' -- AUTOMAIN --- '''

if __name__ == '__main__':
    print("Starting process.")
    start = time.time()

    ai_move_analysis()

    print("Process complete. Took {} seconds.".format(time.time() - start))