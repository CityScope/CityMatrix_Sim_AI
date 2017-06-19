import numpy as np
from sklearn.externals import joblib
import sys
sys.path.append('../global/')
# Ignore unneeded sklearn deprecation warnings
import warnings
warnings.filterwarnings("ignore", category = DeprecationWarning)

from config import SOLAR_MODEL_FILENAME

model = joblib.load(SOLAR_MODEL_FILENAME)

def get_5x5_block(city, x, y):
    """Return an array of a 5x5 block around a point of a city.
    
    Args:
        city (cityiograph.City): -
        x (int): -
        y (int): -
    
    Returns:
        list: list of cityiograph.Cell objects representing the block
    """
    cells = []

    for i in range(x - 2, x + 3):
        for j in range(y - 2, y + 3):
            if i < 0 or i >= city.width or j < 0 or j >= city.height:
                cells.append(None)
            else:
                cells.append(city.cells[(i, j)])

    return cells

def push_5x5_deltas(city, deltas, x, y):
    """Add the delta values to the block around a point of a city
    
    Args:
        city (cityiograph.City): -
        deltas (nparray (5, 5)): delta matrix
        x (int): -
        y (int): -
    
    Returns:
        cityiograph.City: output city
    """
    counter = 0
    for i in range(x - 2, x + 3):
        for j in range(y - 2, y + 3):
            if i < 0 or i >= city.width or j < 0 or j >= city.height:
                pass # 0 value here
            else:
                city.cells[(i, j)].data["solar"] += deltas[counter]
            counter += 1

    return city

def deltas(block):
    """Get the solar delta values for removing a building at the center of a block.
    
    Args:
        block (list): list of cell objects that are in the block
    
    Returns:
        nparray (5, 5): delta values for this block
    """
    heights = []
    for c in block:
        if c == None:
            heights.append(0)
        else:
            heights.append(c.get_height())

    model_output = model.predict(heights)[0]

    # But, this is (1, 1225) - need to average every 49 elements to get 5x5 block
    return np.mean(model_output.reshape(-1, 49), axis = 1)


def update_city(old_city, new_city, x, y):
    """Function to update a city's solar predictoin values based on a prior state.
    
    Args:
        old_city (cityiograph.City): -
        new_city (cityiograph.City): -
        x (int): location in x
        y (int): location in y
    
    Returns:
        TYPE: Description
    """
    # Get the deltas
    remove_old = deltas(get_5x5_block(old_city, x, y))
    add_new = deltas(get_5x5_block(new_city, x, y))

    # find real change
    change = np.subtract(remove_old, add_new)

    # Push the change to the OLD city
    final_city = old_city.copy()
    push_5x5_deltas(final_city, change, x, y)
    return final_city

if __name__ == "__main__":
    import sys
    sys.path.append("../global/")
    import cityiograph
    with open("./city_0_output_solar.json", 'r') as f:
        city = cityiograph.City(f.read())
        # for cell in city.cells.values():
            # cell.data["solar"] = 0
        new_city = city.copy()
        for cell in new_city.cells.values(): cell.density = 0
        update_city(new_city, city, 5,5)
        # with open("city_0_output_solar_new.json", 'w') as o:
        #   o.write(city.to_json())