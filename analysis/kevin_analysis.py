"""
Quick script to analyze results from CityMatrix user tests.
"""

import datetime
import glob
import json
import os
import sys
import time
from collections import defaultdict

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

sys.path.append('../global/')
import cityiograph

BASE_DIR = '/Users/Kevin/Documents/mit/urop/data/server_test_data/current/'
CITY_SIZE = 16
METRIC_NAMES = ["Density", "Diversity", "Energy", "Traffic", "Solar"]
MOVE_THRESHOLD = 3
BIN_SIZE = 5
MIN_TIME = 1499541483


def unique_city_generator(city_directory):
    """Generator instance to give us cities that are different based on equals().
        Args:
        city_directory (str): directory (relative or absolute) with
            .json city *output* files

    Yields:
        3-tuple: unique City instance that can be used for analysis
            and corresponding dictionary object + filename
    """
    prev_city = None
    good_count = 0
    total_count = 0

    files = glob.glob(city_directory + '*.json')
    files.sort()

    for city_path in tqdm(files):
        total_count += 1
        # Read file
        with open(city_path, 'r') as f:
            full_json_string = f.read()

        # Get only the city described by ai or predict keys
        d = json.loads(full_json_string)['ai']
        if d is None:
            # null AI -> use predict instead
            d = json.loads(full_json_string)['predict']
        j_string = json.dumps(d)
        current_city = cityiograph.City(j_string)
        fname = os.path.basename(city_path)

        # Validate time
        the_city_time = get_time(fname)
        if the_city_time < MIN_TIME:
            continue

        if prev_city is None:
            # First time, just yield
            prev_city = current_city
            good_count += 1
            yield current_city, d, fname

        elif not prev_city.equals(current_city):
            # Different cities - yield new
            prev_city = current_city
            good_count += 1
            yield current_city, d, fname

        else:
            # Equal
            continue

    print("Yield = {:.2%}. {} / {}.".format(float(good_count) / total_count,
                                            good_count, total_count))


def get_time(filename):
    """Gets the UNIX timestamp int out of a filename.

    Args:
        filename (str): of the form city_predictions_TIME.json

    Returns:
        int: UNIX timestamp value
    """
    idx_start = len('city_predictions_')
    end = filename[idx_start:]
    stop_index = end.index('.json')
    final = end[: stop_index]
    return int(final)


def groupedAvg(myArray, N=2):
    result = np.cumsum(myArray, 0)[N - 1::N] / float(N)
    result[1:] = result[1:] - result[:-1]
    return result


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
        # metric_names = ["Density", "Diversity", "Energy", "Traffic", "Solar"]
        # df = pd.DataFrame(columns = metric_names)
        prev_move_suggested = None
        prev_city = None
        rates = []
        accept_count = 0
        idx = 0

        while True:
            try:
                city, d = next(gen)

                if prev_city is None:
                    # First time - just update value
                    prev_city = city
                    # prev_move = tuple(city.AIMov)[: -1]

                else:
                    # Get the difference between this one and prev
                    this_move = city.get_move(prev_city)

                    if this_move == prev_move_suggested:
                        # We have an acceptance!
                        # print("omg")
                        accept_count += 1

                    else:
                        # Nope
                        # print("AI suggested = {}. User did = {}."
                        #    .format(prev_move_suggested, this_move))
                        pass

                    # Add to y array
                    new_rate = float(accept_count) / idx * 100
                    rates.append(new_rate)

                    # Also, append this current move to the set
                    prev_move_suggested = tuple(city.AIMov)[: -1]

                    # Update prev instance
                    prev_city = city

                # total_scores.append(sum(city.scores))
                # Get dict of scores
                # city_metrics = d["objects"]["metrics"]
                # metrics_dict = { k : city_metrics[k][0] * city_metrics[k][1]
                #    for k in city_metrics }
                # df = df.append(pd.Series(metrics_dict), ignore_index = True)

                idx += 1

            except StopIteration:
                break

        # Plot the rates
        plt.figure(figsize=(12, 8))
        plt.title(test.replace(BASE_DIR, ''), fontsize=20)
        plt.xlabel("City Time Instance")
        plt.ylabel("Acceptance Rate (%)")
        plt.ylim([0, 100])
        plt.plot(rates)
        plt.savefig('data/' + test.replace(BASE_DIR,
                                           '').replace('/', '|') + '_ai_'
                    'accept.png')

        '''
        # Plot the columns over time
        plt.figure(figsize = (12, 8))
        i = 1
        for column in df:
            plt.subplot(int('32' + str(i)))
            df[column].plot()
            plt.title(column)
            i += 1

        plt.tight_layout(pad=3)
        plt.suptitle(test.replace(BASE_DIR, ''), fontsize = 20)
        plt.savefig('data/' + test.replace(BASE_DIR, '').replace('/', '|') + '_each_score.png')

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
    #   x, y = k
    #   heatmap[y, x] = v

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


def base_method():
    # Outer vars

    # Iterate over the tests
    for i, test in enumerate(glob.glob(BASE_DIR + '*')):
        test_string = test.replace(BASE_DIR, '').replace('/', '|')
        print("Working on test = {}...".format(test))
        # Create gen
        gen = unique_city_generator(test + '/')

        # Tracker vars

        for city, d, fname in gen:
            continue

        break  # Debug only


def get_ratios():
    """Get ratios of move type for each type.
    """
    # Outer vars
    df = pd.DataFrame()

    # Iterate over the tests
    for i, test in enumerate(glob.glob(BASE_DIR + '*')):
        print("Working on test = {}...".format(test))
        # Create gen
        gen = unique_city_generator(test + '/')

        # Tracker vars
        prev = None
        counter = defaultdict(int)

        for city, d, fname in gen:
            counter[city.AIMov[0]] += 1

        # Add to dataframe
        df = df.append(pd.Series(dict(counter), name=i + 1))

    df['SUM'] = df.sum(axis=1)

    print("Here are the exact move type counts for each test.")
    print(df)
    del df['SUM']

    print("And here are the ratios of these counts for each test.")
    df_norm = df.div(df.sum(axis=1), axis=0)
    print(df_norm)


def get_density_info():
    # Outer vars

    # Iterate over the tests
    for i, test in enumerate(glob.glob(BASE_DIR + '*')):
        test_string = test.replace(BASE_DIR, '').replace('/', '|')
        print("Working on test = {}...".format(test))
        # Create gen
        gen = unique_city_generator(test + '/')

        # Tracker vars
        idx = []
        val = []

        for city, d, fname in gen:
            if city.AIMov[0] == 'DENSITY':
                idx.append(city.AIMov[1])
                val.append(city.AIMov[2])

        idx = np.array(idx)
        val = np.array(val)

        plt.figure(figsize=(10, 6))
        idx_labels, idx_counts = np.unique(idx, return_counts=True)
        plt.bar(idx_labels, idx_counts / np.sum(idx_counts))
        plt.title("Test {}. Density index histogram.".format(test_string))
        plt.xlabel("Index")
        plt.ylabel("Frequency")
        plt.savefig('data_new/' + test_string + '_density_indices.png')

        plt.figure(figsize=(10, 6))
        val_labels, val_counts = np.unique(val, return_counts=True)
        plt.bar(val_labels, val_counts / np.sum(val_counts))
        plt.title("Test {}. Density value histogram.".format(test_string))
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.xlim([-1, 31])
        plt.savefig('data_new/' + test_string + '_density_values.png')

        # break # Debug only


def ai_weight_track():
    # Outer vars

    # Iterate over the tests
    for i, test in enumerate(glob.glob(BASE_DIR + '*')):
        test_string = test.replace(BASE_DIR, '').replace('/', '|')
        print("Working on test = {}...".format(test))
        # Create gen
        gen = unique_city_generator(test + '/')

        # Tracker vars
        times = []
        weights = []

        for city, d, fname in gen:
            time = get_time(fname)
            times.append(time)
            weights.append(city.AIWeights)

        x_times = np.array(times)
        # x_times = (times - times[0]) # / 60
        x_times_dt = [datetime.datetime.fromtimestamp(t) for t in x_times]
        mpl_times = matplotlib.dates.date2num(x_times_dt)

        weights = np.array(weights)

        fig = plt.figure(figsize=(10, 12))
        for i, col in enumerate(weights.T):
            # Plot this weight column
            sub = fig.add_subplot(5, 1, i + 1)
            sub.set_title(METRIC_NAMES[i])
            sub.set_ylim([0, 1])

            plt.xticks(rotation=25)
            ax = plt.gca()
            xfmt = matplotlib.dates.DateFormatter('%I:%M:%S %p')
            ax.xaxis.set_major_formatter(xfmt)

            sub.plot(mpl_times, col)

        plt.subplots_adjust(left=0.05, bottom=0.1,
                            right=0.95, top=0.9, wspace=1, hspace=0.7)
        fig.suptitle("Test = {}. AI Weights vs time (minutes).".format(
            test_string), fontsize=15)
        # plt.show()
        plt.savefig('data_new/' + test_string + '_ai_weights.png')

        # break # Debug only


def scores():
    # Outer vars

    # Iterate over the tests
    for i, test in enumerate(glob.glob(BASE_DIR + '*')):
        test_string = test.replace(BASE_DIR, '').replace('/', '|')
        print("Working on test = {}...".format(test))
        # Create gen
        gen = unique_city_generator(test + '/')

        # Tracker vars
        times = []
        scores = []

        for city, d, fname in gen:
            time = get_time(fname)
            times.append(time)
            # Get score values from city
            # Here, we look at the metrics dictionary
            # scores.append(city.scores)
            scores.append([city.metrics[k]['metric'] * city.metrics[k]['weight']
                           for k in city.metrics])
            # scores.append([city.metrics[k]['metric'] for k in city.metrics])

        x_times = np.array(times)
        x_times_dt = [datetime.datetime.fromtimestamp(t) for t in x_times]
        mpl_times = matplotlib.dates.date2num(x_times_dt)

        '''
        scores = np.array(scores)

        fig = plt.figure(figsize=(10, 12))
        for i, col in enumerate(scores.T):
            # Plot this score column
            sub = fig.add_subplot(5, 1, i + 1)
            sub.set_title(METRIC_NAMES[i])
            sub.set_ylim([0, 1])

            plt.xticks(rotation=25)
            ax = plt.gca()
            xfmt = matplotlib.dates.DateFormatter('%I:%M:%S %p')
            ax.xaxis.set_major_formatter(xfmt)

            sub.plot(mpl_times, col)

        plt.subplots_adjust(left=0.05, bottom=0.1,
                            right=0.95, top=0.92, wspace=1, hspace=0.7)
        fig.suptitle("Test = {}. Individual scores vs time (minutes).".format(
            test_string), fontsize=15)
        plt.savefig('data_new/' + test_string + '_indi_scores_yes_weight.png')

        # scores_avg = scores  # groupedAvg(scores, N=2)
        # x_times_avg = x_times  # groupedAvg(x_times, N=2)
        '''

        scores_avg_total = np.sum(scores, axis=1)
        plt.figure(figsize=(10, 8))
        plt.plot(mpl_times, scores_avg_total)
        plt.ylim([0, 1.5])
        plt.title("Test = {}. Total city score vs time (minutes).".format(
            test_string), fontsize=15)
        plt.subplots_adjust(left=0.05, bottom=0.1,
                            right=0.95, top=0.92, wspace=1, hspace=0.3)

        plt.xticks(rotation=25)
        ax = plt.gca()
        xfmt = matplotlib.dates.DateFormatter('%I:%M:%S %p')
        ax.xaxis.set_major_formatter(xfmt)

        plt.savefig('data_new/' + test_string + '_total_score.png')

        # break # Debug only


def ai_acceptance():
    # Outer vars

    # Iterate over the tests
    for i, test in enumerate(glob.glob(BASE_DIR + '*')):
        test_string = test.replace(BASE_DIR, '').replace('/', '|')
        print("Working on test = {}...".format(test))
        # Create gen
        gen = unique_city_generator(test + '/')

        # Tracker vars
        times = []
        prev = None
        move_set = []
        move_indicator = []
        df = pd.DataFrame()

        for city, d, fname in gen:
            the_time = get_time(fname)
            if the_time < 1499543294:  # Custom check
                continue
            times.append(the_time)

            if prev is None:
                prev = city
                move_indicator.append(0)
                data = dict(time=str(the_time), indicator='0')
                df = df.append(pd.Series(data), ignore_index=True)

            else:
                move = city.get_move(prev)
                prev = city

                # Trim our set if needed
                if len(move_set) == MOVE_THRESHOLD + 1:
                    del move_set[0]

                if move not in move_set:
                    move_set.append(move)
                    move_indicator.append(0)
                    data = dict(time=str(the_time), indicator='0')
                    df = df.append(pd.Series(data), ignore_index=True)

                else:
                    move_indicator.append(1)
                    data = dict(time=str(the_time), indicator='1')
                    df = df.append(pd.Series(data), ignore_index=True)

        # Save CSV
        # df.to_csv(os.path.join(BASE_DIR, os.pardir, 'ryan_alex_accept.csv'))

        # sys.exit(1)

        x_times = np.array(times)
        x_times_dt = [datetime.datetime.fromtimestamp(t) for t in x_times]
        mpl_times = matplotlib.dates.date2num(x_times_dt)

        move_indicator = np.array(move_indicator)

        # Sum it into bins
        bin_count, remainder = divmod(move_indicator.shape[0], BIN_SIZE)
        first = move_indicator[: bin_count * BIN_SIZE]
        last = move_indicator[bin_count * BIN_SIZE:]
        first = first.reshape(-1, BIN_SIZE)
        first_sum = first.sum(axis=1) / BIN_SIZE
        last_sum = [last.sum() / remainder]
        first_repeat = np.repeat(first_sum, BIN_SIZE)
        last_repeat = np.repeat(last_sum, remainder)
        all_sums = np.concatenate((first_repeat, last_repeat), axis=0)

        # Plot it
        plt.figure(figsize=(10, 8))
        plt.plot(mpl_times, all_sums)
        plt.ylim([0, 1.1])
        plt.title("Test = {}. AI acceptance rate vs time (minutes).".format(
            test_string), fontsize=15)
        plt.subplots_adjust(left=0.05, bottom=0.1,
                            right=0.95, top=0.92, wspace=1, hspace=0.3)

        plt.xticks(rotation=25)
        ax = plt.gca()
        xfmt = matplotlib.dates.DateFormatter('%I:%M:%S %p')
        ax.xaxis.set_major_formatter(xfmt)

        # plt.show()
        # sys.exit(1)
        plt.savefig('data_new/' + test_string + '_ai_acceptance.png')

        # break # Debug only


def ai_step():
    # Outer vars

    # Iterate over the tests
    for i, test in enumerate(glob.glob(BASE_DIR + '*')):
        test_string = test.replace(BASE_DIR, '').replace('/', '|')
        print("Working on test = {}...".format(test))
        # Create gen
        gen = unique_city_generator(test + '/')

        # Tracker vars
        times = []
        steps = []

        for city, d, fname in gen:
            time = get_time(fname)
            if time < 1499541483:
                continue

            times.append(datetime.datetime.fromtimestamp(time))
            steps.append(city.AIStep)

        time_nums = matplotlib.dates.date2num(times)

        plt.subplots_adjust(bottom=0.2)
        plt.xticks(rotation=25)
        ax = plt.gca()
        xfmt = matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)
        plt.plot(time_nums, steps)
        plt.show()

        break  # Debug only


def id_dist():
    # Outer vars

    # Iterate over the tests
    for i, test in enumerate(glob.glob(BASE_DIR + '*')):
        test_string = test.replace(BASE_DIR, '').replace('/', '|')
        print("Working on test = {}...".format(test))
        # Create gen
        gen = unique_city_generator(test + '/')

        # Tracker vars
        times = []

        for city, d, fname in gen:
            the_time = get_time(fname)
            times.append(the_time)
            type_array = [cell.type_id for cell in city.cells.values()]
            vals, counts = np.unique(type_array, return_counts=True)
            print(counts, vals)
            sys.exit(1)

        break  # Debug only


if __name__ == '__main__':
    print("Starting process.")
    start = time.time()

    # ai_move_analysis()
    # get_ratios()
    # get_density_info()
    # ai_weight_track()
    # scores()
    # ai_acceptance()
    # base_method()
    # ai_step()
    id_dist()

    print("Process complete. Took {} seconds.".format(time.time() - start))
