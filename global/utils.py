'''
Filename: utils.py
Author: kalyons11 <mailto:kalyons@mit.edu>
Created: 2017-05-12 23:13:20
Last modified by: kalyons11
Description:
    - Simple utils script to be used alongside our server, among other files. Various
        tasks, including model serialization and math operations.
TODO:
    - None at this time.
'''

# General imports
import sys, json, os, time, pickle, traceback, logging, atexit, subprocess, threading, copy
import smtplib, base64, glob, random, numpy as np
from email.mime.text import MIMEText
from enum import Enum

# Custom imports
from config import *
from cityiograph import *

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

if first:
    log.info("Successfully initialized log file at {}.".format(LOGGER_FILENAME))

def handler(t, value, tb):
    """Helper method to log exceptions for the server and attempt to restart if needed.
    
    Args:
        t (type): exception type
        value (str): exception message
        tb (traceback): object showing us where the error came from
    """
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
    '''Restarts the CityMatrixServer after some fatal error. Notifies of any error message via e-mail.
    
    Args:
        message (str): string describing the error message
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
    '''Sends notification of server crash and reboot to users.
    
    Args:
        message (str): string describing the error message
        did_restart (bool): bool indiciating success of restart operation
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