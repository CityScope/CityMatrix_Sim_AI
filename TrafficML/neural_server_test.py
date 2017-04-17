import sys, time

sys.path.insert(0, '../TrafficTreeSim/')
import cityiograph

sys.path.insert(0, '../')
import city_udp

# Set parameters. Testing with same file path

FILENAME = '../../../data/cities/city_9000.json'

# Initialize server

server = city_udp.City_UDP("Neural_Network_Model_Server_Test", receive_port=9001, send_port=9000)

# Load some test file into a city

with open(FILENAME, 'r') as f: json_string = f.read()

city = cityiograph.City(json_string)

print("Successfully loaded city.")

# Send that city to our UDP server

server.send_city(city)

print("Sent city!!!")

while True:

	print("Waiting to receive city...")

	# Breifly sleep
	time.sleep(0.1)

	# Constantly wait for new cities to be received via UDP
	# Taken directly from Alex's code for regression_server.py
	# Updated for neural network standards

	incoming_city = server.receive_city()
	print("City received!")

	print(incoming_city.to_dict())

print("Process complete.")