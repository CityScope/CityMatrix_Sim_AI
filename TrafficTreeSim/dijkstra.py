# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 22:49:30 2017

@author: Alex
"""

import heapq

def shortestPaths(graph, start):
    """Implementation of Dijkstra's algorithm to find shortest paths.

    For each node N in graph other than start, finds the shortest path to N 
    from start.
    
    Built off code from
    code.activestate.com/recipes/119466-dijkstras-algorithm-for-shortest-paths/
    """
    queue = [(0, start, [])]
    shortest_paths = []
    seen = set()
    while queue:
        (cost, v, path) = heapq.heappop(queue)
        if v not in seen:
            path = path + [v]
            seen.add(v)
            shortest_paths.append(path + [])
            for (next, c) in graph[v].iteritems():
                heapq.heappush(queue, (cost + c, next, path))
                
