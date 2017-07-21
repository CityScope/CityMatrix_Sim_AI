import numpy as np

persons_per_floor = [18, 28, 63, 52, 87, 156, 0]
def population(cell):
    return cell.density * persons_per_floor[cell.type_id]


def id_pop_dict(city):
    #pop = {}
    pop = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, -1: 0} #RZ - fix the error if no certain type_id in the input city. 
    for cell in city.cells.values():
        #print(cell.type_id)
        if cell.type_id not in pop:
            pop[cell.type_id] = 0
        pop[cell.type_id] += population(cell)
    #print(pop)
    return pop

def normalize(x, min, max):
    return (x - min) / (max - min)

pdp_min = 0
pdp_max = 100000 #958464
def pop_density_perf(city):
    pop_dict = id_pop_dict(city)
    #print(pop_dict)
    pop = sum(pop_dict.values())
    return normalize(pop, pdp_min, pdp_max)

def LUM(populations):
    #print(populations)
    tot = sum(populations)
    probs = map(lambda x: (x / tot) * np.log10(x / tot) if x != 0 else 0, populations)
    return -sum(probs) / np.log10(len(populations))

edp_min = 0.65
edp_max = 1.0 # need to determine this
def pop_diversity_perf(city):
    pop_dict = id_pop_dict(city)
    residential_diversity = LUM([pop_dict[0], pop_dict[1], pop_dict[2]])
    office_diversity = LUM([pop_dict[3], pop_dict[4], pop_dict[5]])
    living_working_diversity = LUM([pop_dict[0] + pop_dict[1] + pop_dict[2],
                                 pop_dict[3] + pop_dict[4] + pop_dict[5]])
    return normalize( (residential_diversity + office_diversity +
            living_working_diversity) / 3.0, edp_min, edp_max )

#energy_per_sqm = [0.8, 1.0, 1.2, 2.0, 2.5, 3.0, 0]
energy_per_sqm = [-0.2, 0.0, 0.2, -0.4, 0.0, 0.4, 0.0] #RZ 170617 
floor_area = 1562.5 # square meters
ep_min = -300000
ep_max = 300000 # need to determine this
def energy_perf(city):
    tot = 0
    for cell in city.cells.values():
        tot += cell.density * floor_area * energy_per_sqm[cell.type_id]
    return normalize(tot, ep_min, ep_max)

tp_min = 1000
tp_max = 3000 # need to determine this
def traffic_perf(city):
    #traffics = [cell.data["traffic"] for cell in city.cells.values()] #RZ 170703
    #RZ 170703
    traffics = []
    for cell in city.cells.values():
        if cell.type_id == 6:
            traffics.append(cell.data["traffic"])
    return 1 - normalize(sum(traffics) / len(traffics), tp_min, tp_max)

sp_min = 1000
sp_max = 1300 # need to determine this
def solar_perf(city):
    #solars = [cell.data["solar"] for cell in city.cells.values()] #RZ 170703
    #RZ 170703
    solars = []
    for cell in city.cells.values():
        if (cell.type_id >= -1 or cell.type_id <= 5) \
        and (cell.x >= 4 and cell.x <= 12 and cell.y >= 4 and cell.y <= 12) :
            solars.append(cell.data["solar"])
    return normalize(sum(solars) / len(solars), sp_min, sp_max)