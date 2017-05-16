# Traffic Machine Learning
Machine learning methods for approximating the traffic simulation performed by CityGamatrix. Code should be runnable out of the box, with parameters changeable in the code.


# traffic_regression.py

## Running

Edit the variables `input_dir` and `output_dir` to point towards json files storing input and output cities for training.  Edit `prediction_dir` to point towards the directory where the regression models defined in `estimators` should save the predicted cities based on training, and input cities.

Then, run the script, preferably with an IDE.

Model predictions will be saved in directories named after the model under `prediction_dir`.
A log file with sklearn R^2 information will be saved, as well as a `models.pkl` file for portability.

## Dependencies
Tested with Python 2.7, though Python 3 should work without too much trouble.

Scikit-Learn  
Numpy

## Features and Results
The ML models are trained on pairs of vectors representing the input and expected output of a given city's traffic simulation. These vectors are names features and results respectively. They are generated with the following formats from json files produced by CityGamatrix. The default location of these files are in `./data/input` and `./data/output`. The files should be named such that they get ordered properly according to python's `os.listdir` function.

The features input into each model are a one-dimensional vector of the following format. These values come from json files produced by CityGamatrix.
`cell(i,j)` references the road, park, or building at location (i,j). X is the width of the city and Y is the length.
```
[
cell(0,0).population,
cell(0,0).isRoad,
cell(1,0).population,
cell(1,0).isRoad,
...
cell(X-1,Y-1).population,
cell(X-1,Y-1).isRoad
]
```
The results used to train (and eventually produced by) the models are a one-dimensional vector of the following format:
```
[
cell(0,0).traffic,
cell(0,0).wait_time,
cell(1,0).traffic,
cell(1,0).wait_time,
...
cell(X-1,Y-1).traffic,
cell(X-1,Y-1).wait_time
]
```

These vectors are produced by a given city using the function `get_[features|results]`.
Edit those functions (and `[cell/city]_[features/results]`) to alter the feature/result vectors used.
