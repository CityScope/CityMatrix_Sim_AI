class ObjectiveFunction(object):
    def __init__(self):
        self.metrics - []

    def add_metric(self, metric, weight):
        this.metrics.append((metric, weight))

    def get_function(self):
        return lambda (city): self.objective_function(self.metrics, city)  #TODO check if this copies self.metrics, or references it

    def objective_function(metrics, city):
        scores = []
        for m, w in metrics:
            scores.append(m(city) * w)
            total_weight += w
        return scores.sum() / total_weight

    def score(self, city):
        return self.objective_function(self.metrics, city)


class Metric(object):
    def __init__(self, f):
        pass

    def set_function(self, f):
        self.func = f

    def set_normalizer(self, n):
        self.norm = n


def feature_scale_normalizer(xMin, xMax):
    def normalizer(x):
        return (x - xMin) / (xMax - xMin)

    return normalizer


def z_scorer(xMean, xStdev):
    def z_score(x):
        return (x - xMean) / xStdev

    return z_score


if __name__ == "__main__":
    import os
    os.
