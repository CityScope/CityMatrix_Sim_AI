"""
File to run our neural network on the data.
"""

import os
import sys
from glob import glob

import keras.backend as K
import matplotlib.pyplot as plt
import numpy as np
import sacred
from dotmap import DotMap
from keras.callbacks import TensorBoard
from keras.layers import (BatchNormalization, Conv2D, Dense, Dropout, Flatten,
                          Input, Reshape)
from keras.models import Model
from keras.regularizers import l1
from keras_tqdm import TQDMCallback
from sacred.observers import FileStorageObserver
from tqdm import tqdm

sys.path.append('../global/')
import cityiograph

# Define experiment
ex = sacred.Experiment()

# Add observers
ex.observers.append(FileStorageObserver.create('runs'))


# http://jmbeaujour.com/ml/2017/03/20/CoeffDetermination_CustomMetric4Keras/
def coeff_determination(y_true, y_pred):
    SS_res =  K.sum(K.square( y_true-y_pred )) 
    SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) ) 
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )


def configurations():
    config = DotMap()

    # Data configs
    config.dir = '../../../data/new_traffic_cities/*/*.json'

    # Hyperparams
    config.hyper.lr = 1e-3
    config.hyper.optimizer = 'adam'
    config.hyper.dropout = 0.3
    config.hyper.lam = 1e-5
    config.hyper.loss = 'mean_squared_error'
    config.hyper.metrics = [coeff_determination]
    config.hyper.batch_size = 32
    config.hyper.nb_epochs = 500
    config.hyper.nb_filters = 4
    config.hyper.batch_norm = False
    config.hyper.num_dense_units = 512
    config.hyper.num_dense_layers = 1

    # Debug/util configs
    config.util.print_model = True
    config.util.val_split = 0.15

    return config


@ex.config
def sacred_configurations():
    config = configurations()


@ex.capture
def data(config):
    print(">>> Loading data...")

    config = DotMap(config)

    X, Y = [], []

    for path in tqdm(np.random.permutation(glob(config.dir))):
        with open(path, 'r') as f:
            # Extract
            city = cityiograph.City(f.read())
            inp = cityiograph.get_features(city, mode='traffic')
            out = cityiograph.get_results(city, mode='traffic')
            # Reshape
            inp = inp.reshape(16, 16, 2)
            out = out.reshape(16, 16, 2)
            # Noramlize
            inp = (inp - inp.mean()) / inp.std()
            out = (out - out.mean()) / out.std()
            # Load
            X.append(inp)
            Y.append(out)

    X = np.array(X)
    Y = np.array(Y)

    return X, Y


@ex.capture
def model(config):
    print(">>> Loading model...")

    config = DotMap(config)

    inp = Input(shape=(16, 16, 2),
                name='input')

    x = Conv2D(filters=config.hyper.nb_filters,
               kernel_size=(3, 3),
               activation='relu')(inp)
    if config.hyper.batch_norm:
        x = BatchNormalization()(x)

    x = Conv2D(filters=config.hyper.nb_filters * 2,
               kernel_size=(3, 3),
               activation='relu')(x)
    if config.hyper.batch_norm:
        x = BatchNormalization()(x)

    x = Conv2D(filters=config.hyper.nb_filters * 3,
               kernel_size=(3, 3),
               activation='relu')(x)
    if config.hyper.batch_norm:
        x = BatchNormalization()(x)

    dense_layer = Flatten()(x)

    for _ in range(config.hyper.num_dense_layers):
        dense_layer = Dense(units=config.hyper.num_dense_units,
                            kernel_regularizer=l1(config.hyper.lam))(dense_layer)
        dense_layer = Dropout(config.hyper.dropout)(dense_layer)
        if config.hyper.batch_norm:
            dense_layer = BatchNormalization()(dense_layer)

    out = Reshape(target_shape=(16, 16, 2))(dense_layer)

    m = Model(inputs=inp, outputs=out)

    if config.util.print_model:
        print(m.summary())

    return m


@ex.automain
def run(config):
    config = DotMap(config)

    X, Y = data()

    m = model()
    m.compile(optimizer=config.hyper.optimizer,
              loss=config.hyper.loss,
              metrics=config.hyper.metrics)

    callbacks = [
        TQDMCallback(),
        TensorBoard(log_dir=ex.observers[0].dir,
                    histogram_freq=0,
                    write_graph=True,
                    write_images=True)
    ]

    m.fit(x=X,
          y=Y,
          batch_size=config.hyper.batch_size,
          epochs=config.hyper.nb_epochs,
          verbose=2,
          callbacks=callbacks,
          validation_split=config.util.val_split)

    m.save(os.path.join(ex.observers[0].dir, 'final_model.hdf5'))

    print("Process complete!!!")
