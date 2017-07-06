import numpy as np
from sklearn.externals import joblib
import sys
sys.path.append('../global/')
# Ignore unneeded sklearn deprecation warnings
import warnings
warnings.filterwarnings("ignore", category = DeprecationWarning)

from config import SOLAR_MODEL_FILENAME, CITY_SIZE

model = joblib.load(SOLAR_MODEL_FILENAME)

def get_5x5_block(city, x, y):
    """Return an array of a 5x5 block of heights around a point of a city.
    
    Args:
        city (cityiograph.City OR dict): either city object OR dictionary mapping (x , y) location to cell height
        x (int): -
        y (int): -
    
    Returns:
        list: list of height values representing the block
    """
    cells = []

    for i in range(x - 2, x + 3): # TODO May need to negate one of these
        for j in range(y - 2, y + 3):
            if i < 0 or i >= CITY_SIZE or j < 0 or j >= CITY_SIZE:
                cells.append(0) # Out of bounds of city
            else:
                if isinstance(city, dict): # Just use the existing dict mapping
                    cells.append(city[(i , j)])
                else: # Must be cityiograph.City instance
                    cells.append(city.cells[(i , j)].get_height())

    return cells

def push_5x5_deltas(city, deltas, x, y):
    """Add the delta values to the block around a point of a city
    
    Args:
        city (cityiograph.City): -
        deltas (nparray (5, 5)): delta matrix
        x (int): -
        y (int): -
    """
    counter = 0
    for i in range(x - 2, x + 3): # TODO May need to negate one of these
        for j in range(y - 2, y + 3):
            if i < 0 or i >= city.width or j < 0 or j >= city.height:
                pass # 0 value here
            else:
                city.cells[(i, j)].data["solar"] += deltas[counter]
            counter += 1

def deltas(block_heights):
    """Get the solar delta values for removing a building at the center of a block.
    
    Args:
        block_heights (list): list of height values representing the block
    
    Returns:
        nparray (25,): delta values for this block, in column major order
    """
    # Use the lin reg model to predict
    model_output = model.predict(block_heights)[0]

    # But, this is (1, 1225) - need to average every 49 elements to get 5x5 block
    return np.mean(model_output.reshape(-1, 49), axis = 1)


def update_city(input_city, previous_city_heights, x, y):
    """Function to update a city's solar predictoin values based on a prior state.
    
    Args:
        input_city (cityiograph.City): the city that is currently being predicted - need to update its solar values
        previous_city_heights (dict): mapping (x , y) -> height on the PREVIOUS city state
        x (int): location in x
        y (int): location in y
    
    Returns:
        cityiograph.City: new city instance with updated solar values
    """
    # Get the deltas
    remove_old = deltas(get_5x5_block(previous_city_heights, x, y))
    add_new = deltas(get_5x5_block(input_city, x, y))

    # Find real change (OLD - NEW)
    change = np.subtract(remove_old, add_new)

    # Push the change to the input city
    push_5x5_deltas(input_city, change, x, y)
    
    return input_city