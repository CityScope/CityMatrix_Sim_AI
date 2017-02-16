# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 23:13:35 2017

@author: Alex
"""
import json

EDGE_COST = 1
ROAD_ID = 6

class City(object):
    def __init__(self, json_string):
        json_obj = json.loads(json_string)
        self.meta = json_obj['objects']
        self.densities = self.meta['density']
        self.cells = dict_from_cells(cells_from_json(json_obj['grid'], 
                                                     self.densities))
        self.width = max(map(lambda c: c.x, self.cells.values()))
        self.height = max(map(lambda c: c.y, self.cells.values()))
        
        self.graph = self.get_graph()
        self.calculate_road_densities()
        
    def nesw(self, pos):
        x = pos[0]
        y = pos[1]
        directions = []
        if x > 0:
            directions.append((x - 1, y))
        if x < self.width:
            directions.append((x + 1, y))
        if y > 0:
            directions.append((x, y - 1))
        if y < self.height:
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
    
    def calculate_road_densities(self):
        for cell in self.cells.values():
            if cell.type_id == ROAD_ID:
                road_density = 0
                for n in [self.cells[pos] for pos in self.nesw(cell.get_pos())]:
                    if n.type_id != ROAD_ID:
                        road_density += n.density
                cell.density = road_density
    
    def get_road_graph(self):
        road_graph = {}
        for (pos, edges) in self.graph.iteritems():
            if self.cells[pos].type_id == ROAD_ID:
                new_edges = {}
                for (other_pos, cost) in edges.iteritems():
                    if self.cells[other_pos].type_id == ROAD_ID:
                        new_edges[other_pos] = cost
                road_graph[pos] = new_edges
        return road_graph

        
class Cell(object):
    def __init__(self, type_id, x, y, rot, density_arr, magnitude=-1):
        self.type_id = type_id
        self.x = x
        self.y = y
        self.rot = rot
        self.magnitude = magnitude
        
        if type_id == ROAD_ID:
            self.density = 0
        else:
            self.density = density_arr[type_id]
        
    def get_pos(self):
        return (self.x, self.y)
    

def cells_from_json(json_buildings, densities):
    cells = []
    for jcell in json_buildings:
        c = Cell(jcell['type'], jcell['x'], jcell['y'], jcell['rot'], 
                     densities, magnitude=jcell['magnitude'])
        cells.append(c)
        
    return cells
    
    
def dict_from_cells(cells):
    cell_dict = {}
    for cell in cells:
        cell_dict[cell.get_pos()] = cell
    return cell_dict
    