'''
    File name: server_test.py
    Author: Kevin Lyons
    Date created: 4/11/2017
    Date last modified: 6/12/2017
    Python Version: 3.5
    Purpose: Quick script to test the functionality of our prediciton server. Make minor tweaks to cities
     to test our code.
    TODO:
    	- Make this file representative of Ryan's tests.
'''

# Global imports
import sys, os, time, random, logging, glob, time, json, pprint, numpy as np, matplotlib.pyplot as plt

# Custom imports
sys.path.insert(0, '../global/')
import utils, city_udp
from config import SEND_PORT, RECEIVE_PORT, CITY_SIZE
from cityiograph import City
log = logging.getLogger('__main__')

# Set parameters. Testing with same file path
# filename = 'C:/RH_GH/_verification/170510_ML_Validation_003/02_kevin_prediction_linear_normalized/city_8000_output_normalized.json'
# filename = '../../../data/cities/cityIO.json'
# filename = '../../../data/cities/city_9000.json'
# filename = random.choice(glob.glob('../../../data/train_good/*.json'))
d = '../CityPrediction/input_cities/'
files = glob.glob(d + '*')
filename = max(files, key = os.path.getctime) # Get the latest one
log.debug("Getting data from city at {}.".format(os.path.abspath(filename)))

# Initialize server, flip ports
server = city_udp.City_UDP("CityMatrixSimTestServer", receive_port = SEND_PORT, send_port = RECEIVE_PORT)

# Load some test file into a city
with open(filename, 'r') as f:
	json_string = f.read()
city = City(json_string)
log.debug("Successfully loaded city.")

# city.cells[(random.randint(0, 16), random.randint(0, 16))].data['traffic'] = random.randint(0, 1000)
city.densities[random.randint(0, 5)] = random.randint(0, 30)
# city.densities = [30, 30, 30, 1, 2, 30]

# Send that city to our UDP server
server.send_city(city)
log.debug("Sent city!!!")

start = time.time()

# Wait to receive the response from the server
log.debug("Waiting to receive data...")
data = server.receive_data()
# log.debug(data)
log.debug("Data response received! Took a total of {} seconds.".format(time.time() - start))

# Vis our first city
types = []
for x in range(CITY_SIZE):
	for y in range(CITY_SIZE):
		cell = city.get_cell((x, y))
		types.append(cell.type_id)
plt.figure()
plt.subplot(211)
plt.imshow(np.array(types).reshape(CITY_SIZE, CITY_SIZE), cmap = 'hot', interpolation = 'nearest')
# plt.show()

# Run any validation checks on the cities
ml = City(data['predict'], dict_mode = True)
ai = City(data['ai'], dict_mode = True)

'''

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(ml.to_dict())

one, two = [], []
for x in range(CITY_SIZE):
	for y in range(CITY_SIZE):
		a = ml.get_cell((x, y))
		b = ai.get_cell((x, y))
		one.append(a.data['traffic'])
		two.append(b.data['traffic'])

one = np.array(one).reshape(CITY_SIZE, CITY_SIZE)
two = np.array(two).reshape(CITY_SIZE, CITY_SIZE)

log.debug(one)
log.debug(two)

# Get solar info and vis
solar = []
for x in range(CITY_SIZE):
	for y in range(CITY_SIZE):
		cell = p.get_cell((x, y))
		solar.append(cell.data['solar'])
plt.subplot(212)
plt.imshow(np.array(solar).reshape(CITY_SIZE, CITY_SIZE), cmap = 'hot', interpolation = 'nearest')
plt.show()
'''

log.debug("Process complete.")