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

# Constantly loop and wait for new city packets to reach our UDP server
while True:
    # Get city from server and note timestamp
    input_city = server.receive_city()
    timestamp = str(int(time.time()))

    # Only consider new city if it is different from most recent
    if input_city != None:
        key, data = diff_cities(input_city)
        # print(key)
        # print(data)
        # print(input_city.densities, "inp")
        if key is not CityChange.NO:
            # First, write new city to local file
            log.info("New city received @ timestamp {}.".format(timestamp))
            inputSimCity = simulator.SimCity(input_city, timestamp)
            write_city(inputSimCity)

            # Run our black box predictor on this city with given changes
            ml_city = ML.predict(input_city, key, data)
            # print(ml_city.densities, "ml")

            # Run our AI on this city
            ai_city, move, ai_metrics_list = Strategy.search(input_city)
            # print(ai_city.densities, "ai")

            # Now, we need to send 2 city objects back to GH
            # First, get metrics dicts for cities
            ml_metrics = metrics_dictionary(objective.get_metrics(ml_city))
            ai_metrics = metrics_dictionary(ai_metrics_list)

            # Now, update dictionaries
            ml_dict = ml_city.to_dict()
            ml_dict['objects']['metrics'] = ml_metrics
            ai_dict = ai_city.to_dict()
            ai_dict['objects']['metrics'] = ai_metrics

            # Save result locally and send
            result = { 'predict' : ml_dict , 'ai' : ai_dict } # None
            write_city(result, timestamp = timestamp)
            server.send_data(result)
            log.info("Predicted city data successfully sent to GH.\n")

            # Now, run the GAMA simulation "async" on this city and save the resulting JSON for later use
            if DO_SIMULATE: sim.simulate(simCity)

            log.info("Waiting to receive new city...")

        elif result is not None: #RZ This is necessary to check if ml_city and ai_city has been calculated onece or not
            #RZ firstly, we need to update only the meta data of the 2 cities, including slider position and AI Step
            ml_city.updateMeta(input_city) #RZ necessary, do not delete
            ai_city.updateMeta(input_city) #RZ necessary, do not delete

            # Then, get metrics dicts for cities
            ml_metrics = metrics_dictionary(objective.get_metrics(ml_city))
            ai_metrics = metrics_dictionary(ai_metrics_list)

            # Now, update dictionaries
            ml_dict = ml_city.to_dict()
            ml_dict['objects']['metrics'] = ml_metrics
            ai_dict = ai_city.to_dict()
            ai_dict['objects']['metrics'] = ai_metrics

            # Send result
            result = { 'predict' : ml_dict , 'ai' : ai_dict } # None
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