import sys
import pickle
import time
import traffic_regression

sys.path.insert(0, 'TrafficTreeSim/')
import cityiograph

sys.path.insert(0, '../')
import city_udp

model = pickle.load(open('./linear_model.pkl', 'r+b'))
server = city_udp.City_UDP("Linear_Model_Server")

print("{} listening on ip: {} port: {}".format(server.name, server.receive_ip, 
                                               server.receive_port))
while(True):
    time.sleep(0.1)
    incoming_city = server.receive_city()
    print("City received")
    data = traffic_regression.get_features(incoming_city)
    results = model.predict([data])
    outgoing_city = incoming_city
    traffic_regression.output_to_city(outgoing_city, results[0])
    print("Updated city sent")
    server.send_city(outgoing_city)


