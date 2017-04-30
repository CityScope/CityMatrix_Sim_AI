# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 00:23:07 2017

@author: Alex
"""

import cityiograph
import dijkstra
import time
import os
import imp


def traffic_sim(city):
    road_graph = city.get_road_graph()
    pop_graph = city.get_road_nearby_population_map()
    for destination in road_graph.keys():
        cascade_traffic(city, road_graph, pop_graph, destination)


def cascade_traffic(city, road_graph, pop_graph, destination):
    shortest_paths = dijkstra.shortestPaths(road_graph, destination)

    for path in shortest_paths:
        traffic = traffic_between(pop_graph[path[-1]], pop_graph[destination])
        for road in path:
            city.get_cell(road).data["traffic"] += traffic


def traffic_between(source, destination):
    return source * destination


if __name__ == "__main__":
    in_dir = "./data/input/"
    out_dir = "./data/output/"
    for directory in [x[0] for x in os.walk(in_dir)]:
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                json_input = open(directory + "/" + filename).read()

                city = cityiograph.City(json_input)

                road_graph = city.get_road_graph()

                traffic_sim(city)
                full_out_dir = out_dir + directory.split("/")[-1] + "/"
                if not os.path.exists(os.path.dirname(full_out_dir)):
                    os.makedirs(os.path.dirname(full_out_dir))
                outfile = open(full_out_dir + filename, 'w')
                outfile.write(city.to_json())
