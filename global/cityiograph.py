# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 23:13:35 2017

@author: Alex, Kevin
"""

''' --- IMPORTS --- '''

import sys
import os
import json
import numpy as np
import collections
import logging

from config import *

''' --- CONFIGURATIONS --- '''

log = logging.getLogger('__main__')

''' --- CLASS DEFINITIONS --- '''

class City(object):
    """General representation of a city matrix.
    
    Attributes:
        AIMov (list): list data describing the move suggested by an AI for a given city 
        cells (dict): (x, y) -> cityiograph.Cell
        densities (list): list of densities for each cell type id in the city
        dockID (TYPE): Description
        dockRotation (TYPE): Description
        height (int): city dimensionality
        json_obj (dict): full JSON object describing the city
        meta (dict): contains meta information about the city, not the grid
        population (int): total population of the city
        scores (list): list of objective scores for the city
        width (int): city dimensionality
    """
    def __init__(self, json_string):
        """Class init method.
        
        Args:
            json_string (str): string from JSON file that describes this city
        """
        self.json_obj = json.loads(json_string)
        self.meta = self.json_obj['objects']

        self.densities = self.meta['densities']
        self.dockID = self.meta['dockID']
        self.dockRotation = self.meta['dockRotation']

        self.cells = dict_from_cells(
            cells_from_json(self.json_obj['grid'], self.densities))
        self.width = max(map(lambda c: c.x, self.cells.values())) + 1
        self.height = max(map(lambda c: c.y, self.cells.values())) + 1

        self.population = 0
        for c in self.cells.values():
            self.population += c.population

    def equals(self, other):
        '''Determines if this city object is equivalent to another. Need all cells, densities and 
            densities to be equal.
        
        Args:
            other (cityiograph.City): the city to be compared
        
        Returns:
            bool: indicates the equality of this city and other
        '''
        cells_equal = all(
            [c.equals(other.cells.get(pos)) for pos, c in self.cells.items()])
        return cells_equal and (self.densities == other.densities) \
            and (self.width == other.width) and (self.height == other.height)

    def to_dict(self):
        '''Converts this city to a dictionary object for storage and other purposes.
        
        Returns:
            dict: dictionary mapping of this city
        '''
        self.meta["densities"] = self.densities
        self.meta["population"] = self.population
        self.meta["dockID"] = self.dockID
        self.meta["dockRotation"] = self.dockRotation

        result = {
            "objects": self.meta,
            "grid": [c.to_dict() for c in self.cells.values()]
        }

        return result

    def updateMeta(self, other_city):
        '''Ignoring a prediction of any sort, simply update the metadata of a given city with the data from another.
        
        Args:
            other_city (cityiograph.City): -
        '''
        self.dockID = other_city.dockID
        self.dockRotation = other_city.dockRotation
        # self.densities = other_city.densities #RZ 170617 shouldn't pass densities, but handled by search()
        # self.AIMov = other_city.AIMov #RZ shouldn't pass from GH CV, but added by python server
        # self.animBlink = other_city.animBlink #RZ this will be handled in server.py

    def updateAIMov(self, mov):
        """Quick method from Ryan to update AI move.
        
        Args:
            mov (unknown): move representation
        """
        pass # self.AIMov = mov

    #RZ 170615
    def updateScores(self, scores):
        """Quick method from Ryan to update AI score values.
        
        Args:
            scores (list): -
        """
        pass # self.scores = scores

    def to_json(self):
        """Converts the current city object to a JSON string.
        
        Returns:
            string: JSON string of city
        """
        return json.dumps(self.to_dict())

    def copy(self):
        """General copy method to avoid object pointer errors.
        
        Returns:
            cityiograph.City: new city with exact same internal data
        """
        return City(self.to_json())

    def get_cell(self, pos):
        """Helper method to get a cell from our dictionary.
        
        Args:
            pos (2-tuple): (x, y) tuple describing the cell location we want to retreive
        
        Returns:
            cityiograph.Cell: the cell object at that location
        """
        return self.cells[pos]

    def get_data_matrix(self, key):
        """Get a data output for the city in a numpy format for data analysis.
        
        Args:
            key (string): data key we will check in cell { 'traffic', 'wait', 'solar' }
        
        Returns:
            nparray (self.height, self.width): -
        """
        result = []
        for x in range(self.width):
            for y in range(self.height):
                cell = self.get_cell((x, y))
                result.append(cell.data[key])
        result = np.array(result).reshape(self.height, self.width)
        return result

    def change_density(self, idx, new_density):
        """Helper method to update a density on a city. Used in AI modeling.
        
        Args:
            idx (int): type id of the density we are updating
            new_density (int): the new density value
        """
        for cell in self.cells.values():
            if cell.type_id == idx:
                cell.density = new_density
                cell.update_pop()

        self.densities[idx] = new_density

    def change_cell(self, x, y, new_id):
        """Helper method to update a particular cell on a city. Used in AI modeling.
        
        Args:
            x (int): x location
            y (int): y location
            new_id (int): the new type id for this paricular cell
        """
        cell = self.cells[(x, y)]
        cell.type_id = new_id

        if cell.type_id == ROAD_ID:
            cell.density = 0
        else:
            cell.density = self.densities[cell.type_id]

        cell.update_pop()

    def write_to_file(self, timestamp):
        """Helper method to write a city to a local filestore for later use.
        
        Args:
            timestamp (str): str UNIX timestamp value when we received this city
        """
        # Get filename
        filename = os.path.join(os.path.abspath(os.path.join(INPUT_CITIES_DIRECTORY,
            'city_input_' + timestamp + ".json")))

        # Write to that file
        with open(filename, 'w') as f:
            f.write(self.to_json())

    def update_values(self, data_array, mode):
        """Given some new data, we want to push this onto the current city.
        
        Args:
            data_array (nparray (self.width * self.height * 2, )): traffic/wait array
            mode (str): describes the type of data copying we are looking for - traffic or solar
        
        Raises:
            ValueError: if an invalid mode string is passed
        """
        i = 0
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cells.get((x, y))
                if mode == 'traffic':
                    cell.data["traffic"] = round(data_array[i], 2) # Rounding to 2 decimals for some precision, without too much
                    cell.data["wait"] = round(data_array[i + 1], 2)
                    i += 2
                elif mode == 'solar':
                    cell.data["solar"] = round(data_array[i], 2)
                    i += 1
                else:
                    raise ValueError("Invalid mode string detected.")

class Cell(object):
    """General representation of a single block within an instance of a cityiograph.City.
    
    Attributes:
        data (dict): contains ML attributes of city
        density (int): -
        height (float): height of cell for solar prediction
        json_obj (dict): full data object
        magnitude (int): ?
        population (int): number of people who live on this cell
        rot (int): direction wrt the table
        type_id (int): -
        x (int): -
        y (int): -
    """
    def __init__(self, json_data, density_array):
        """Class init method.
        
        Args:
            json_data (dict): contains all data for this cell
            density_array (list): list indexed by building type -> density value
        """
        self.json_obj = json_data
        self.type_id = json_data['type']
        self.x = json_data['x']
        self.y = json_data['y']
        try:
            self.rot = json_data['rot']
            self.magnitude = json_data['magnitude']
        except:
            self.rot = 0
            self.magnitude = 0
        self.data = json_data.get('data', {'traffic': 0, "wait": 0, "solar" : 0}) # Changed by Kevin - adding solar

        if self.type_id == ROAD_ID:
            self.density = 0
        else:
            try:
                self.density = density_array[self.type_id]
            except:
                self.density = 0 # Accounting for odd ID case error - Kevin, 5/19/2017

        self.update_pop()
        self.update_height()

    def update_pop(self):
        """Helper method to update the actual population value of a cell - used in feature extraction.
        """
        self.population = density_to_pop(self.type_id, self.density)

    def update_height(self):
        """Helper method to update the actual height value of a cell - used in feature extraction.
        """
        self.height = density_to_height(self.type_id, self.density)

    def get_pos(self):
        """Basic helper method to get location of a cell.
        
        Returns:
            2-tuple: (x, y) location
        """
        return (self.x, self.y)

    def equals(self, other_cell):
        """True if type, x and y are the same.
        
        Args:
            other_cell (cityiograph.Cell): -
        
        Returns:
            bool: indicator of equality
        """
        return (self.type_id == other_cell.type_id) \
            and (self.x == other_cell.x) and (self.y == other_cell.y)

    def to_dict(self):
        """Helper method to convert cell to dictionary object for later use.
        
        Returns:
            dict: -
        """
        result = {
            "type": self.type_id,
            "x": self.x,
            "y": self.y,
            "magnitude": self.magnitude,
            "rot": self.rot,
            "data": self.data
        }
        return result

''' --- GLOBAL HELPER METHODS --- '''

def cells_from_json(json_buildings, densities):
    """Extract cell objects from json.
    
    Args:
        json_buildings (json mapping): input grid of cell data
        densities (list): list of densities for each cell type id in the city
    
    Returns:
        list: cell instances in the city
    """
    cells = []
    for jcell in json_buildings:
        c = Cell(jcell, densities)
        cells.append(c)

    return cells

def dict_from_cells(cells):
    """Provides dictionary mapping (x, y) : cityiograph.Cell.
    
    Args:
        cells (list): cell instances in the city
    
    Returns:
        dict: -
    """
    cell_dict = {}
    for cell in cells:
        cell_dict[cell.get_pos()] = cell
    return cell_dict

def density_to_pop(type_id, density):
    """Converts the raw floor density to actual people living in a cell.
    
    Args:
        type_id (int): -
        density (int): density value for this type id
    
    Returns:
        float: total number of people living at this given location
    """
    if type_id not in range(len(POP_ARR)):
        return 0
    return density * POP_ARR[type_id]

def density_to_height(type_id, density):
    """Converts the raw floor density to the height of a building - used in solar prediction.
    
    Args:
        type_id (int): -
        density (int): density value for this type id
    
    Returns:
        float: height of a cell
    """
    if type_id not in range(len(POP_ARR)):
        return 0
    return density * 3.5

def cell_features(cell, mode):
    '''Get the 2 input features for a given cell.
    
    Args:
        cell (cityiograph.Cell): -
        mode (str): describes the type of feature extraction we are looking for - traffic or solar
    
    Returns:
        list: input features for this cell
    '''
    if mode == 'traffic':
        feats = [ cell.population ]
        feats.append(0) if (cell.type_id == ROAD_ID) else feats.append(1)
    elif mode == 'solar':
        feats = [ cell.height ]
    else:
        raise ValueError("Invalid mode string detected.")
    
    return feats

def cell_results(cell, mode):
    '''Get the 2 output features for a given cell.
    
    Args:
        cell (cityiograph.Cell): -
        mode (str): describes the type of feature extraction we are looking for - traffic or solar
    
    Returns:
        list: output features for this cell
    '''
    if mode == 'traffic':
        return [ cell.data["traffic"], cell.data["wait"] ]
    elif mode == 'solar':
        return [ cell.data["solar"] ]
    else:
        raise ValueError("Invalid mode string detected.")

def get_features(city, mode):
    '''Get the input feature vector for a given city.
    
    Args:
        city (cityiograph.City): -
        mode (str): describes the type of feature extraction we are looking for - traffic or solar
    
    Returns:
        nparray: input features for this city
    '''
    features = []
    for i in range(city.width):
        for j in range(city.height):
            cell = city.cells.get((i, j))
            features.append(cell_features(cell, mode))
    
    return np.array(features)

def get_results(city, mode):
    '''Get the output feature vector for a given city.
    
    Args:
        city (cityiograph.City): -
        mode (str): describes the type of feature extraction we are looking for - traffic or solar
    
    Returns:
        nparray: output features for this city
    '''
    results = []
    for i in range(city.width):
        for j in range(city.height):
            cell = city.cells.get((i, j))
            results.append(cell_results(cell, mode))
    
    return np.array(results)