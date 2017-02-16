# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 00:23:07 2017

@author: Alex
"""

import cityiograph

json_filename = "../CityGenerator/out/city_000.json"
json_input = open(json_filename).read()

city = cityiograph.City(json_input)

road_graph = city.get_road_graph()




def traffic_between(source, destination):
    return source.density * destination.density