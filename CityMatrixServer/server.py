'''
Filename: server.py
Author: kalyons11 <mailto:kalyons@mit.edu>
Created: 2017-06-01 21:27:53
Last modified by:   kalyons11 
Last modified time: 2017-06-04 20:18:49
Description:
    - Our complete CityMatrixServer controller. Accepts incoming cities, runs ML + AI work, and \
        provides output to Grasshopper.
TODO:
    - None at this time.
'''

# Import local scripts for all key functionality, both ML and AI
import sys, logging
sys.path.extend(['../global/', '../CityPrediction/', '../CityMAItrix/'])
from utils import *
import utils, city_udp, simulator, predictor as ML
from strategies import random_single_moves as Strategy
log = logging.getLogger('__main__')

# Check input parameters for AUTO_RESTART value
if len(sys.argv) == 2: AUTO_RESTART = False

# Create instance of our server
server = city_udp.City_UDP(SERVER_NAME, receive_port = RECEIVE_PORT, send_port = SEND_PORT)

# Close all ports if server closed
@atexit.register
def register():
    server.close()
    log.warning("Closing all ports for {}.".format(SERVER_NAME))

# First, ensure that all directories exist
# Taken from http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
DIRECTORY_LIST = [ INPUT_CITIES_DIRECTORY, OUTPUT_CITIES_DIRECTORY, GAMA_OUTPUT_DIRECTORY, XML_DIRECTORY ]

for d in DIRECTORY_LIST:
    if not os.path.exists(d):
        log.warn("Creating new directory {}.".format(d))
        os.makedirs(d)

# Create instance of our simulator, if needed
if DO_SIMULATE:
    sim = simulator.CitySimulator(SIM_NAME, log)

log.info("{} listening on ip: {}, port: {}.\n".format(SERVER_NAME, RECEIVE_IP, RECEIVE_PORT))
log.info("Waiting to receive new city...")

# Constantly loop and wait for new city packets to reach our UDP server
while LISTENING:
    # Get city from server and note timestamp
    city = server.receive_city()
    timestamp = str(int(time.time()))

    if city != None:

        # Only consider new city if it is different from most recent
        key, data = utils.diff_cities(city)
        if FORCE_PREDICTION or key is not CityChange.NO:
            # First, write new city to local file
            # UNIX logic taken from https://timanovsky.wordpress.com/2009/04/09/get-unix-timestamp-in-java-python-erlang/
            log.info("New city received @ timestamp {}.".format(timestamp))
            simCity = simulator.SimCity(city, timestamp)
            utils.write_city(simCity)

            # Run our black box predictor on this city with given changes
            ml_city = ML.predict(city, key, data)

            # Run our AI on this city
            ai_city, move, metrics = Strategy.search(city)

            # Now, we need to send 2 cities back to Grasshopper
            result = { 'predict' : ml_city.to_dict() , 'ai' : ai_city.to_dict() }

            # city.AIStep = int((math.sin(time.time() * 0.2) * 0.5 + 0.5) * 30) #RZ test changing the AIStep with server
            # log.info('AIStep changed to and send: ' + str(city.AIStep)) #RZ
            server.send_data(result)
            log.info("Predicted city sent!\n")

            # Now, run the GAMA simulation "async" on this city and save the resulting JSON for later use
            if DO_SIMULATE: sim.simulate(simCity)

            log.info("Waiting to receive new city...")

        else:
            # This new city is no different from the previous one
            # Do not send prediction back to server client, just continue
            log.info("Same city received. Waiting to receive new city...")

    else:
        # Invalid city, just continue and wait
        continue