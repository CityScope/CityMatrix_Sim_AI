"""
city_udp: a file that provides an object to handle the transmitting and
receiving of cities over UDP.

Assumes packets sent to its endpoint are byte encodings of json strings of
cities in standard format

Sends cities as byte-encoded strings of the following json format:
{
"sender": City_UDP.name
"city": CITY_JSON
}

Author: Alex Aubuchon
"""

import socket, json, sys

import cityiograph

DEFAULT_SEND_IP = "127.0.0.1"
DEFAULT_SEND_PORT = 7985
DEFAULT_RECEIVE_IP = "127.0.0.1"
DEFAULT_RECEIVE_PORT = 7986
DEFAULT_BUFFER_SIZE = 1024 * 128

class City_UDP(socket.socket):

    def __init__(self, name, send_ip=DEFAULT_SEND_IP, send_port=DEFAULT_SEND_PORT, \
                 receive_ip=DEFAULT_RECEIVE_IP, \
                 receive_port=DEFAULT_RECEIVE_PORT, \
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
        packet_dict = city.to_dict()
        """
        {
            "sender": self.name,
            "city": city.to_dict()
        }
        """
        json_message = json.dumps(packet_dict)
        self.sendto(json_message.encode(), (self.send_ip, self.send_port))

    def receive_city(self):
        data, addr = self.recvfrom(self.buffer_size)
        json_string = data.decode("utf-8")
        #RZ
        try:
            return cityiograph.City(json_string)
        except:
            print('error when loading json_string to json_obj')
            return None