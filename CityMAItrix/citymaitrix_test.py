import sys
sys.path.insert(0, "../global/")
from cityiograph import *

from strategies import random_single_moves as Strategy

f = open("./city_0_output_solar.json", 'r')
print(Strategy.search(City(f.read())))
