import numpy as np

def population(city):
    return city.population

def cost(city):
    return np.sum([c.density for c in city.cells.values()])