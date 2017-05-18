'''
    File name: sim.py
    Author(s): Kevin Lyons
    Date created: 5/16/2017
    Date last modified: 5/18/2017
    Python Version: 3.5
    Purpose: Python script that should call GAMA simulator in "headless mode" to run a particular JSON file. Should return the results of that simulation to be saved later on.
    TODO:
    	- Need to get OUTPUT of GAMA simulation as well... then, update network later. Filename matching is key!
    	- Passing data dictionary through calls.
'''

# Global imports
import sys, xmltodict, json, time
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

	def simulate(self, city, filename, prefix):
		'''
		Input: city - instance of cityiograph.City - city to be simulated in GAMA
			   filename - full string of input JSON
			   prefix - raw name of file with timestamp, to be used for output later on
		Output: None - write simulation output to specific file through GAMA
		'''

		# First, write filename to our experiment file
		self.update_filename(filename)

		# Using subprocess to run command and check progress
		# Taken from http://stackoverflow.com/questions/636561/how-can-i-run-an-external-command-asynchronously-from-python
		# Begin process on new thread
		utils.async_process(GAMA_COMMANDS, self.complete)
		self.log.info("Simulation initialized for file {}.".format(filename))

	def complete(self, process):
		'''
		Input: process - instance of subprocess.Popen that was run async
		Output: TBD
		'''

		# Need to take result from process and act accordingly
		pass

	def update_filename(self, filename):
		'''
		Input: filename - full string of input JSON file
		Output: None - update XML file to have this filename
		'''

		# Load XML file from memory
		with open(XML_PATH, 'r') as f:
			# Get dictionary from XML file
			# Taken from multiple sources
			# http://stackoverflow.com/questions/20166749/how-to-convert-an-ordereddict-into-a-regular-dict-in-python3
			# https://github.com/martinblech/xmltodict
			d = json.loads(json.dumps(xmltodict.parse(f.read())))

			# d is of the form: {'Experiment_plan': {'Simulation': {'@experiment': 'Run', '@finalStep': '8642', '@sourcePath': './models/CityGamatrix.gaml', 'Parameters': {'Parameter': {'@value': 'TEMP_VALUE', '@name': 'filename', '@type': 'STRING'}}, '@id': '1'}}}
			# Now, update value in d to correct filename
			d['Experiment_plan']['Simulation']['Parameters']['Parameter']['@value'] = filename

		# Convert dict back to XML and write to file
		with open(XML_PATH, 'w') as f:
			f.write(xmltodict.unparse(d, pretty = True))