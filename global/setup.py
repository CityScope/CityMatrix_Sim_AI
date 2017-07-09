"""
General setup.py script to be run before we start the server for the first time.
"""

import os
import config

# First, ensure that all directories exist
# Taken from
# http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
DIRECTORY_LIST = [config.INPUT_CITIES_DIRECTORY,
                  config.PREDICTED_CITIES_DIRECTORY,
                  config.GAMA_OUTPUT_DIRECTORY,
                  config.XML_DIRECTORY]

for d in DIRECTORY_LIST:
    if not os.path.exists(d):
        print("Creating new directory {}.".format(d))
        os.makedirs(d)
