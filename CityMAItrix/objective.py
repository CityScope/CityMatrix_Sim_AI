class ObjectiveFunction(object):
    def __init__(self):
        self.metrics = []

    def predict(self, city):
        outputs = [weight * fun(city) for name, fun, weight in self.metrics]
        return sum(outputs)

    def get_metrics(self, city):
        return [(name, fun(city), weight) for name, fun, weight in self.metrics]

    def add_metric(self, name, metric, weight):
        self.metrics.append((name, metric, weight))

from metrics import citymatrix_stats as Metrics

objective = ObjectiveFunction()
objective.add_metric("Population Density Performance",
                     Metrics.pop_density_perf, 1)
objective.add_metric("Population Diversity Performance",
                     Metrics.pop_diversity_perf, 1)
objective.add_metric("Energy & Cost Performance",
                     Metrics.energy_perf, 1)
objective.add_metric("Traffic Performance",
                     Metrics.traffic_perf, 1)
objective.add_metric("Solar Access Performace",
                     Metrics.solar_perf, 1)
