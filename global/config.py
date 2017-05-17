'''
    File name: config.py
    Author(s): Kevin Lyons
    Date created: 5/17/2017
    Date last modified: 5/17/2017
    Python Version: 3.5
    Purpose: Configuration file for our project. All filenames are relative to the file in which they are used. May need to change for specific users/machines/operating systems.
'''

# ML variables
LINEAR_MODEL_FILENAME = './model_files/linear_model.pkl' # Pickle file for traffic predictor
ROOT_NN_FILENAME = './model_files/neural_model' # Root name for neural network JSON/H5
NUM_FEATURES = 512 # Traffic and wait for 256 cells = 512
MATRIX_SHAPE = (-1, 16, 16, 2) # 3D matrix representation of our city grid as "image" for CNN

# Server variables
LISTENING = True # Bool to say whether or not we want our server to be "on" and listening
SERVER_NAME = 'Prediction_Server'
RECEIVE_IP = "127.0.0.1"
RECEIVE_PORT = 9000
SEND_IP = "127.0.0.1"
SEND_PORT = 9001

# Log variables
LOGGER_NAME = 'CityLog'
INPUT_CITIES_DIRECTORY = './input_cities/'
OUTPUT_DIRECTORY = './sim_output/'
LOGGER_FILENAME = './log.log'

# Simulator variables
SIM_NAME = 'PythonSim'
GAMA_PATH = '/Applications/Gama.app/Contents/headless/gama-headless.sh'
XML_PATH = '../CityGamatrix/experiment.xml'
GAMA_COMMANDS = ['sh', GAMA_PATH, '-c', '-v', XML_PATH]

# City variables
ROAD_ID = 6