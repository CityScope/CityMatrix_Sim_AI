'''
Filename:           server.py
Author:             kalyons11 <mailto:kalyons@mit.edu>
Created:               2017-06-01 21:27:53
Last modified by:   kalyons11 
Last modified time: 2017-06-01 21:40:51
Description:
    - Our complete CityMatrixServer controller. Accepts incoming cities, runs ML + AI work, and \
        provides output.
TODO:
    - Setup script of some sort - setup.py.
'''

# Import local scripts for all key functionality 
import sys; sys.path.extend(['../global/', '../CityPrediction/'])
import city_udp
from predictor import *
import sim as simulator

# Create instance of our server
server = city_udp.City_UDP(SERVER_NAME, receive_port = RECEIVE_PORT, send_port = SEND_PORT)

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

log.info("{} listening on ip: {}, port: {}.".format(SERVER_NAME, RECEIVE_IP, RECEIVE_PORT))
log.info("Waiting to receive new city...")

# Constantly loop and wait for new city packets to reach our UDP server
# Taken directly from Alex's code for regression_server.py
while LISTENING:
    # Get city from server
    city = server.receive_city()
    timestamp = str(int(time.time()))

    #RZ
    if city != None:

        # Only consider new city if it is different from most recent
        key, data = diff_cities(city)

        if FORCE_PREDICTION or key is not CityChange.NO:

            # First, write new city to local file
            # UNIX logic taken from https://timanovsky.wordpress.com/2009/04/09/get-unix-timestamp-in-java-python-erlang/
            log.info("New city received @ timestamp {}.".format(timestamp))
            simCity = simulator.SimCity(city, timestamp)
            log.write_city(simCity)

            # Run our black box predictor on this city with given changes
            new_city = predict(city, key, data)

            # Send the new_city object directly back to Grasshopper script via UDP server
            #city.AIStep = int((math.sin(time.time() * 0.2) * 0.5 + 0.5) * 30) #RZ test changing the AIStep with server
            log.info('AIStep changed to and send: ' + str(city.AIStep)) #RZ
            server.send_city(city)
            log.info("Predicted city sent!"+"\n") #RZ

            # Now, run the GAMA simulation "async" on this city and save the resulting JSON for later use
            if DO_SIMULATE: sim.simulate(simCity)

            log.info("Waiting to receive new city...")

        else:
            # This new city is no different from the previous one
            # Do not send prediction back to server client, just continue
            continue

    else:
        print('JSON received invalid!')