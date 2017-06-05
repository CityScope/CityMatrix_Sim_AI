'''
    File name: server_test.py
    Author: Kevin Lyons
    Date created: 4/11/2017
    Date last modified: 6/4/2017
    Python Version: 3.5
    Purpose: Quick script to test the functionality of our prediciton server. Make minor tweaks to cities \
     to test our code.
'''

# Global imports
import sys, time, random

# Custom imports
sys.path.insert(0, '../global/')
import utils, city_udp, logging
from cityiograph import City
log = logging.getLogger('__main__')

# Set parameters. Testing with same file path
FILENAME = '../../../data/cities/city_9000.json'

# Initialize server
server = city_udp.City_UDP("Neural_Network_Model_Server_Test", receive_port=9001, send_port=9000)

# Load some test file into a city
with open(FILENAME, 'r') as f:
	json_string = f.read()
city = City(json_string)
print("Successfully loaded city.")

# city.cells[(random.randint(0, 16), random.randint(0, 16))].data['traffic'] = random.randint(0, 1000)
city.densities[random.randint(0, 5)] = random.randint(0, 30)

# Send that city to our UDP server
server.send_city(city)
print("Sent city!!!")

# Wait to receive the response from the server
print("Waiting to receive data...")
data = server.receive_data()
print("Data response received!")

print("Process complete.")