import numpy as np
from sklearn.externals import joblib
import sys
sys.path.append(['../global/'])
# Ignore unneeded sklearn deprecation warnings
import warnings
warnings.filterwarnings("ignore", category = DeprecationWarning)

from config import SOLAR_MODEL_FILENAME

model = joblib.load(SOLAR_MODEL_FILENAME)

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
    # print(deltas.reshape(5, 5))
    for i in range(x - 2, x + 3):
        for j in range(y - 2, y + 3):
            if i < 0 or i >= city.width or j < 0 or j >= city.height:
                pass
            else:
                city.cells[(i, j)].data["solar"] =  int(round(city.cells[(i, j)].data["solar"] + deltas[counter])) # Rounding to nearest int
            counter += 1

    return city

def deltas(block):

    heights = []
    for c in block:
        if c == None:
            heights.append(0)
        else:
            heights.append(c.get_height())

    model_output = model.predict(heights)

    # But, this is (1, 1225) - need to average every 49 elements to get 5x5 block
    return np.mean(model_output.reshape(-1, 49), axis = 1)


def update_city(old_city, new_city, x, y):
    remove_old = deltas(get_5x5_block(old_city, x, y))
    add_new = deltas(get_5x5_block(new_city, x, y))

    change = np.subtract(remove_old, add_new)

    push_5x5_deltas(new_city, change, x, y)
    return new_city

if __name__ == "__main__":
    import sys
    sys.path.append("../global/")
    import cityiograph
    with open("./data/city_0_output.json", 'r') as f:
        city = cityiograph.City(f.read())
        for cell in city.cells.values():
            cell.data["solar"] = 0
        update_city(city, city, 5,5)
        with open("./data/city_0_output_solar.json", 'w') as o:
            o.write(city.to_json())
