'''
Filename: server_test.py
Author: kalyons11 <mailto:kalyons@mit.edu>
Created: 2017-04-11 23:06:29
Last modified by: kalyons11
Description:
    - Quick script to test the functionality of our prediciton server. Make minor tweaks to cities
     to test our code.
TODO:
    - None at this time.
'''

# Global imports
import sys, os, time, random, logging, glob, time, json, pprint, numpy as np, matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

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
# filename = '../../../data/cities/new_city.json'
# filename = '../../../data/cities/latest_city_format.json'
filename = '../MachineLearning/runs/65/predicted_cities/SolarSimCity_7000_output_predicted.json'
# filename = random.choice(glob.glob('../../../data/train_good/*.json'))
# d = '../CityPrediction/input_cities/'
# files = glob.glob(d + '*')
# filename = max(files, key = os.path.getctime) # Get the latest one
log.debug("Getting data from city at {}.".format(os.path.abspath(filename)))

# Initialize server, flip ports
server = city_udp.City_UDP("CityMatrixSimTestServer", receive_port = SEND_PORT, send_port = RECEIVE_PORT)

# Load some test file into a city
with open(filename, 'r') as f:
    json_string = f.read()
city = City(json_string)
log.debug("Successfully loaded city.")

traffic_matrix = city.get_data_matrix(key='traffic')
print(traffic_matrix.shape)
plt.imshow(traffic_matrix)
plt.show()
sys.exit(1)

# Make some changes for testing purposes
# x = np.random.randint(0, 16)
# y = np.random.randint(0, 16)
# t = np.random.randint(0, 6)
# print("change", x, y, t)
# city.change_cell(x, y, t)

# d_new = np.random.randint(0, 30)
# i = np.random.randint(0, 6)
# print(d_new, "@", i)
# city.densities[i] = d_new

# city.densities = [30, 30, 30, 1, 2, 30]

# city.AIWeights = np.random.dirichlet(np.ones(5), size = 1)[0].tolist()

# city.AIStep = 19

city.toggle1 = 0

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
for y in range(CITY_SIZE):
    for x in range(CITY_SIZE): # Reverse order for correct vis
        cell = city.get_cell((x, y))
        types.append(cell.type_id)
plt.figure()
plt.subplot(311)
plt.imshow(np.array(types).reshape(CITY_SIZE, CITY_SIZE), cmap = 'hot', interpolation = 'nearest')
# plt.show()

# Run any validation checks on the cities
ml = City(json.dumps(data['predict']))
ai = City(json.dumps(data['ai']))

print(ai.metrics, ai.score)

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

'''

# Get solar info and vis
solar_matrix = ml.get_data_matrix('solar')
plt.subplot(312)
plt.imshow(solar_matrix.T, cmap = 'hot', interpolation = 'nearest')

solar_matrix2 = ai.get_data_matrix('solar')
plt.subplot(313)
plt.imshow(solar_matrix2.T, cmap = 'hot', interpolation = 'nearest')
# plt.matshow(solar_matrix.T, cmap = 'hot', norm=LogNorm(vmin=300, vmax=5000))
plt.show()

log.debug("Process complete.")