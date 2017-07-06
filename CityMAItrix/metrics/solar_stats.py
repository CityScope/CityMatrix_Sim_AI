import numpy as np

def max_solar_radiation(city):
    return np.max([c.data["solar"] for c in city.cells.values()])

def min_solar_radiation(city):
    return np.min([c.data["solar"] for c in city.cells.values()])

def avg_solar_radiation(city):
    return np.mean([c.data["solar"] for c in city.cells.values()])

def total_solar_radiation(city):
    return np.sum([c.data["solar"] for c in city.cells.values()])