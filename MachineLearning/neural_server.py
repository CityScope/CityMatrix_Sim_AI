'''
    File name: neural_server.py
    Author(s): Kevin Lyons, Alex Aubuchon
    Date created: 4/07/2017
    Date last modified: 4/14/2017
    Python Version: 3.5
    Purpose: Create UDP server that can wait for new cities from Grasshopper, predict traffic and wait output given structure and population, and send that result back to Grasshopper. This server uses the CNN stored in the saved_model.json and saved_model.h5 local files. This can be configured with the ROOT_FILENAME parameter.
    TODO:
    - Still need to have some sort of update() function that fits the model on some new set of data points
'''

import sys, time, traffic_regression

from keras.models import model_from_json

# Import local scripts for city utils

sys.path.insert(0, '../TrafficTreeSim/')
import cityiograph

sys.path.insert(0, '../')
import city_udp

# Init global params

ROOT_FILENAME = 'saved_model'
LISTENING = True
RECEIVE_PORT = 9000
SEND_PORT = 9001

# Serializes a Keras model to a JSON and h5 data file
def serialize_model(model, root_filename=ROOT_FILENAME):

    # Convert to JSON
    model_in_json = model.to_json()

    # Write to file
    with open(root_filename + ".json", "w") as json_file:
        json_file.write(model_in_json)

    # Save weights
    model.save_weights(root_filename + ".h5")

    print("Successfully serialized model to local files {}.".format(root_filename))

# Deserialze data in .json and .h5 files into a Keras model that can be used for ML prediction
def deserialize_model(root_filename=ROOT_FILENAME):

    # Read JSON string
    json_file = open(root_filename + '.json', 'r')
    model_in_json = json_file.read()
    json_file.close()

    # Load model with architecture and weights
    model = model_from_json(model_in_json)
    model.load_weights(root_filename + '.h5')

    # Compile the model with loss, optimizer and metrics
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

    # Return the final model
    print("Successfully deserialized our model.")
    return model

# Load model and server
model = deserialize_model()
server = city_udp.City_UDP("Neural_Network_Model_Server", receive_port=RECEIVE_PORT, send_port=SEND_PORT)

# Constantly loop and wait
while LISTENING:

    # Breifly sleep
    time.sleep(0.1)

    # Constantly wait for new cities to be received via UDP
    # Taken directly from Alex's code for regression_server.py
    # Updated for neural network standards

    print("Waiting to receive city...")

    incoming_city = server.receive_city()
    print("City received!")

    # Extract feature matrix from this city
    features = traffic_regression.get_features(incoming_city)
    features = features.reshape((-1, 16, 16, 2))

    # Make traffic and wait prediction using CNN
    predicted_city = model.predict(features)[0]
    result_list = predicted_city.reshape(512).tolist()

    # Write prediction back to the cityiograph.City structure
    outgoing_city = incoming_city
    traffic_regression.output_to_city(outgoing_city, result_list)

    print("Updated city sent!")

    # Send the city back to Grasshopper script via UDP
    server.send_city(outgoing_city)