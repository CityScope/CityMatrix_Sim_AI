import numpy as np
import pickle as pkl

model = None
with open("./models/solar_model.pkl", "rb") as f:
    model = pkl.load(f)

def get_5x5_block(city, x, y):
    cells = []

    for i in range(x - 2, x + 2):
        for j in range(y - 2, y + 2):
            if i < 0 or i >= city.width or j < 0 or j >= city.height:
                cells.append(None)
            else:
                cells.append(city.cells[(i, j)])

    return cells

def push_5x5_deltas(city, deltas, x, y):
    counter = 0
    for i in range(x - 2, x + 2):
        for j in range(y - 2, y + 2):
            if i < 0 or i >= city.width or j < 0 or j >= city.height:
                pass
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

    return model.predict(heights)


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
