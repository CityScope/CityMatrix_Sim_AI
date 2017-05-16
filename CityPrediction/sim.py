'''
    File name: sim.py
    Author(s): Kevin Lyons, Alex Aubuchon
    Date created: 5/16/2017
    Date last modified: 5/16/2017
    Python Version: 3.5
    Purpose: Python script that should call GAMA simulator in "headless mode" to run a particular JSON file. Should return the results of that simulation to be saved later on.
    TODO:
    	- Implement XML schema for GAMA headless mode. May need module import here.
'''

# Global imports
import sys

# Custom imports
sys.path.append('../global/')
import utils

# Global instance variables
GAMA_PATH = ''

# Class method for our simulator
class CitySimulator:
	def __init__(self, name, log):
		self.name = name # Name to help us ID the sim
		self.log = log # Instance of utils.CityLogger so we can write to JSON

	def simulate(self, city, filename):
		'''
		Input: city - instance of cityiograph.City - city to be simulated in GAMA
			   filename - raw prefix string of filename - need to format
		Output: None - write simulation output to specific file through GAMA
		'''
		
		print("Simulation complete!")