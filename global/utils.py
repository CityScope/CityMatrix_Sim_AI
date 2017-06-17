'''
	File name: utils.py
	Author(s): Kevin Lyons, Alex Aubuchon
	Date created: 5/12/2017
	Date last modified: 6/15/2017
	Python Version: 3.5
	Purpose: Simple utils script to be used alongside our server, among other files. Various
		tasks, including model serialization and math operations.
	TODO:
		- Clean up!!!
'''

# General imports
import sys, json, os, time, pickle, traceback, logging, atexit, subprocess, threading, copy
import smtplib, base64, glob, random, numpy as np
from email.mime.text import MIMEText
from enum import Enum

# Custom imports
from cityiograph import *
from config import *

# Set up logging functionality
log = logging.getLogger('__main__')

# First time log file initialized
# Taken from http://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-using-python
if not os.path.isfile(LOGGER_FILENAME):
	first = True
else:
	first = False

# Set up logger to file AND console
# Taken from multiple sources
# http://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
# https://docs.python.org/2/howto/logging.html
logFormatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s", '%m/%d/%Y %I:%M:%S %p')
log.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(LOGGER_FILENAME)
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)

if first: log.info("Successfully initialized log file at {}.".format(LOGGER_FILENAME))

# Configure log to handle all uncaught exceptions and reboot server, if needed
# Taken from http://stackoverflow.com/questions/8050775/using-pythons-logging-module-to-log-all-exceptions-and-errors
# Also from http://stackoverflow.com/questions/4564559/get-exception-description-and-stack-trace-which-caused-an-exception-all-as-a-st
def handler(t, value, tb):
	# Log exception
	message = str(value) + "\n" + "\n".join(traceback.format_tb(tb))
	log.exception(message)

	# Determine the source and act accordingly
	filename = traceback.extract_tb(tb)[0].filename
	if t != KeyboardInterrupt and filename == os.path.basename(SERVER_FILENAME):
		log.warning(SERVER_NAME + " has been stopped.")
		if AUTO_RESTART:
			log.warning("Attempting to reboot {}...".format(SERVER_NAME))
			time.sleep(5) # Small delay
			restart(message)
		else:
			notify(message, False)

# Set default hook for system
sys.excepthook = handler

def restart(message):
	'''
	Restarts the CityMatrixServer after some fatal error. Notifies of any error message via e-mail.
	Input: 	message - string describing the error message
	Output:	None - restart server and send e-mail accordingly
	'''

	did_restart = False
	try:
		subprocess.Popen([PYTHON_VERSION, SERVER_FILENAME, "FALSE"])
	except:
		log.exception("Unable to restart " + SERVER_NAME + ".")
	else:
		did_restart = True
	finally:
		notify(message, did_restart)

def notify(message, did_restart):
	'''
	Sends notification of server crash and reboot to users.
	Input:	message - string describing the error message
			did_restart - bool indiciating success of restart operation
	Output:	None - send e-mail to users
	'''

	try:
		if not DEBUG: # Only do this in release mode for the server
			# Retreive data from credentials file
			cred = pickle.load(open(CREDENTIALS_FILENAME, 'rb'))
			username, password = tuple(base64.b64decode(cred[k]).decode() for k in ['u', 'p'])
			
			# Set up STMP connection
			server = smtplib.SMTP(SMTP_HOSTNAME, SMTP_PORT)
			server.ehlo()
			server.starttls()
			server.login(username, password)

			# Prepare e-mail message
			body = 'This is a notice that {} has been stopped. See below for stack trace information.\n\n{}\n\n'.format(SERVER_NAME, message)
			if did_restart:
				body += '{} was able to successfully restart.'.format(SERVER_NAME)
			else:
				body += '{} could not restart at this time.'.format(SERVER_NAME)

			msg = MIMEText(body)
			msg['Subject'] = '{} has been stopped.'.format(SERVER_NAME)
			msg['From'] = username
			msg['To'] = ", ".join(EMAIL_LIST)

			# Send message and log
			server.sendmail(username, EMAIL_LIST, msg.as_string())
			server.close()
			log.info("Successfully notified users via e-mail.")

	except Exception as e:
		log.exception(e)
		log.warning("Unable to notify users via e-mail.")

class CityChange(Enum):
	'''
	Custom enum to describe the difference between two cities.
	'''
	NO = -1, # Exact same cities
	FIRST = 0, # First city in our directory
	DENSITY = 1, # Some change in the density array
	CELL = 2 # Some change in a road/building cell on the grid

def diff_cities(current_city, prev_city = None):
	'''
	Determine if a new city is different from the existing one in memory, and if so, how?
	Input: 	current_city - instance of cityiograph.City object - incoming city to server
			prev_city - instance of cityiograph.City object - may be given if we are doing direct comparison
	Output:	Return the difference between current city and previouly saved one
			key - CityChange instance
			data - list of [ [ changes ] , previous_predicted_city or BOOL indicator ]
	'''

	if prev_city is None:
		# First, get the most recent city from our saved set
		# Taken from http://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python
		files = glob.glob(INPUT_CITIES_DIRECTORY + '*')

		# If this is the first city, return need for prediction
		if len(files) == 0:
			return ( CityChange.FIRST , True )

		# Run comparison on this city and most recent one
		with open(max(files, key = os.path.getctime), 'r') as f:
			# Load prev_city from JSON
			prev_city = City(f.read())

		# Also, get the previous PREDICTED city from our directory
		predicted_files = glob.glob(PREDICTED_CITIES_DIRECTORY + '*')
		with open(max(predicted_files, key = os.path.getctime)) as g: # Get the most recent one by created time
			# Load dict
			json_dict = json.load(g)

			# Get predicted city object
			prev_predicted_city = City(json.dumps(json_dict['predict']))
	else:
		prev_predicted_city = prev_city.copy() # Update our prev var
		
	# Now, compare directly for densities, size and cells
	if prev_city.equals(current_city):
		return ( CityChange.NO , False ) # No difference
	else:
		# Yes, we have a difference, let's explore
		result = []
		if prev_city.densities != current_city.densities: # Density changes - note indices
			for i, d in enumerate(prev_city.densities):
				if current_city.densities[i] != d:
					result.append(i)
			return ( CityChange.DENSITY , [ result, prev_predicted_city ] )
		else:
			# We likely have some cell mismatch(es) - need to find
			# Return locations (x, y)
			for x in range(prev_city.width):
				for y in range(prev_city.height):
					old = prev_city.cells.get((x, y))
					new = current_city.cells.get((x, y))
					if not old.equals(new):
						result.append( (x, y) )
			return ( CityChange.CELL , [ result, prev_predicted_city ] )