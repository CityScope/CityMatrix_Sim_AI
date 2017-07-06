'''
Filename: misc.py
Author: kalyons11 <mailto:kalyons@mit.edu>
Created: 2017-06-15 20:09:56
Last modified by: kalyons11
Description:
    - Misc methods/definitions that have been cleaned as a result of reformatting.
TODO:
    - None at this time.
'''

''' --- /globals/cityiograph.py ---'''

def nesw(self, pos):
    x = pos[0]
    y = pos[1]
    directions = []
    if x > 0:
        directions.append((x - 1, y))
    if x < self.width - 1:
        directions.append((x + 1, y))
    if y > 0:
        directions.append((x, y - 1))
    if y < self.height - 1:
        directions.append((x, y + 1))
    return directions

def get_graph(self):
    graph = {}
    for cell in self.cells.values():
        edges = {}
        for n in self.nesw(cell.get_pos()):
            edges[n] = EDGE_COST
        graph[cell.get_pos()] = edges
    return graph

def get_road_nearby_population_map(self):
    pop_map = {}
    for pos, cell in self.cells.items():
        if cell.type_id == ROAD_ID:
            pop_map[pos] = 0
            for n in [self.cells[p] for p in self.nesw(pos)]:
                if n.type_id != ROAD_ID:
                    pop_map[pos] += n.population
    return pop_map

def get_road_graph(self):
    road_graph = {}
    for (pos, edges) in self.get_graph().items():
        if self.cells[pos].type_id == ROAD_ID:
            new_edges = {}
            for (other_pos, cost) in edges.items():
                if self.cells[other_pos].type_id == ROAD_ID:
                    new_edges[other_pos] = cost
            road_graph[pos] = new_edges
    return road_graph

def plot_city(city):

    plotWidget = pg.plot()
    building_points = []
    road_points = []
    for c in city.cells.values():
        if c.type_id == ROAD_ID:
            road_points.append(c.get_pos())
        else:
            building_points.append(c.get_pos())

    plotWidget.plot(
        [t[0] for t in road_points], [t[1] for t in road_points],
        pen=None,
        symbol='+')
    plotWidget.plot(
        [t[0] for t in building_points], [t[1] for t in building_points],
        pen=None,
        symbol='s')

def traffic_plot(city):
    data = np.zeros([city.width, city.height])
    for c in city.cells.values():
        data[c.x][-c.y] = c.data["traffic"]
    pg.image(data)

def update_dict(d, u):
    """
    http://stackoverflow.com/questions/3232943
    /update-value-of-a-nested-dictionary-of-varying-depth
    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

''' --- /globals/utils.py --- '''

def serialize_model(model, root_filename):
    '''
    Serializes a Keras model to a JSON and h5 data file
    Input:  model - instance of Keras model to be serialized
    root_filename - string representing root of JSON and h5 data file for model
    Output: None - simply write the model to the files
    '''

    # Convert to JSON
    model_in_json = model.to_json()

    # Write to file
    with open(root_filename + ".json", "w") as json_file:
        json_file.write(model_in_json)

    # Save weights
    model.save_weights(root_filename + ".h5")

def deserialize_model(root_filename):
    '''
    Deserialze data in .json and .h5 files into a Keras model that can be used for ML prediction
    Input:  root_filename - string representing root of JSON and h5 data file for model
    Output: model - instance of Keras model taken from data
    '''

    # Read JSON string
    with open(root_filename + '.json', 'r') as f:
        model_in_json = f.read()

    # Load model with architecture and weights
    model = model_from_json(model_in_json)
    model.load_weights(root_filename + '.h5')

    # Compile the model with loss, optimizer and metrics and return
    model.compile(loss = LOSS_FUNCTION, optimizer = OPTIMIZER, metrics = KERAS_METRICS)
    return model

def compute_accuracy(true, pred):
    '''
    Compute percent accuracy between 2 input matrices (true and predicted values)
    Input:  a, b - np array n x ( )
    Output: accuracy - scalar that represents (1 - percent error) between a and b, in range [0, 1]
    '''

    # Simple solution taken from http://stackoverflow.com/questions/20402109/calculating-percentage-error-by-comparing-two-arrays
    return 1 - np.mean(true != pred)