import traffic_regression

sys.path.insert(0, 'TrafficTreeSim/')
import cityiograph

sys.path.insert(0, '../')
import city_udp

model = pickle.load('./regression_model.pkl')
server = city_udp.City_UDP()

while(True):
    incoming_city = server.receive_city()
    print("City received")
    data = get_features(incoming_city)
    results = model.predict(data)
    outgoing_city = incoming_city
    traffic_regression.output_to_city(outgoing_city, results[0])
    print("Updated city sent")
    server.send_city(outgoing_city)


