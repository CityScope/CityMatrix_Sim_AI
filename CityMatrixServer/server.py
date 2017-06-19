'''
Filename: server.py
Author: kalyons11 <mailto:kalyons@mit.edu>
Created: 2017-06-01 21:27:53
Last modified by: kalyons11
Last modified time: 2017-06-15 23:50:46
Description:
    - Our complete CityMatrixServer controller. Accepts incoming cities, runs ML + AI work, and
        provides output to Grasshopper.
TODO:
    - None at this time.
'''

''' --- IMPORTS --- '''

import sys, logging

sys.path.extend(['../global/', '../CityPrediction/', '../CityMAItrix/'])
from utils import *
import city_udp, simulator, predictor as ML
from strategies import random_single_moves as Strategy
from objective import objective
log = logging.getLogger('__main__')
result = None #RZ This is necessary to check if ml_city and ai_city has been calculated onece or not
animBlink = 0 #RZ 170614
PRINT_CITY_RECEIVED = False
PRINT_CITY_TO_SEND = True

''' --- CONFIGURATIONS --- '''

# Check input parameters for AUTO_RESTART value
if len(sys.argv) == 2: AUTO_RESTART = False

# Create instance of our server
server = city_udp.City_UDP(SERVER_NAME, receive_port = RECEIVE_PORT, send_port = SEND_PORT)

# Close all ports if server closed
@atexit.register
def register():
    server.close()
    log.warning("Closing all ports for {}.".format(SERVER_NAME))

# Create instance of our simulator, if needed
if DO_SIMULATE: sim = simulator.CitySimulator(SIM_NAME, log)

''' --- GLOBAL HELPER METHODS --- '''

def metrics_dictionary(metrics):
    '''
    Helper method to convert list of tuples to dictionary for JSON submission.
    Input:  metrics - list of tuples of the form [ ('Population Density Performance', 0.11217427049946581, 1) , ... ]
    Output: d - dictionary mapping metric name -> value
    '''

    return { name : [ value , weight ] for name, value, weight in metrics }

''' --- MAIN SERVER LOGIC --- '''

log.info("{} listening on ip: {}, port: {}. Waiting to receive new city...".format(SERVER_NAME, RECEIVE_IP, RECEIVE_PORT))
# TODO add the storage of the previous city that holds the most recent solar radiation values and also lets us find the move made
# TODO push the previous city solar values onto the incoming city immediately (and get the moves made), then don't worry about the previous city anymore, it shouldn't have any impact after that point
# TODO the previous city is first set on the initialization json step
# Constantly loop and wait for new city packets to reach our UDP server
while True:
    # Get city from server and note timestamp
    input_city = server.receive_city()
    timestamp = str(int(time.time()))#RZ 170614 alter animBlink after received a city from GH CV
    if animBlink == 0:
        animBlink = 1
    else:
        animBlink = 0
    #print("animBlink: {}".format(animBlink))

    #RZ 170614 print to check received city
    if PRINT_CITY_RECEIVED:
        print("\nReceived City: ")
        print("densities: {}".format(city.densities))
        print("population: {}".format(city.population))
        print("slider1: {}".format(city.slider1))
        print("slider2: {}".format(city.slider2))
        print("toggle1: {}".format(city.toggle1))
        print("AIWeights: {}".format(city.AIWeights))
        print("startFlag: {}".format(city.startFlag))
        print("AIMov: {}".format(city.AIMov))

    # Only consider new city if it is different from most recent
    if input_city != None:
        key, data = diff_cities(input_city)
        # print(key)
        # print(data)
        # print(input_city.densities, "inp")
        #RZ 170613 for resetting the solar by pressing "startFlag" button in GH CV
        if input_city.startFlag == 1:
            log.info("First/reset city received @ timestamp {}.".format(timestamp))
            inputSimCity = simulator.SimCity(input_city, timestamp)
            write_city(inputSimCity)
            #RZ 170615 score the current city
            ml_city = ML.predict(input_city, key, data)
            mlCityScores = Strategy.scores(ml_city)[1]
            ml_city.updateScores(mlCityScores)
            ai_city, move, ai_metrics_list = Strategy.search(input_city) # TODO change this to ml_city
            ml_city.animBlink = animBlink
            ai_city.animBlink = animBlink
            ml_metrics = metrics_dictionary(objective.get_metrics(ml_city))
            ai_metrics = metrics_dictionary(ai_metrics_list)
            ml_city.updateMeta(input_city)
            ai_city.updateMeta(input_city)
            ml_dict = ml_city.to_dict()
            ml_dict['objects']['metrics'] = ml_metrics
            ai_dict = ai_city.to_dict()
            ai_dict['objects']['metrics'] = ai_metrics
            result = { 'predict' : ml_dict , 'ai' : ai_dict }
            server.send_data(result)
            log.info("First/reset ml_city and ai_city data successfully sent to GH.\n")
        elif key is not CityChange.NO:
            # First, write new city to local file
            log.info("New city received @ timestamp {}.".format(timestamp))
            inputSimCity = simulator.SimCity(input_city, timestamp)
            write_city(inputSimCity)

            # Run our black box predictor on this city with given changes
            ml_city = ML.predict(input_city, key, data)
            # print(ml_city.densities, "ml")

            #RZ 170615 score the current city
            mlCityScores = Strategy.scores(ml_city)[1]
            ml_city.updateScores(mlCityScores)

            # Run our AI on this city
            ai_city, move, ai_metrics_list = Strategy.search(input_city) # TODO change this to ml_city
            # print(ai_city.densities, "ai")

            #RZ 170614 update city.animBlink
            ml_city.animBlink = animBlink
            ai_city.animBlink = animBlink

            # Now, we need to send 2 city objects back to GH
            # First, get metrics dicts for cities
            ml_metrics = metrics_dictionary(objective.get_metrics(ml_city))
            ai_metrics = metrics_dictionary(ai_metrics_list)

            ml_city.updateMeta(input_city)
            ai_city.updateMeta(input_city)

            # Now, update dictionaries
            ml_dict = ml_city.to_dict()
            ml_dict['objects']['metrics'] = ml_metrics
            ai_dict = ai_city.to_dict()
            ai_dict['objects']['metrics'] = ai_metrics

            # Save result locally and send
            result = { 'predict' : ml_dict , 'ai' : ai_dict } # None
            write_city(result, timestamp = timestamp)
            server.send_data(result)
            log.info("New ml_city and ai_city data successfully sent to GH.\n")

            # Now, run the GAMA simulation "async" on this city and save the resulting JSON for later use
            if DO_SIMULATE: sim.simulate(simCity)

            log.info("Waiting to receive new city...")

        elif result is not None: #RZ This is necessary to check if ml_city and ai_city has been calculated onece or not
            #RZ 170614 update city.animBlink
            ml_city.animBlink = animBlink
            ai_city.animBlink = animBlink

            # Then, get metrics dicts for cities
            ml_metrics = metrics_dictionary(objective.get_metrics(ml_city))
            ai_metrics = metrics_dictionary(ai_metrics_list)

            #RZ firstly, we need to update only the meta data of the 2 cities, including slider position and AI Step
            ml_city.updateMeta(input_city)
            ai_city.updateMeta(input_city)

            # Now, update dictionaries
            ml_dict = ml_city.to_dict()
            ml_dict['objects']['metrics'] = ml_metrics
            ai_dict = ai_city.to_dict()
            ai_dict['objects']['metrics'] = ai_metrics

            # Send result
            result = { 'predict' : ml_dict , 'ai' : ai_dict } # None

            #RZ 170614 print to check city to send
            if PRINT_CITY_TO_SEND:
                print("\nml_city to send: ")
                print("densities: {}".format(ml_city.densities))
                print("slider1: {}".format(ml_city.slider1))
                print("slider2: {}".format(ml_city.slider2))
                print("AIWeights: {}".format(ml_city.AIWeights))
                print("startFlag: {}".format(ml_city.startFlag))
                print("AIMov: {}".format(ml_city.AIMov))
                print("animBlink: {}".format(ml_city.animBlink))
                print("scores: {}".format(ml_city.scores))
                print("ai_city to send: ")
                print("densities: {}".format(ai_city.densities))
                print("slider1: {}".format(ai_city.slider1))
                print("slider2: {}".format(ai_city.slider2))
                print("AIWeights: {}".format(ai_city.AIWeights))
                print("startFlag: {}".format(ai_city.startFlag))
                print("AIMov: {}".format(ai_city.AIMov))
                print("animBlink: {}".format(ai_city.animBlink))
                print("scores: {}".format(ai_city.scores))

            server.send_data(result)
            log.info("Same city received. Still sent some metadata to GH. Waiting to receive new city...")

"""
#RZ 170614
Notes for socket error in windows 10:
run flowing in cmd:
FOR /F "tokens=4 delims= " %P IN ('netstat -a -n -o ^| findstr :7000') DO taskKill.exe /PID %P /F

#RZ 170615
Notes for udp ports:
7000 - GH CV send to python server
7001 - python server send to unity
7002 - python server send to GH VIZ
"""
