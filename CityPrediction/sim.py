'''
    File name: sim.py
    Author(s): Kevin Lyons
    Date created: 5/16/2017
    Date last modified: 5/19/2017
    Python Version: 3.5
    Purpose: Python script that should call GAMA simulator in "headless mode" to run a particular JSON file. Should return the results of that simulation to be saved later on.
    TODO:
    	- None at this time.
'''

# Global imports
import sys, xmltodict, json, time, os, copy
from subprocess import Popen

# Custom imports
sys.path.append('../global/')
import utils
from config import *

# Class method for our simulator
class CitySimulator:
	def __init__(self, name, log):
		self.name = name # Name to help us ID the sim
		self.log = log # Existing instance of utils.CityLogger so we can write to JSON

	def simulate(self, city):
		'''
		Input: city - instance of SimCity
		Output: None - write simulation output to specific file through GAMA
		'''

		# First, write filename to our experiment file
		commands = GAMA_COMMANDS[:]
		commands[-2] = city.xml
		self.update_parameters(city)

		# Using subprocess to run command and check progress
		# Taken from http://stackoverflow.com/questions/636561/how-can-i-run-an-external-command-asynchronously-from-python
		# Begin process on new thread
		utils.async_process(commands, self.complete, self.log, city)
		self.log.info("Simulation initialized for file {}.".format(city.filename))

	def complete(self, city):
		'''
		Input: city - instance of SimCity that has just been simulated
		Output: None - simply log that we are done
		'''

		# Need to take result from process and act accordingly
		self.log.info("Simulation complete for file {}.".format(city.filename))

	def update_parameters(self, city):
		'''
		Input: city - instance of SimCity that has just been simulated
		Output: None - update XML file to have this city's data
		'''

		# Now, update values in default dictionary to correct data
		d = copy.deepcopy(DEFAULT_XML)
		d['Experiment_plan']['Simulation']['Parameters']['Parameter'][0]['@value'] = city.filename # filename
		d['Experiment_plan']['Simulation']['Parameters']['Parameter'][1]['@value'] = os.path.abspath(OUTPUT_CITIES_DIRECTORY) + '/' # output_dir
		d['Experiment_plan']['Simulation']['Parameters']['Parameter'][2]['@value'] = city.prefix # prefix

		# Convert dict back to XML and write to file
		with open(city.xml, 'w') as f:
			f.write(xmltodict.unparse(d, pretty = True))

# Class that represents a city object being passed along to GAMA
# Different from cityiograph.City object
class SimCity:
	def __init__(self, cityObject, timestamp):
		self.cityObject = cityObject # Instance of cityiograph.City object
		self.timestamp = timestamp # UNIX timestamp
		self.prefix = "city_" + timestamp # Prefix
		self.filename = self.get_full_filename(INPUT_CITIES_DIRECTORY) # Full filename
		self.xml = self.get_xml_path() # Path to corresponding XML path

	def get_xml_path(self):
		'''
		Input: None
		Output: full XML path for this city
		'''

		# Experiment filename convention
		return os.path.abspath(XML_DIRECTORY + 'experiment_' + self.timestamp + '.xml')

	def get_full_filename(self, directory, mode = ".json"): # Default JSON extension mode
		'''
		Input: directory - dir where we want to save this file to
			   mode - extension for this file
		Output: formatted_filename - properly updated to reflect filename format for later ML prediction, full path
		'''

		# Create output directory if needed
		# Taken from http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
		if not os.path.exists(directory):
			os.makedirs(directory)

		return os.path.abspath(directory + self.prefix + mode)