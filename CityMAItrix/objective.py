from metrics import citymatrix_stats as Metrics


class ObjectiveFunction(object):
    def __init__(self):
        self.metrics = []

    def evaluate(self, city):
        outputs = [weight * fun(city) for name, fun, weight in self.metrics]
        return [sum(outputs), outputs]

    def get_metrics(self, city):
        self.update_weights(city.AIWeights)
        return [(name, fun(city), weight) for name, fun, weight in self.metrics]

    def add_metric(self, name, metric, weight):
        self.metrics.append((name, metric, weight))

    # RZ 170615 update AIWeights before search
    def update_weights(self, weights):
        for i in range(5):
            self.metrics[i] = self.metrics[i][:2] + (weights[i],)
        # print("updated self.metrics: {}".format(self.metrics))


objective = ObjectiveFunction()
objective.add_metric("Density",
                     Metrics.pop_density_perf, 0.2)
objective.add_metric("Diversity",
                     Metrics.pop_diversity_perf, 0.2)
objective.add_metric("Energy",
                     Metrics.energy_perf, 0.2)
objective.add_metric("Traffic",
                     Metrics.traffic_perf, 0.2)
objective.add_metric("Solar",
                     Metrics.solar_perf, 0.2)
