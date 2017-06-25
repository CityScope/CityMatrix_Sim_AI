'''
Filename: server.py
Author: kalyons11 <mailto:kalyons@mit.edu>
Created: 2017-06-01 21:27:53
Last modified by: kalyons11
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
import city_udp, predictor as ML
from strategies import random_single_moves as Strategy
from objective import objective
log = logging.getLogger('__main__')
result = None #RZ This is necessary to check if ml_city and ai_city has been calculated onece or not
animBlink = 0 #RZ 170614
PRINT_CITY_RECEIVED = False
PRINT_CITY_TO_SEND = True
previous_city = None

''' --- CONFIGURATIONS --- '''

# Check input parameters for AUTO_RESTART value
if len(sys.argv) == 2: AUTO_RESTART = False

# Create instance of our server
server = city_udp.City_UDP(SERVER_NAME, receive_port = RECEIVE_PORT, send_port = SEND_PORT)
unity_server = city_udp.City_UDP("Unity_Test_Sever", receive_port = 7009, send_port = 7001)

# Close all ports if server closed
@atexit.register
def register():
    server.close()
    log.warning("Closing all ports for {}.".format(SERVER_NAME))

''' --- GLOBAL HELPER METHODS --- '''

def metrics_dictionary(metrics):
    '''Helper method to convert list of tuples to dictionary for JSON submission.
    
    Args:
        metrics (list): list of tuples (name, value, weight)
    
    Returns:
        dict: dictionary mapping metric name -> value and weight
    '''
    return { name : [ value , weight ] for name, value, weight in metrics }

def write_dict(result_dict, timestamp):
    """Helper method to write our output prediction dictionary to JSON.
    
    Args:
        result_dict (dict): output from ML/AI work
        timestamp (str): -
    """
    # Get filename
    filename = os.path.join(PREDICTED_CITIES_DIRECTORY, 'city_predictions_' + timestamp + '.json')

    # Write dictionary
    with open(filename, 'w') as f:
        f.write(json.dumps(result_dict))    

''' --- MAIN SERVER LOGIC --- '''

log.info("{} listening on ip: {}, port: {}. Waiting to receive new city...".format(SERVER_NAME, RECEIVE_IP, RECEIVE_PORT))

# Constantly loop and wait for new city packets to reach our UDP server
while True:
    # Get city from server and note timestamp
    input_city = server.receive_city()
    timestamp = str(int(time.time()))

    #RZ 170614 alter animBlink after received a city from GH CV
    if animBlink == 0:
        animBlink = 1
    else:
        animBlink = 0

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

    # Ensure that there was no error parsing the city json packet
    if input_city != None:
        # Write to local file for later use
        input_city.write_to_file(timestamp)

        if previous_city is not None:
            # Check if this city is different from the previous one
            if not previous_city.equals(input_city):
                # Run full ML/AI prediction
                # ML first
                ml_city = ML.predict(input_city)

                # Update previous value
                previous_city = ml_city

                # Compute ML scores
                mlCityScores = Strategy.scores(ml_city)[1]
                ml_city.updateScores(mlCityScores)

                # Still run our normal AI on this new ML city
                ai_city, move, ai_metrics_list = Strategy.search(ml_city)

                # Update animation
                ml_city.animBlink = animBlink
                ai_city.animBlink = animBlink

                # Get metrics
                ml_metrics = metrics_dictionary(objective.get_metrics(ml_city))
                ai_metrics = metrics_dictionary(ai_metrics_list)
                ml_city.updateMeta(input_city)
                ai_city.updateMeta(input_city)
                ml_dict = ml_city.to_dict()
                ml_dict['objects']['metrics'] = ml_metrics
                ai_dict = ai_city.to_dict()
                ai_dict['objects']['metrics'] = ai_metrics

                # Save result and send back to GH/Unity
                result = { 'predict' : ml_dict , 'ai' : ai_dict }
                
                write_dict(result, timestamp)
                server.send_data(result)
                unity_server.send_data(result)

                log.info("New ml_city and ai_city data successfully sent to GH.\n")
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

                # Send resulting 2-city dictionary (predict/ai) back to GH
                result = { 'predict' : ml_dict , 'ai' : ai_dict }
                server.send_data(result)
                unity_server.send_data(result)

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
                
                log.info("Same city received. Still sent some metadata to GH. Waiting to receive new city...")

        else:
            # This is the first city
            # Run full ML/AI prediction
            # ML first
            ml_city = ML.predict(input_city)

            # Update previous value
            previous_city = ml_city

            # Compute ML scores
            mlCityScores = Strategy.scores(ml_city)[1]
            ml_city.updateScores(mlCityScores)

            # Still run our normal AI on this new ML city
            ai_city, move, ai_metrics_list = Strategy.search(ml_city)

            # Update animation
            ml_city.animBlink = animBlink
            ai_city.animBlink = animBlink

            # Get metrics
            ml_metrics = metrics_dictionary(objective.get_metrics(ml_city))
            ai_metrics = metrics_dictionary(ai_metrics_list)
            ml_city.updateMeta(input_city)
            ai_city.updateMeta(input_city)
            ml_dict = ml_city.to_dict()
            ml_dict['objects']['metrics'] = ml_metrics
            ai_dict = ai_city.to_dict()
            ai_dict['objects']['metrics'] = ai_metrics

            # Save result and send back to GH/Unity
            result = { 'predict' : ml_dict , 'ai' : ai_dict }
            
            write_dict(result, timestamp)
            server.send_data(result)
            unity_server.send_data(result)

            log.info("New ml_city and ai_city data successfully sent to GH.\n")
            log.info("Waiting to receive new city...")

"""
#RZ 170614
Notes for socket error in windows 10:
run following in cmd:

FOR /F "tokens=4 delims= " %P IN ('netstat -a -n -o ^| findstr :7000') DO taskKill.exe /PID %P /F

#KL 170621
Notes for socket error in Mac OSX:
run following in Terminal:

lsof -i :7000
kill -9 <PID given by previous command>

#RZ 170615
Notes for udp ports:
7000 - GH CV send to python server
7001 - python server send to unity
7002 - python server send to GH VIZ
"""
