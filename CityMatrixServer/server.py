'''
Filename: server.py
Author: kalyons11 <mailto:kalyons@mit.edu>
Created: 2017-06-01 21:27:53
Last modified by: kalyons11
Last modified time: 2017-06-11 00:20:56
Description:
    - Our complete CityMatrixServer controller. Accepts incoming cities, runs ML + AI work, and
        provides output to Grasshopper.
TODO:
    - None at this time.
'''

# Import local scripts for all key functionality, both ML and AI
import sys, logging

sys.path.extend(['../global/', '../CityPrediction/', '../CityMAItrix/'])
from utils import *
import city_udp, simulator, predictor as ML
#import unity_udp #RZ 170614
from strategies import random_single_moves as Strategy

log = logging.getLogger('__main__')
result = None #RZ This is necessary to check if ml_city and ai_city has been calculated onece or not
animBlink = 0 #RZ 170614
PRINT_CITY_RECEIVED = False
PRINT_CITY_TO_SEND = True

# Check input parameters for AUTO_RESTART value
if len(sys.argv) == 2: AUTO_RESTART = False

# Create instance of our server
server = city_udp.City_UDP(SERVER_NAME, receive_port=RECEIVE_PORT, send_port=SEND_PORT)

#RZ 170614 Create instance of another server to send to unity
#server_unity = unity_udp.Unity_UDP("Send_to_Unity", send_port = 7001)


# Close all ports if server closed
@atexit.register
def register():
    server.close()
    #server_unity.close() #RZ 170614
    log.warning("Closing all ports for {}.".format(SERVER_NAME))


# Create instance of our simulator, if needed
if DO_SIMULATE: sim = simulator.CitySimulator(SIM_NAME, log)

log.info(
    "{} listening on ip: {}, port: {}. Waiting to receive new city...".format(SERVER_NAME, RECEIVE_IP, RECEIVE_PORT))

# Constantly loop and wait for new city packets to reach our UDP server
while True:
    # Get city from server and note timestamp
    city = server.receive_city()
    timestamp = str(int(time.time()))

    #RZ 170614 alter animBlink after received a city from GH CV
    if animBlink == 0: 
        animBlink = 1
    else: 
        animBlink = 0
    #print("animBlink: {}".format(animBlink))

    #RZ 170615 update objective weights


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
    if city != None:
        key, data = diff_cities(city)
        #RZ 170613 
        if city.startFlag == 1 or key is CityChange.FIRST:
            log.info("First city received @ timestamp {}.".format(timestamp))
            ml_city = ML.predict(city, key, data)
            # Write city to local file for later comparison
            simCity = simulator.SimCity(ml_city, timestamp)
            write_city(simCity)
            #RZ 170615 score the current city
            mlCityScores = Strategy.scores(ml_city)[1]
            ml_city.updateScores(mlCityScores)
            # Run our AI on this city
            ai_city, move, metrics = Strategy.search(city)
            #RZ 170614 update city.animBlink
            ml_city.animBlink = animBlink
            ai_city.animBlink = animBlink
            #RZ update city meta data
            ml_city.updateMeta(city)
            ai_city.updateMeta(city)
            # format output json
            result = {'predict': ml_city.to_dict(), 'ai': ai_city.to_dict()}
            # send json via udp
            server.send_data(result)
        elif FORCE_PREDICTION or key is not CityChange.NO:
            # First, write new city to local file
            log.info("New city received @ timestamp {}.".format(timestamp))

            # Run our black box predictor on this city with given changes
            ml_city = ML.predict(city, key, data)

            # Write city to local file for later comparison
            simCity = simulator.SimCity(ml_city, timestamp)
            write_city(simCity)

            #RZ 170615 score the current city
            mlCityScores = Strategy.scores(ml_city)[1]
            ml_city.updateScores(mlCityScores)

            # Run our AI on this city
            ai_city, move, metrics = Strategy.search(city)

            #RZ 170614 update city.animBlink
            ml_city.animBlink = animBlink
            ai_city.animBlink = animBlink
            #RZ update city meta data
            ml_city.updateMeta(city)
            ai_city.updateMeta(city)

            # Now, we need to send 2 city objects back to GH
            result = {'predict': ml_city.to_dict(), 'ai': ai_city.to_dict()}
            server.send_data(result)
            log.info("Predicted city data sent to GH. ")

            # Now, run the GAMA simulation "async" on this city and save the resulting JSON for later use
            if DO_SIMULATE: sim.simulate(simCity)

            log.info("Waiting to receive new city...")

        elif result is not None:  # RZ This is necessary to check if ml_city and ai_city has been calculated onece or not
            #RZ firstly, we need to update only the meta data of the 2 cities, including slider position and AI Step
            #RZ 170614 update city.animBlink
            ml_city.animBlink = animBlink
            ai_city.animBlink = animBlink
            #RZ update city meta data
            ml_city.updateMeta(city)
            ai_city.updateMeta(city)
            result = {'predict': ml_city.to_dict(), 'ai': ai_city.to_dict()}
            
            #RZ 170614 print to check city to send
            if PRINT_CITY_TO_SEND:
                print("\nml_city to send: ")
                print("densities: {}".format(ml_city.densities))
                print("population: {}".format(ml_city.population))
                print("slider1: {}".format(ml_city.slider1))
                print("slider2: {}".format(ml_city.slider2))
                print("toggle1: {}".format(ml_city.toggle1))
                print("AIStep: {}".format(ml_city.AIStep))
                print("AIWeights: {}".format(ml_city.AIWeights))
                print("startFlag: {}".format(ml_city.startFlag))
                print("AIMov: {}".format(ml_city.AIMov))
                print("animBlink: {}".format(ml_city.animBlink))
                print("ai_city to send: ")
                print("densities: {}".format(ai_city.densities))
                print("population: {}".format(ai_city.population))
                print("slider1: {}".format(ai_city.slider1))
                print("slider2: {}".format(ai_city.slider2))
                print("toggle1: {}".format(ai_city.toggle1))
                print("AIStep: {}".format(ai_city.AIStep))
                print("AIWeights: {}".format(ai_city.AIWeights))
                print("startFlag: {}".format(ai_city.startFlag))
                print("AIMov: {}".format(ai_city.AIMov))
                print("animBlink: {}".format(ai_city.animBlink))
            
            #print('result: {}'.format(result))
            server.send_data(result)
            log.info("Same city received. Still sent some metadata to GH and Unity. Waiting to receive new city...")

"""
if socket error in windows 10: 
run flowing in cmd: 
FOR /F "tokens=4 delims= " %P IN ('netstat -a -n -o ^| findstr :7000') DO taskKill.exe /PID %P /F
FOR /F "tokens=4 delims= " %P IN ('netstat -a -n -o ^| findstr :7001') DO taskKill.exe /PID %P /F

udp ports: 
7000 - GH CV send to python server
7001 - python server send to unity
7002 - python server send to GH VIZ
"""