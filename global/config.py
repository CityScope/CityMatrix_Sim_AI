"""
Configuration file for our project.

Note: all filenames are relative to the file in which they are used.
"""

import os

# Environment configs
SERVER_OS = 'MAC'  # Operating system of the prediction server, either MAC or WIN
# Version we are running the server on - used for restart command
PYTHON_VERSION = 'python3.5'
DEBUG = True

# Server variables
SERVER_NAME = 'CityMatrixServer'
RECEIVE_IP = "127.0.0.1"
RECEIVE_PORT = 7000
SEND_IP = "127.0.0.1"
SEND_PORT = 7002

UNITY_SERVER_NAME = 'UnityServer'
UNITY_RECEIVE_PORT = 7009
UNITY_SEND_PORT = 7003

# If we want to ignore diff feature and always predict for debugging purposes
FORCE_PREDICTION = False
AUTO_RESTART = not DEBUG  # Do we want to restart the server if it goes down?
# List of e-mails we want to notify if the server crashes
EMAIL_LIST = ['kalyons@mit.edu', 'popabczhang@gmail.com']
# Stores e-mail username and password information
CREDENTIALS_FILENAME = '../CityMatrixServer/credentials.p'
SMTP_HOSTNAME = 'smtp.gmail.com'  # Google SMTP server hostname for e-mail service
SMTP_PORT = 587  # Default Google SMTP server port
# Relative path from utils script
SERVER_FILENAME = '../CityMatrixServer/server.py'

# City variables
CITY_SIZE = 16
ROAD_ID = 6  # ID of a road cell on our grid matrix
# Array representing the number of people per floor in each building type
POP_ARR = [5, 8, 16, 16, 23, 59]
EDGE_COST = 1  # Used in graph creation'
DENSITY_TO_HEIGHT_FACTOR = 3.5  # Used for solar radiation analysis

# Machine learning variables
MODEL_DIR = '../CityPrediction/model_files/'
# Pickle file for traffic predictor
LINEAR_MODEL_FILENAME = os.path.join(MODEL_DIR, 'linear_traffic_model.pkl')
# Pickle file for solar predictor
SOLAR_MODEL_FILENAME = os.path.join(MODEL_DIR, 'linear_solar_model.pkl')

# Log variables
# Directory to save incoming cities, before prediction
INPUT_CITIES_DIRECTORY = '../CityPrediction/input_cities/'
# Directory to save outgoing cities, after prediction
PREDICTED_CITIES_DIRECTORY = '../CityPrediction/predicted_cities/'
LOGGER_FILENAME = 'output.log'  # Log file

# Simulator variables
DO_SIMULATE = False  # Bool to say if we run the GAMA simulator on the file or not
SIM_NAME = 'PythonSim'  # Name of our simulator for ID purposes
# GAMA simulation script
SIM_SCRIPT_PATH = '../../CityGamatrix/models/CityGamatrix_PEV.gaml'
# Output directory for misc GAMA needs
GAMA_OUTPUT_DIRECTORY = '../CityPrediction/sim_output/'
# Directory to save custom XML configuration files
XML_DIRECTORY = '../CityPrediction/xml/'
DEFAULT_XML = {'Experiment_plan':
               {'Simulation': {'@finalStep': '8642', '@id': '1', '@experiment': 'Run',
                               'Parameters': {'Parameter': [{'@value': 'TMP_VALUE', '@name': 'filename', '@type': 'STRING'},
                                                            {'@value': 'TMP_VALUE', '@name': 'output_dir', '@type': 'STRING'}, {'@value': 'TMP_VALUE',
                                                                                                                                '@name': 'prefix', '@type': 'STRING'}]}, '@sourcePath': SIM_SCRIPT_PATH}}}
# Data dictionary that is to be converted into XML

# Other vars
if SERVER_OS == 'MAC':
    # Path to Eclipse JAR file needed for GAMA plugins
    JAR_PATH = '/Applications/Gama.app/Contents/Eclipse/plugins/org.eclipse.equinox.launcher_1.3.100.v20150511-1540.jar'
    GAMA_COMMANDS = ['java', '-cp', JAR_PATH, '-Xms512m', '-Xmx2048m', '-Djava.awt.headless=true', 'org.eclipse.core.launcher.Main',
                     '-application', 'msi.gama.headless.id4', 'XML_PATH', GAMA_OUTPUT_DIRECTORY]  # Command list for subprocess.Popen
