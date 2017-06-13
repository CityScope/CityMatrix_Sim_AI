import numpy as np; # np.set_printoptions(threshold = np.nan)
from sklearn.externals import joblib
import sys
sys.path.append('../global/')
# Ignore unneeded sklearn deprecation warnings
import warnings
warnings.filterwarnings("ignore", category = DeprecationWarning)

from config import SOLAR_MODEL_FILENAME

model = joblib.load(SOLAR_MODEL_FILENAME)

# Figure out bugs w/ Alex, Ryan

def get_5x5_block(city, x, y):
    cells = []

    for i in range(x - 2, x + 3):
        for j in range(y - 2, y + 3):
            if i < 0 or i >= city.width or j < 0 or j >= city.height:
                cells.append(None)
            else:
                cells.append(city.cells[(i, j)])

    return cells

def push_5x5_deltas(city, deltas, x, y):
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

    heights = []
    for c in block:
        if c == None:
            heights.append(0)
        else:
            heights.append(c.get_height())

    model_output = model.predict(heights)[0]

    '''

    # Need to perform custom logic for the solar sensor layout
    # Changes made by Kevin, 6/11/17
    # First, reshape
    one = model_output.reshape(25, 7, 7)

    # Next, reindex
    idx = np.array([ 5, 10, 14, 19, 24, 4, 9, 13, 18, 23, 3, 8, 0, 17, 22, 2, 7, 12, 16, 21, 1, 6, 11, 15, 20 ])
    two = one[idx]

    # Next, rotate
    three = np.rot90(two, axes = (1, 2))

    # Finally, average
    return three.mean(axis = (1, 2))

    '''

    # Going back to old logic
    # But, this is (1, 1225) - need to average every 49 elements to get 5x5 block
    return np.mean(model_output.reshape(-1, 49), axis = 1)


def update_city(old_city, new_city, x, y):
    remove_old = deltas(get_5x5_block(old_city, x, y))
    add_new = deltas(get_5x5_block(new_city, x, y))

    change = np.subtract(add_new, remove_old) # Kevin - switched order for subtract operation...
    # print(change)

    push_5x5_deltas(old_city, change, x, y)
    return old_city

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
