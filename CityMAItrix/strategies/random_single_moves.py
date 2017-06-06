import sys
sys.path.extend(['../', '../../CityPrediction/'])
from objective import objective
from random import *
from CityPrediction import predictor as ML
import utils

density_change_chance = 0.5
id_range = (0, 6)
iterations = 30

def search(city):
    visited = []
    best_score = None
    best_move = None
    for i in range(iterations):
        r = random()
        if r <= density_change_chance:
            idx = dens = -1
            while (dens == -1 or idx == -1)  \
                or ("DENSITY", idx, dens) in visited:
                idx = randint(id_range[0], id_range[1] - 1) #TOTO maginc number here?
                dens = randint(density_range[0], density_range[1])
            mov = ("DENSITY", idx, dens)
        else:
            x = y = newid = -1
            while (x == -1 or y == -1 or newid == -1) \
                or ("CELL", x, y, newid) in visited:
                x = randint(0, city.width - 1)
                y = randint(0, city.height - 1)
                newid = randint(id_range[0], id_range[1])
            mov = ("CELL", x, y, newid)
        visited.append(mov)
        scr = score(city, mov)
        if best_score == None or scr > best_score:
            best_score = scr
            best_move = mov

    suggested_city = move(city, best_move)
    return (suggested_city, mov, objective.get_metrics(suggested_city))

def move(city, mov):
    city = city.copy()
    if mov[0] == "DENSITY":
        city.change_density(mov[1], mov[2])
    elif mov[0] == "CELL":
        city.change_cell(mov[1], mov[2], mov[3])
    else:
        raise error("Bad move!")
    return city

def score(city, mov):
    new_city = move(city, mov)
    update(new_city, city)
    return objective.predict(new_city)

def update(city, prev_city):
    # Need to run our ML prediction here
    # Run our black box predictor on this city with given changes
    key, data = utils.diff_cities(city, prev_city)
    return ML.predict(city, key, data, force_predict = True)