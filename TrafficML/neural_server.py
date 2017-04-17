import sys, time, traffic_regression

from keras.models import model_from_json

sys.path.insert(0, '../TrafficTreeSim/')
import cityiograph

sys.path.insert(0, '../')
import city_udp

ROOT_FILENAME = 'saved_model'
LISTENING = False

def serialize_model(model, root_filename=ROOT_FILENAME):

	# Convert to JSON
	model_in_json = model.to_json()

	# Write to file
	with open(root_filename + ".json", "w") as json_file:
		json_file.write(model_in_json)

    # Save weights
	model.save_weights(root_filename + ".h5")

	print("Successfully serialized model to local files {}.".format(root_filename))

def deserialize_model(root_filename=ROOT_FILENAME):

	# Read JSON string 
	json_file = open(root_filename + '.json', 'r')
	model_in_json = json_file.read()
	json_file.close()

	# Load model with architecture and weights
	model = model_from_json(model_in_json)
	model.load_weights(root_filename + '.h5')

	# Return the final model
	print("Successfully deserialized our model.")
	return model

# model = deserialize_model()
server = city_udp.City_UDP("Neural_Network_Model_Server")

while LISTENING:

	# Breifly sleep
	time.sleep(0.1)

	# Constantly wait for new cities to be received via UDP
	# Taken directly from Alex's code for regression_server.py
	# Updated for neural network standards

	incoming_city = server.receive_city()
	print("City received!")
	data = traffic_regression.get_features(incoming_city)
	print(data)
    # Prediction should look like this
    # predicted_first_city = model.predict(train_x[index].reshape(-1, 16, 16, 2))[0]
	results = model.predict(data)
	outgoing_city = incoming_city
    # results 0 should be list of length 512...
	traffic_regression.output_to_city(outgoing_city, results[0])
	print("Updated city sent!")

	# Send the city back to Grasshopper script via UDP
	server.send_city(outgoing_city)

# WHERE I AM RIGHT NOW

# Model is completely trained with 84 % accuracy, saved in saved_model files
# Now, just need to test this new UDP framework back and forth on localhost
# Alex said to run 2 processes at once
# Still need to have some sort of update() function that fits the model on some new set of data points