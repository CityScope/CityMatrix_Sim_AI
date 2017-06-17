
def total_traffic(city):
    return np.sum([c.data['traffic'] for c in city.cells.values()])

def avg_traffic(city):
    return np.mean([c.data['traffic'] for c in city.cells.values()])

def total_wait(city):
    return np.sum([c.data['wait'] for c in city.cells.values()])

def avg_wait(city):
    return np.mean([c.data['wait'] for c in city.cells.values()])