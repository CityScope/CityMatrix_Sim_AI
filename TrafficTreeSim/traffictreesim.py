# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 00:23:07 2017

@author: Alex
"""

import cityiograph
import dijkstra
import time

def traffic_sim(city):
    for destination in city.road_graph.keys():
        cascade_traffic(city, destination)
    

def cascade_traffic(city, destination):
    shortest_paths = dijkstra.shortestPaths(city.road_graph, destination)
    
    for path in shortest_paths:
        traffic = traffic_between(city.get_cell(path[-1]), city.get_cell(destination))
        for road in path:
            city.get_cell(road).traffic += traffic        

def traffic_between(source, destination):
    return source.density * destination.density

t0 = time.clock()
json_filename = "./data/city_1.json"
json_input = open(json_filename).read()

city = cityiograph.City(json_input)
cityiograph.plot_city(city)

road_graph = city.get_road_graph()

traffic_sim(city)
print time.clock() - t0

cityiograph.traffic_plot(city)