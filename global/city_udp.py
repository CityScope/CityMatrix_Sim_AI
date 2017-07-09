"""
city_udp: a file that provides an object to handle the transmitting and
receiving of cities over UDP.

Assumes packets sent to its endpoint are byte encodings of json strings of
cities in standard format.

Sends cities as byte-encoded strings.

Author: Alex Aubuchon, Kevin Lyons
"""

import socket
import json
import logging

from cityiograph import City

log = logging.getLogger('__main__')

# Default values
DEFAULT_SEND_IP = "127.0.0.1"
DEFAULT_SEND_PORT = 7985
DEFAULT_RECEIVE_IP = "127.0.0.1"
DEFAULT_RECEIVE_PORT = 7986
DEFAULT_BUFFER_SIZE = 1024 * 128 * 64

''' --- CLASS DEFINITIONS --- '''


class City_UDP(socket.socket):
    """Our general, abstracted city UDP server class.

    Attributes:
        buffer_size (int): -
        name (string): descriptor
        receive_ip (str): -
        receive_port (str): -
        send_ip (str): -
        send_port (str): -
    """

    def __init__(self, name, send_ip=DEFAULT_SEND_IP, send_port=DEFAULT_SEND_PORT,
                 receive_ip=DEFAULT_RECEIVE_IP,
                 receive_port=DEFAULT_RECEIVE_PORT,
                 buffer_size=DEFAULT_BUFFER_SIZE):
        self.name = name
        self.send_ip = send_ip
        self.send_port = send_port
        self.receive_ip = receive_ip
        self.receive_port = receive_port
        self.buffer_size = buffer_size
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        self.bind((self.receive_ip, self.receive_port))

    def send_city(self, city):
        """Send a city to another client as JSON.

        Args:
            city (cityiograph.City): -
        """
        packet_dict = city.to_dict()
        json_message = json.dumps(packet_dict)
        self.sendto(json_message.encode(), (self.send_ip, self.send_port))

    def send_data(self, data):
        """Send a generic data dictionary to another client as JSON.

        Args:
            data (dict): some data mapping
        """
        json_message = json.dumps(data)
        self.sendto(json_message.encode(), (self.send_ip, self.send_port))

    def receive_city(self):
        """Receive city object from a client.

        Returns:
            cityiograph.City: result city object
        """
        try:
            data, addr = self.recvfrom(self.buffer_size)
        except Exception as e:
            if type(e) == KeyboardInterrupt:
                pass  # Handle manual server stop case
            else:
                log.exception("Error receiving data from socket.")
                return None
        else:
            json_string = data.decode("utf-8")
            try:
                return City(json_string)
            except Exception:
                log.exception("Invalid city JSON received.")
                return None

    def receive_data(self):
        """Receive a generic data dictionary from another client as JSON.

        Returns:
            dict: some data mapping
        """
        data, addr = self.recvfrom(self.buffer_size)
        json_string = data.decode("utf-8")
        try:
            return json.loads(json_string)
        except Exception:
            log.exception("Invalid JSON object received.")
            return None
