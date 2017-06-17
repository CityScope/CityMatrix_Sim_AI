"""
unity_udp: a file that provides an object to send cities over UDP to 
CityMatrixAI Unity app.

Assumes packets sent to its endpoint are byte encodings of json strings of
cities in standard format

Sends cities as byte-encoded strings of the following json format:

Author: Alex Aubuchon, Ryan Zhang <ryanz@mit.edu>
"""

# Global imports
import socket, json, sys, logging

# Local imports
from utils import *
log = logging.getLogger('__main__')

# Default values
DEFAULT_SEND_IP = "127.0.0.1"
DEFAULT_SEND_PORT = 7002
DEFAULT_BUFFER_SIZE = 1024 * 128 * 4 #RZ 170605 1024 * 128 wasn't enough

class Unity_UDP(socket.socket):

    def __init__(self, name, send_ip=DEFAULT_SEND_IP, send_port=DEFAULT_SEND_PORT, \
                 buffer_size=DEFAULT_BUFFER_SIZE):
        self.name = name
        self.send_ip = send_ip
        self.send_port = send_port
        self.buffer_size = buffer_size
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        try:
            #RZ 170614 https://stackoverflow.com/questions/12362542/python-server-only-one-usage-of-each-socket-address-is-normally-permitted
            #self.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.bind((self.send_ip, self.send_port))
        except OSError as e:
            log.error(e); log.error("Attempting to close any open ports...")
            if SERVER_OS == 'MAC':
                # Run command to close the port
                # First, get the process ID (pid) where this port is running
                p = subprocess.Popen(['lsof', '-i :' + str(RECEIVE_PORT)], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                out, err = p.communicate()
                pid = out.decode("utf-8")
                # Close it
                x = subprocess.Popen(['kill', '-9', pid])
            #RZ 170614 doesn't work yet
            elif SERVER_OS == 'WIN':
                # Run command to close the port
                # get the process ID (pid) where this port is running and kill it
                # https://stackoverflow.com/questions/6204003/kill-a-process-by-looking-up-the-port-being-used-by-it-from-a-bat
                subprocess.call(['FOR', '/F \"tokens=4 delims= \" %P IN (\'netstat -a -n -o ^| findstr :7000\') DO taskKill.exe /PID %P /F']) # doesn't work yet

    def send_city(self, city):
        packet_dict = city.to_dict()
        """
        {
            "sender": self.name, # Deprecated <-
            "city": city.to_dict()
        }
        """
        json_message = json.dumps(packet_dict)
        self.sendto(json_message.encode(), (self.send_ip, self.send_port))

    def send_data(self, data):
        # data is a dictionary object we would like to send along
        json_message = json.dumps(data)
        self.sendto(json_message.encode(), (self.send_ip, self.send_port))