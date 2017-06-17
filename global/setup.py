'''
Filename: setup.py
Author: kalyons11 <mailto:kalyons@mit.edu>
Created: 2017-06-04 20:23:55
Last modified by: kalyons11
Last modified time: 2017-06-11 23:20:57
Description:
    - General setup.py script to be run before we start the server for the first time.
TODO:
    - None at this time.
'''

import os
from config import *

# First, ensure that all directories exist
# Taken from http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
DIRECTORY_LIST = [ INPUT_CITIES_DIRECTORY, PREDICTED_CITIES_DIRECTORY, GAMA_OUTPUT_DIRECTORY, XML_DIRECTORY ]

for d in DIRECTORY_LIST:
    if not os.path.exists(d):
        print("Creating new directory {}.".format(d))
        os.makedirs(d)