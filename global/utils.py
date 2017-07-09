"""
Simple utils script to be used alongside our server, among other files.
"""

import sys
import json
import os
import time
import pickle
import traceback
import logging
import subprocess
import smtplib
import base64
from email.mime.text import MIMEText

import config

# Set up logging functionality
log = logging.getLogger('__main__')

# First time log file initialized
# Taken from
# http://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-using-python
if not os.path.isfile(config.LOGGER_FILENAME):
    first = True
else:
    first = False

# Set up logger to file AND console
# Taken from multiple sources
# http://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
# https://docs.python.org/2/howto/logging.html
logFormatter = logging.Formatter(
    "%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s", '%m/%d/%Y %I:%M:%S %p')
log.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler(config.LOGGER_FILENAME)
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)

if first:
    log.info("Successfully initialized log file at {}.".format(config.LOGGER_FILENAME))


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
    if t != KeyboardInterrupt and filename == os.path.basename(config.SERVER_FILENAME):
        log.warning(config.SERVER_NAME + " has been stopped.")
        if config.AUTO_RESTART:
            log.warning("Attempting to reboot {}...".format(config.SERVER_NAME))
            time.sleep(5)  # Small delay
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
        subprocess.Popen([config.PYTHON_VERSION, config.SERVER_FILENAME, "FALSE"])
    except Exception:
        log.exception("Unable to restart " + config.SERVER_NAME + ".")
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
        if not config.DEBUG:  # Only do this in release mode for the server
            # Retreive data from credentials file
            cred = pickle.load(open(config.CREDENTIALS_FILENAME, 'rb'))
            username, password = tuple(base64.b64decode(
                cred[k]).decode() for k in ['u', 'p'])

            # Set up STMP connection
            server = smtplib.SMTP(config.SMTP_HOSTNAME, config.SMTP_PORT)
            server.ehlo()
            server.starttls()
            server.login(username, password)

            # Prepare e-mail message
            body = 'This is a notice that {} has been stopped. See below for stack trace information.\n\n{}\n\n'.format(
                config.SERVER_NAME, message)
            if did_restart:
                body += '{} was able to successfully restart.'.format(
                    config.SERVER_NAME)
            else:
                body += '{} could not restart at this time.'.format(
                    config.SERVER_NAME)

            msg = MIMEText(body)
            msg['Subject'] = '{} has been stopped.'.format(config.SERVER_NAME)
            msg['From'] = username
            msg['To'] = ", ".join(config.EMAIL_LIST)

            # Send message and log
            server.sendmail(username, config.EMAIL_LIST, msg.as_string())
            server.close()
            log.info("Successfully notified users via e-mail.")

    except Exception as e:
        log.exception(e)
        log.warning("Unable to notify users via e-mail.")


def write_dict(result_dict, timestamp):
    """Helper method to write our output prediction dictionary to JSON.

    Args:
        result_dict (dict): output from ML/AI work
        timestamp (str): -
    """
    # Get filename
    filename = os.path.join(config.PREDICTED_CITIES_DIRECTORY,
                            'city_predictions_' + timestamp + '.json')

    # Write dictionary
    with open(filename, 'w') as f:
        f.write(json.dumps(result_dict))
