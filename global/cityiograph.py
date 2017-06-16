# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 23:13:35 2017

@author: Alex
"""
import json
import numpy as np
import collections

from config import *

class City(object):
    def __init__(self, json_str, dict_mode = False):
        if dict_mode:
            self.json_obj = json_str
        else:
            self.json_obj = json.loads(json_str)
        self.meta = self.json_obj['objects']

        #RZ 170614 meta data read from json
        try: self.densities = self.meta['densities']
        except:self.densities = [1,1,1,1,1,1]
        try: self.slider1 = self.meta['slider1']
        except: self.slider1 = 0.0
        try: self.slider2 = self.meta['slider2']
        except: self.slider2 = 0.0
        try: self.toggle1 = self.meta['toggle1']
        except: self.toggle1 = 0
        try: self.AIStep = self.meta['AIStep']
        except: self.AIStep = -1
        try: self.AIMov = self.meta['AIMov']
        except: self.AIMov = ['CELL',0,0,0]
        try: self.AIWeights = self.meta['AIWeights']
        except: self.AIWeights = [0.2,0.2,0.2,0.2,0.2]
        try: self.startFlag = self.meta['startFlag']
        except: self.startFlag = 0
        try: self.animBlink = self.meta['animBlink']
        except: self.animBlink = 0
        try: self.scores = self.meta['scores']
        except: self.scores = [0,0,0,0,0]

        self.cells = dict_from_cells(
            cells_from_json(self.json_obj['grid'], self.densities))
        self.width = max(map(lambda c: c.x, self.cells.values())) + 1
        self.height = max(map(lambda c: c.y, self.cells.values())) + 1
        self.AIMov = None

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
        try:
            #RZ 170614
            self.meta["densities"] = self.densities
            self.meta["population"] = self.population
            self.meta["slider1"] = self.slider1
            self.meta["slider2"] = self.slider2
            self.meta["toggle1"] = self.toggle1
            self.meta["AIStep"] = self.AIStep
            self.meta["AIMov"] = self.AIMov
            self.meta["AIWeights"] = self.AIWeights
            self.meta["startFlag"] = self.startFlag
            self.meta["animBlink"] = self.animBlink
            self.meta["scores"] = self.scores
        except: pass # Some older version cities may not have these keys - ignoring
        changes = {
            "objects": self.meta,
            "grid": [c.to_dict() for c in self.cells.values()]
        }
        return update_dict(self.json_obj, changes)

    #RZ pass the data from GH CV to GH VIZ
    def updateMeta(self, city):
        #self.densities = city.densities #RZ can not be here, will overwrite the right densities for AI_city
        #self.population = city.population #RZ can not be here, will overwrite the right population for AI_city
        try:
            #RZ 170614
            self.densities = city.densities
            self.population = city.population
            self.slider1 = city.slider2
            self.slider2 = city.slider2
            self.toggle1 = city.toggle1
            self.AIStep = city.AIStep
            #self.AIMov = city.AIMov #RZ shouldn't pass from GH CV, but added by python server
            self.AIWeights = city.AIWeights
            self.startFlag = city.startFlag
            #self.animBlink = city.animBlink #RZ this will be handled in server.py
        except:
            pass # Added by Kevin - for old cities with bad keys

    #RZ
    def updateAIMov(self, mov):
        self.AIMov = mov

    #RZ 170615
    def updateScores(self, scores):
        self.scores = scores

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
        if self.type_id > 6: self.type_id = -1
        self.x = jcell['x']
        self.y = jcell['y']
        self.rot = jcell['rot']
        self.magnitude = 0 # jcell['magnitude']
        self.data = jcell.get('data', {'traffic': 0, "wait": 0, "solar" : 0}) # Changed by Kevin - adding solar
        #self.data = jcell['data'] #RZ

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
        return float(8 * self.density / 3)

    def equals(self, other):
        """True if type, x, y, rot and mag are the same
        """
        return (self.type_id == other.type_id) \
            and (self.x == other.x) and (self.y == other.y)

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
