# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 23:13:35 2017

@author: Alex
"""
import json
import numpy as np
import collections

from config import * # Kevin, 5/20/2017

class City(object):
    def __init__(self, json_string):
        self.json_obj = json.loads(json_string)
        self.meta = self.json_obj['objects']
        self.densities = self.meta['density']
        self.AIStep = self.meta['AIStep'] #RZ
        print ('AIStep in received JSON: ' + str(self.AIStep)) #RZ
        self.cells = dict_from_cells(
            cells_from_json(self.json_obj['grid'], self.densities))
        self.width = max(map(lambda c: c.x, self.cells.values())) + 1
        self.height = max(map(lambda c: c.y, self.cells.values())) + 1

        self.population = 0
        for c in self.cells.values():
            self.population += c.population

    def copy(self):
        return City(self.to_json())

    def equals(self, other):
        """True iff all of this city's cells are equal to their corresponding
        cells in other and densities, width, and height are the same.
        """
        cells_equal = all(
            [c.equals(other.cells.get(pos)) for pos, c in self.cells.items()])
        return cells_equal and (self.densities == other.densities) \
            and (self.width == other.width) and (self.height == other.height)

    def to_dict(self):
        self.meta["density"] = self.densities
        self.meta["population"] = self.population
        self.meta["AIStep"] = self.AIStep #RZ
        changes = {
            "objects": self.meta,
            "grid": [c.to_dict() for c in self.cells.values()]
        }
        return update_dict(self.json_obj, changes)

    def to_json(self):
        return json.dumps(self.to_dict())

    def get_cell(self, pos):
        return self.cells[pos]

    def nesw(self, pos):
        x = pos[0]
        y = pos[1]
        directions = []
        if x > 0:
            directions.append((x - 1, y))
        if x < self.width - 1:
            directions.append((x + 1, y))
        if y > 0:
            directions.append((x, y - 1))
        if y < self.height - 1:
            directions.append((x, y + 1))
        return directions

    def get_graph(self):
        graph = {}
        for cell in self.cells.values():
            edges = {}
            for n in self.nesw(cell.get_pos()):
                edges[n] = EDGE_COST
            graph[cell.get_pos()] = edges
        return graph

    def get_road_nearby_population_map(self):
        pop_map = {}
        for pos, cell in self.cells.items():
            if cell.type_id == ROAD_ID:
                pop_map[pos] = 0
                for n in [self.cells[p] for p in self.nesw(pos)]:
                    if n.type_id != ROAD_ID:
                        pop_map[pos] += n.population
        return pop_map

    def get_road_graph(self):
        road_graph = {}
        for (pos, edges) in self.get_graph().items():
            if self.cells[pos].type_id == ROAD_ID:
                new_edges = {}
                for (other_pos, cost) in edges.items():
                    if self.cells[other_pos].type_id == ROAD_ID:
                        new_edges[other_pos] = cost
                road_graph[pos] = new_edges
        return road_graph


    def change_density(self, idx, new_density):
        for cell in self.cells.values():
            if cell.type_id == idx:
                cell.density = new_density

        self.densities[idx] = new_density

    def change_cell(self, x, y, new_id):
        cell = self.cells[(x, y)]
        cell.type_id = new_id

        if cell.type_id == ROAD_ID:
            cell.density = 0
        else:
            cell.density = self.densities[cell.type_id]

        cell.population = density_to_pop(cell.type_id, cell.density)





class Cell(object):
    def __init__(self, jcell, density_arr):
        self.json_obj = jcell
        self.type_id = jcell['type']

        if self.type_id > 6: #RZ
            #print("type_id>6! change to -1") #RZ
            self.type_id = -1 #RZ
            
        self.x = jcell['x']
        self.y = jcell['y']
        self.rot = jcell['rot']
        self.magnitude = 0 #jcell['magnitude']
        self.data = jcell.get('data', {'traffic': 0, "wait": 0})

        if self.type_id == ROAD_ID:
            self.density = 0
        else:
            try:
                self.density = density_arr[self.type_id]
            except:
                self.density = 0 # Accounting for odd ID case error - Kevin, 5/19/2017

        self.population = density_to_pop(self.type_id, self.density)

    def get_pos(self):
        return (self.x, self.y)

    def get_height(self):
        return round(4 * self.density / 15)

    def equals(self, other):
        """True if type, x, y, rot and mag are the same
        """
        return (self.type_id == other.type_id) \
            and (self.x == other.x) and (self.y == other.y) \
            and (self.rot == other.rot) and (self.magnitude == other.magnitude) \
            and (self.data == other.data)

    def to_dict(self):
        changes = {
            "type": self.type_id,
            "x": self.x,
            "y": self.y,
            "magnitude": self.magnitude,
            "rot": self.rot,
            "data": self.data
        }
        return update_dict(self.json_obj, changes)


def update_dict(d, u):
    """
    http://stackoverflow.com/questions/3232943
    /update-value-of-a-nested-dictionary-of-varying-depth
    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def cells_from_json(json_buildings, densities):
    cells = []
    for jcell in json_buildings:
        c = Cell(jcell, densities)
        cells.append(c)

    return cells


def dict_from_cells(cells):
    cell_dict = {}
    for cell in cells:
        cell_dict[cell.get_pos()] = cell
    return cell_dict


def plot_city(city):

    plotWidget = pg.plot()
    building_points = []
    road_points = []
    for c in city.cells.values():
        if c.type_id == ROAD_ID:
            road_points.append(c.get_pos())
        else:
            building_points.append(c.get_pos())

    plotWidget.plot(
        [t[0] for t in road_points], [t[1] for t in road_points],
        pen=None,
        symbol='+')
    plotWidget.plot(
        [t[0] for t in building_points], [t[1] for t in building_points],
        pen=None,
        symbol='s')


def traffic_plot(city):
    data = np.zeros([city.width, city.height])
    for c in city.cells.values():
        data[c.x][-c.y] = c.data["traffic"]
    pg.image(data)


def density_to_pop(type_id, density):
    if type_id not in range(len(POP_ARR)):
        return 0
    return density * POP_ARR[type_id]
