"""
Our complete CityMatrixServer controller.

Accepts incoming cities, runs ML + AI work, and provides output to Grasshopper.
"""

import sys
import logging

import atexit

sys.path.extend(['../global/', '../CityPrediction/', '../CityMAItrix/'])
import config
from utils import *
import city_udp
import predictor as ML
from strategies import random_single_moves as Strategy
from objective import objective
from cityiograph import *

# Check input parameters for AUTO_RESTART value
if len(sys.argv) == 2:
    AUTO_RESTART = False

# Create instances of our servers
server = city_udp.City_UDP(
    config.SERVER_NAME, receive_port=config.RECEIVE_PORT, send_port=config.SEND_PORT)
unity_server = city_udp.City_UDP(
    config.UNITY_SERVER_NAME, receive_port=config.UNITY_RECEIVE_PORT, send_port=config.UNITY_SEND_PORT)

# Other instance vars
log = logging.getLogger('__main__')
animBlink = 0  # RZ 170614
PRINT_CITY_RECEIVED = False
PRINT_CITY_TO_SEND = True
previous_city = None  # For comparison purposes
AI_move_queue = set()  # KL - keep track of previous moves that have been used


@atexit.register
def register():
    """Helper method to close all ports if server is stopped for some reason.
    """
    server.close()
    log.warning("Closing all ports for {}.".format(config.SERVER_NAME))


log.info("{} listening on ip: {}, port: {}. Waiting to receive new city...".format(
    config.SERVER_NAME, config.RECEIVE_IP, config.RECEIVE_PORT))

# Constantly loop and wait for new city packets to reach our UDP server
while True:
    # Get city from server and note timestamp
    input_city = server.receive_city()
    timestamp = str(int(time.time()))

    # RZ 170614 alter animBlink after received a city from GH CV
    if animBlink == 0:
        animBlink = 1

    else:
        animBlink = 0

    # RZ 170614 print to check received city
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

    # Ensure that there was no error parsing the city JSON packet
    if input_city is not None:
        if previous_city is not None:
            # Check if this city is different from the previous one
            if not previous_city.equals(input_city):
                # New city received - write to local file for later use
                input_city.write_to_file(timestamp)

                # Clear queue
                AI_move_queue = set()

                # Run full ML/AI prediction
                # ML first
                ml_city = ML.predict(input_city)

                # Update previous value
                previous_city = ml_city

                # Compute ML scores
                mlCityScores = Strategy.scores(ml_city)
                ml_city.score = mlCityScores[0]

                # Still run our normal AI on this new ML city
                ai_city, move, ai_metrics_list = Strategy.search(ml_city)

                # Add this move to the queue
                if move[0] == 'DENSITY':
                    move = move[:-1]
                AI_move_queue.add(move)

                # Update city data
                ml_city.animBlink = animBlink
                ai_city.animBlink = animBlink
                ml_city.updateMeta(input_city)
                ai_city.updateMeta(input_city)

                # Save result and send back to GH/Unity
                if input_city.AIStep < 20:  # KL - accounting for AI step case
                    result = {'predict': ml_city.to_dict(), 'ai': None}
                else:
                    result = {'predict': ml_city.to_dict(),
                              'ai': ai_city.to_dict()}
                write_dict(result, timestamp)
                server.send_data(result)
                unity_server.send_data(result)

                log.info("New ml_city and ai_city data successfully sent to GH.\n")
                log.info("Waiting to receive new city...")

            elif input_city.toggle1 != previous_city.toggle1:
                # We have a change in toggle value - we need to send along a new prediction
                # Do not write to file
                # Run full ML/AI prediction
                # ML first
                ml_city = ML.predict(input_city)

                # Update previous value
                previous_city = ml_city

                # Compute ML scores
                mlCityScores = Strategy.scores(ml_city)
                ml_city.score = mlCityScores[0]

                # Still run our normal AI on this new ML city
                ai_city, move, ai_metrics_list = Strategy.search(
                    ml_city, queue=AI_move_queue)

                # Add this move to the queue
                if move[0] == 'DENSITY':
                    move = move[:-1]
                AI_move_queue.add(move)

                # Update city data
                ml_city.animBlink = animBlink
                ai_city.animBlink = animBlink
                ml_city.updateMeta(input_city)
                ai_city.updateMeta(input_city)

                # Save result and send back to GH/Unity
                if input_city.AIStep < 20:  # KL - accounting for AI step case
                    result = {'predict': ml_city.to_dict(), 'ai': None}
                else:
                    result = {'predict': ml_city.to_dict(),
                              'ai': ai_city.to_dict()}
                write_dict(result, timestamp)
                server.send_data(result)
                unity_server.send_data(result)

                log.info(
                    "Same city received, but new toggle value. New ml_city and ai_city data successfully sent to GH.\n")
                log.info("Waiting to receive new city...")

            else:
                # RZ 170626 same city received and not the first city, update
                # meta data for GH UI, do not write to local file

                # RZ 170614 update city.animBlink
                ml_city.animBlink = animBlink
                ai_city.animBlink = animBlink

                # Then, get metrics dicts for cities
                ml_metrics = metrics_dictionary(objective.get_metrics(ml_city))
                ai_metrics = metrics_dictionary(ai_metrics_list)

                # RZ firstly, we need to update only the meta data of the 2
                # cities, including slider position and AI Step
                ml_city.updateMeta(input_city)
                ai_city.updateMeta(input_city)

                # Send resulting 2-city dictionary (predict/ai) back to GH
                if input_city.AIStep < 20:  # KL - accounting for AI step case
                    result = {'predict': ml_city.to_dict(), 'ai': None}
                else:
                    result = {'predict': ml_city.to_dict(),
                              'ai': ai_city.to_dict()}
                server.send_data(result)
                unity_server.send_data(result)

                # RZ 170614 print to check city to send
                if PRINT_CITY_TO_SEND:
                    print("\nml_city to send: ")
                    print("densities: {}".format(ml_city.densities))
                    print("slider1: {}".format(ml_city.slider1))
                    print("slider2: {}".format(ml_city.slider2))
                    print("AIWeights: {}".format(ml_city.AIWeights))
                    print("metrics: {}".format(ml_city.metrics))
                    print("startFlag: {}".format(ml_city.startFlag))
                    print("AIMov: {}".format(ml_city.AIMov))
                    print("animBlink: {}".format(ml_city.animBlink))
                    print("score: {}".format(ml_city.score))
                    print("ai_city to send: ")
                    print("densities: {}".format(ai_city.densities))
                    print("slider1: {}".format(ai_city.slider1))
                    print("slider2: {}".format(ai_city.slider2))
                    print("AIWeights: {}".format(ai_city.AIWeights))
                    print("metrics: {}".format(ai_city.metrics))
                    print("startFlag: {}".format(ai_city.startFlag))
                    print("AIMov: {}".format(ai_city.AIMov))
                    print("animBlink: {}".format(ai_city.animBlink))
                    print("score: {}".format(ai_city.score))

                log.info(
                    "Same city received. Still sent some metadata to GH. Waiting to receive new city...")

        else:
            # This is the first city
            # Write to local file for later use
            input_city.write_to_file(timestamp)

            # Run full ML/AI prediction
            # ML first
            ml_city = ML.predict(input_city)

            # Update previous value
            previous_city = ml_city

            # Compute ML scores
            mlCityScores = Strategy.scores(ml_city)
            ml_city.score = mlCityScores[0]

            # Still run our normal AI on this new ML city
            ai_city, move, ai_metrics_list = Strategy.search(ml_city)

            # Add this move to the queue
            if move[0] == 'DENSITY':
                move = move[:-1]
            AI_move_queue.add(move)

            # Update city data
            ml_city.animBlink = animBlink
            ai_city.animBlink = animBlink
            ml_city.updateMeta(input_city)
            ai_city.updateMeta(input_city)

            # Save result and send back to GH/Unity
            if input_city.AIStep < 20:  # KL - accounting for AI step case
                result = {'predict': ml_city.to_dict(), 'ai': None}
            else:
                result = {'predict': ml_city.to_dict(),
                          'ai': ai_city.to_dict()}
            write_dict(result, timestamp)
            server.send_data(result)
            unity_server.send_data(result)

            log.info("New ml_city and ai_city data successfully sent to GH.\n")
            log.info("Waiting to receive new city...")
