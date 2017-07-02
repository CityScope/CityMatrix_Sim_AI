import sys
import logging
import utils
from objective import objective
from random import *
sys.path.extend(['../', '../../CityPrediction/'])
from CityPrediction import predictor as ML

''' --- CONFIGURATIONS --- '''

log = logging.getLogger('__main__')
density_change_chance = 0.5 #RZ equal chance: (6*30)/(256*6)=0.1172
density_range = (1, 30)
id_range = (0, 5)
iterations = 50 #RZ speed: about 150 iterations per second

''' --- METHOD DEFINITIONS --- '''

def search(city):
    """Random single moves AI search algorithm.
    
    Args:
        city (cityiograph.City): the city for which we would like to optimize our metrics
    
    Returns:
        3-tuple: suggested_city (cityiograph.City): -
                 best_move (3-tuple):    move type { 'DENSITY', 'CELL' } (str)
                                        index (int) and new density (int)
                                            OR
                                        x (int), y (int) and new type id for that cell
                 scores (list): AI metrics scores
    """
    visited = set() # KL 1706625 changing to set to get O(1) search lookups
    best_score = None
    best_scores = None #RZ 170615 passing score array to json
    best_move = None
    #RZ 170615 update the weights before search
    objective.update_weights(city.AIWeights)
    for i in range(iterations):
        r = random()
        if r <= density_change_chance:
            idx = dens = -1
            lmt = 0 #RZ limit the while loop, it will cause dead loop when density_change_chance is high
            while ((dens == -1 or idx == -1)  \
                or ("DENSITY", idx, dens) in visited)  \
                and lmt < 6 * 30 : #RZ possible moves
                idx = randint(id_range[0], id_range[1] - 1) #TOTO magic number here?
                dens = randint(density_range[0], density_range[1])
                lmt = lmt + 1 #RZ
            mov = ("DENSITY", idx, dens)
        else:
            x = y = newid = -1
            lmt = 0 #RZ limit the while loop
            while ((x == -1 or y == -1 or newid == -1) \
                or x < 4 or x > 9 or y < 4 or y > 9 or x == 8 or y == 8 # Focus center of city and no road cell
                or ("CELL", x, y, newid) in visited)  \
                and lmt < 256 * 6 * 8 : #RZ possible moves * 8
                x = randint(0, city.width - 1)
                y = randint(0, city.height - 1)
                newid = randint(id_range[0], id_range[1])
                lmt = lmt + 1 #RZ
            mov = ("CELL", x, y, newid)
        visited.add(mov)
        [ scr , best ] = scores(city, mov) # KL - minor optimization to avoid duplicate calls to score method
        if best_score == None or scr > best_score:
            best_score = scr
            best_scores = best
            best_move = mov

    # Determine our suggested city based on this move
    suggested_city = move(city, best_move)

    # Run the ML prediction on this suggested city
    final_city = ML.predict(suggested_city)

    # Update AI params based on this move - changes from Ryan
    log.info("AI search complete. Best score = {}. Best move = {}.".format(best_score, best_move))
    final_city.updateAIMov(best_move)
    final_city.updateScores(best_scores)

    return final_city, best_move, objective.get_metrics(final_city)

def move(city, mov):
    """Helper method to change a city in some minor yet optimal way.
    
    Args:
        city (cityiograph.City): -
        mov (list): move object we wish to apply
    
    Returns:
        cityiograph.City: new suggested city from AI step
    
    Raises:
        ValueError: if we make a bad move
    """
    # Make a copy and update values accordingly
    new_city = city.copy()
    if mov[0] == "DENSITY":
        new_city.change_density(mov[1], mov[2])

    elif mov[0] == "CELL":
        new_city.change_cell(mov[1], mov[2], mov[3])

    else:
        raise ValueError("Bad move!")

    return new_city

def scores(city, mov = None):
    """Calculate the score of a city after a given move has been made.
    
    Args:
        city (cityiograph.City): -
        mov (list): move object we wish to apply
    
    Returns:
        float: weighted objective score of the city, given certain metrics
    """
    if mov is not None: #RZ 170615
        # Make the move
        new_city = move(city, mov)

        # Run the ML prediction on this new city
        final_city = ML.predict(new_city)

        # Return the evaluated metrics score
        return objective.evaluate(final_city)

    else:
        return objective.evaluate(city) #RZ 170615 - no move to make here