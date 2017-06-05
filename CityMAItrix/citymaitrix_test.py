import sys
sys.path.insert(0, "../global/")
from cityiograph import City
from strategies import random_single_moves as Strategy
log = logging.getLogger('__main__')

f = open("./city_0_output_solar.json", 'r')
log.debug(Strategy.search(City(f.read())))