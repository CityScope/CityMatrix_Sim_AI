'''
    File name: config.py
    Author(s): Kevin Lyons
    Date created: 5/17/2017
    Date last modified: 5/20/2017
    Python Version: 3.5
    Purpose: Configuration file for our project. All filenames are relative to the file in which they are used.
    TODO:
    	- None at this time.
'''

# City variables
ROAD_ID = 6 # ID of a road cell on our grid matrix
POP_ARR = [5, 8, 16, 16, 23, 59] # Array representing the number of people per floor in each building type
EDGE_COST = 1 # Used in graph creation

# Machine learning variables
LINEAR_MODEL_FILENAME = './model_files/linear_model.pkl' # Pickle file for traffic predictor
ROOT_NN_FILENAME = './model_files/neural_model' # Root name for neural network JSON/H5
NUM_FEATURES = 512 # Traffic and wait for 256 cells = 512
MATRIX_SHAPE = (-1, 16, 16, 2) # 3D matrix representation of our city grid as "image" for CNN
LOSS_FUNCTION = 'mean_squared_error' # Loss function for our neural network
OPTIMIZER = 'adam' # Using adam, not SGD
KERAS_METRICS = ['accuracy'] # Percent accuracy metric

# Server variables
LISTENING = True # Bool to say whether or not we want our server to be "on" and listening
SERVER_NAME = 'Prediction_Server'
RECEIVE_IP = "127.0.0.1"
RECEIVE_PORT = 9000
SEND_IP = "127.0.0.1"
SEND_PORT = 9001
FORCE_PREDICTION = False # If we want to ignore diff feature and always predict for debugging purposes

# Log variables
LOGGER_NAME = 'CityLog' # Name of our logger for ID purposes
INPUT_CITIES_DIRECTORY = './input_cities/' # Directory to save incoming cities, before simulation
OUTPUT_CITIES_DIRECTORY = './output_cities/' # Directory to save outgoing cities, after simulation
LOGGER_FILENAME = './output.log' # Log file

# Simulator variables
SIM_NAME = 'PythonSim' # Name of our simulator for ID purposes
SIM_SCRIPT_PATH = '../../CityGamatrix/models/CityGamatrix_PEV.gaml' # GAMA simulation script
GAMA_OUTPUT_DIRECTORY = './sim_output/' # Output directory for misc GAMA needs
XML_DIRECTORY = './xml/' # Directory to save custom XML configuration files
DEFAULT_XML = {'Experiment_plan': {'Simulation': {'@finalStep': '8642', '@id': '1', '@experiment': 'Run', 'Parameters': {'Parameter': [{'@value': 'TMP_VALUE', '@name': 'filename', '@type': 'STRING'}, {'@value': 'TMP_VALUE', '@name': 'output_dir', '@type': 'STRING'}, {'@value': 'TMP_VALUE', '@name': 'prefix', '@type': 'STRING'}]}, '@sourcePath': SIM_SCRIPT_PATH }}} # Data dictionary that is to be converted into XML
SERVER_OS = 'MAC' # Operating system of the prediction server
if SERVER_OS == 'MAC':
	JAR_PATH = '/Applications/Gama.app/Contents/Eclipse/plugins/org.eclipse.equinox.launcher_1.3.100.v20150511-1540.jar' # Path to Eclipse JAR file needed for GAMA plugins
	GAMA_COMMANDS = ['java', '-cp', JAR_PATH, '-Xms512m', '-Xmx2048m', '-Djava.awt.headless=true', 'org.eclipse.core.launcher.Main', '-application', 'msi.gama.headless.id4', 'XML_PATH', GAMA_OUTPUT_DIRECTORY] # Command list for subprocess.Popen