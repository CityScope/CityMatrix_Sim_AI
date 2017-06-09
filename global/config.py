'''
    File name: config.py
    Author(s): Kevin Lyons
    Date created: 5/17/2017
    Date last modified: 6/8/2017
    Python Version: 3.5
    Purpose: Configuration file for our project. All filenames are relative to the file in which they
        are used.
    TODO:
    	- None at this time.
'''

# City variables
ROAD_ID = 6 # ID of a road cell on our grid matrix
POP_ARR = [5, 8, 16, 16, 23, 59] # Array representing the number of people per floor in each building type
EDGE_COST = 1 # Used in graph creation

# Machine learning variables
MODEL_DIR = '../CityPrediction/model_files/'
LINEAR_MODEL_FILENAME = MODEL_DIR + 'linear_model.pkl' # Pickle file for traffic predictor
ROOT_NN_FILENAME = MODEL_DIR + 'neural_model' # Root name for neural network JSON/H5 model/weights files
SOLAR_MODEL_FILENAME = MODEL_DIR + 'solar_model.pkl' # Pickle file for solar predictor
NUM_FEATURES = 512 # Traffic and wait for 256 cells = 512
MATRIX_SHAPE = (-1, 16, 16, 2) # 3D matrix representation of our city grid as "image" for CNN
LOSS_FUNCTION = 'mean_squared_error' # Loss function for our neural network
OPTIMIZER = 'adam' # Using adam, not SGD
KERAS_METRICS = ['accuracy'] # Percent accuracy metric

# Server variables
SERVER_NAME = 'CityMatrixServer'
RECEIVE_IP = "127.0.0.1"
RECEIVE_PORT = 7000
SEND_IP = "127.0.0.1"
SEND_PORT = 7002
FORCE_PREDICTION = False # If we want to ignore diff feature and always predict for debugging purposes
AUTO_RESTART = True # Do we want to restart the server if it goes down?
EMAIL_LIST = [ 'kalyons@mit.edu' , 'popabczhang@gmail.com' ] # List of e-mails we want to notify if the server crashes
CREDENTIALS_FILENAME = '../CityMatrixServer/credentials.p' # Stores e-mail username and password information
SMTP_HOSTNAME = 'smtp.gmail.com' # Google SMTP server hostname for e-mail service
SMTP_PORT = 587 # Default Google SMTP server port
PYTHON_VERSION = 'python3.5' # Version we are running the server on - used for restart command
SERVER_FILENAME = '../CityMatrixServer/server.py' # Relative path from utils script

# Log variables
INPUT_CITIES_DIRECTORY = '../CityPrediction/input_cities/' # Directory to save incoming cities, before simulation
OUTPUT_CITIES_DIRECTORY = '../CityPrediction/output_cities/' # Directory to save outgoing cities, after simulation
LOGGER_FILENAME = 'output.log' # Log file

# Simulator variables
DO_SIMULATE = False # Bool to say if we run the GAMA simulator on the file or not
SIM_NAME = 'PythonSim' # Name of our simulator for ID purposes
SIM_SCRIPT_PATH = '../../CityGamatrix/models/CityGamatrix_PEV.gaml' # GAMA simulation script
GAMA_OUTPUT_DIRECTORY = '../CityPrediction/sim_output/' # Output directory for misc GAMA needs
XML_DIRECTORY = '../CityPrediction/xml/' # Directory to save custom XML configuration files
DEFAULT_XML = {'Experiment_plan': {'Simulation': {'@finalStep': '8642', '@id': '1', '@experiment': 'Run', 'Parameters': {'Parameter': [{'@value': 'TMP_VALUE', '@name': 'filename', '@type': 'STRING'}, {'@value': 'TMP_VALUE', '@name': 'output_dir', '@type': 'STRING'}, {'@value': 'TMP_VALUE', '@name': 'prefix', '@type': 'STRING'}]}, '@sourcePath': SIM_SCRIPT_PATH }}} # Data dictionary that is to be converted into XML

# Environment variables
SERVER_OS = 'MAC' # Operating system of the prediction server, either MAC or WIN
if SERVER_OS == 'MAC':
	JAR_PATH = '/Applications/Gama.app/Contents/Eclipse/plugins/org.eclipse.equinox.launcher_1.3.100.v20150511-1540.jar' # Path to Eclipse JAR file needed for GAMA plugins
	GAMA_COMMANDS = ['java', '-cp', JAR_PATH, '-Xms512m', '-Xmx2048m', '-Djava.awt.headless=true', 'org.eclipse.core.launcher.Main', '-application', 'msi.gama.headless.id4', 'XML_PATH', GAMA_OUTPUT_DIRECTORY] # Command list for subprocess.Popen