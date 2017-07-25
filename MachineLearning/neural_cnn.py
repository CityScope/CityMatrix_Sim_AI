"""
File to run our neural network on the data.
"""

import os
import sys
import pickle
from glob import glob

import keras.backend as K
import matplotlib.pyplot as plt
import numpy as np
import sacred
from dotmap import DotMap
from keras.callbacks import TensorBoard
from keras.layers import (BatchNormalization, Conv2D, Dense, Dropout, Flatten,
                          GlobalAveragePooling2D, Input, Reshape)
from keras.models import Model, load_model
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
    SS_res = K.sum(K.square(y_true - y_pred))
    SS_tot = K.sum(K.square(y_true - K.mean(y_true)))
    return (1 - SS_res / (SS_tot + K.epsilon()))


def configurations():
    config = DotMap()

    # Root configs
    config.root.dir_json = '../../../data/new_traffic_cities/*/*.json'
    config.root.pickle_fname = '../../../data/new_traffic_cities/data.pkl'
    config.root.description = ('No more dropout!!!')
    config.root.outcome = 'To be determined.'
    config.root.new_name = 'no_drop'
    config.root.model_fname = None  # 'runs/0.2_drop_less_epochs/final_model.hdf5'

    # Hyperparams
    config.hyper.lr = 1e-3
    config.hyper.optimizer = 'adam'
    config.hyper.dropout = 0.0
    config.hyper.lam = 1e-5
    config.hyper.loss = 'mean_squared_error'
    config.hyper.metrics = [coeff_determination]
    config.hyper.batch_size = 32
    config.hyper.nb_epochs = 300
    config.hyper.nb_filters = 4
    config.hyper.batch_norm = False
    config.hyper.num_dense_units = 512
    config.hyper.num_dense_layers = 1

    # Debug/util configs
    config.util.print_model = True
    config.util.num_val_samples = 6977
    config.util.force_data_reload = False

    return config


@ex.config
def sacred_configurations():
    print(">>> Loading configurations...")
    config = configurations()


@ex.capture
def data(config):
    print(">>> Loading data...")

    config = DotMap(config)

    # Try to get pickled data
    try:
        if config.util.force_data_reload:
            raise
        print(">>> Trying to load pickled train/val sets.")
        data = pickle.load(open(config.root.pickle_fname, 'rb'))
        print(">>> Success on pickle file.")
        return data
    except Exception:
        print(">>> Loading cities for the first time.")
        train_X, train_Y, train_filename_list = [], [], []
        val_X, val_Y, val_filename_list = [], [], []

        for i, path in tqdm(enumerate(glob(config.root.dir_json))):
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
                if i < config.util.num_val_samples:
                    # Add to train set
                    train_X.append(inp)
                    train_Y.append(out)
                    train_filename_list.append(path)
                else:
                    # Add to val set
                    val_X.append(inp)
                    val_Y.append(out)
                    val_filename_list.append(path)

        # Reshape final arrays
        train_X = np.array(train_X)
        train_Y = np.array(train_Y)
        val_X = np.array(val_X)
        val_Y = np.array(val_Y)

        # Create dict
        output = {
            'train_X': train_X,
            'train_Y': train_Y,
            'val_X': val_X,
            'val_Y': val_Y,
            'train_filename_list': train_filename_list,
            'val_filename_list': val_filename_list
        }

        # Write to pickle
        pickle.dump(output, open(config.root.pickle_fname, 'wb'))

        return output


@ex.capture
def model(config):
    print(">>> Loading model...")

    config = DotMap(config)

    if config.root.model_fname is not None:
        print("Found model from previous run.")
        m = load_model(config.root.model_fname,
                       custom_objects={'coeff_determination': coeff_determination})
        return m

    print("Need to create this model from scratch.")

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
    # dense_layer = GlobalAveragePooling2D()(x)

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
    # Save this source code to the local experiment directory for later use
    print(">>> Saving source code locally...")
    with open(__file__, 'r') as source_file_input:
        source_text = source_file_input.read()

    source_name = os.path.join(ex.observers[0].dir, 'SOURCE_' + __file__)

    with open(source_name, 'w') as source_file_output:
        source_file_output.write(source_text)

    # Get config
    config = DotMap(config)

    # Get data
    data_dict = DotMap(data())

    # Get model
    m = model()

    if config.root.model_fname is None:
        # Only train if this is not a pre-loaded model run
        m.compile(optimizer=config.hyper.optimizer,
                  loss=config.hyper.loss,
                  metrics=config.hyper.metrics)

        # Init callbacks
        callbacks = [
            TQDMCallback(),
            TensorBoard(log_dir=ex.observers[0].dir,
                        histogram_freq=1,
                        write_graph=True,
                        write_images=False)
        ]

        # Train
        print(">>> Training...")
        m.fit(x=data_dict.train_X,
              y=data_dict.train_Y,
              batch_size=config.hyper.batch_size,
              epochs=config.hyper.nb_epochs,
              verbose=2,
              callbacks=callbacks,
              validation_data=(data_dict.val_X, data_dict.val_Y))

        m.save(os.path.join(ex.observers[0].dir, 'final_model.hdf5'))

        # Test
        print(">>> Evaluating...")
        result = m.evaluate(x=data_dict.val_X,
                            y=data_dict.val_Y,
                            batch_size=config.hyper.batch_size,
                            verbose=1,
                            sample_weight=None)

        # Write result to file for later use - loss and R^2
        with open(os.path.join(ex.observers[0].dir, 'test_metrics.txt'), 'w') as f:
            f.writelines([str(result), "loss, R^2"])

    print(">>> Predicting cities...")
    # 1. Make output dir
    output_dir = os.path.join(ex.observers[0].dir, 'predicted_cities')
    os.mkdir(output_dir)
    # 2. Iterate
    for x, fname in tqdm(list(zip(data_dict.val_X, data_dict.val_filename_list))):
        try:
            # Reshape x
            x = np.expand_dims(x, axis=0)

            # Load city
            with open(fname, 'r') as city_file_object:
                city = cityiograph.City(city_file_object.read())

            # Make prediction
            pred = m.predict(x)

            # Reshape
            pred = pred.squeeze().flatten().tolist()

            # Add features
            city.update_values(pred, mode='traffic')

            # Write to new file
            fname_base = os.path.splitext(os.path.basename(fname))[0]
            fname_output = os.path.join(output_dir, fname_base + '_predicted.json')
            with open(fname_output, 'w') as city_file_object_output:
                city_file_object_output.write(city.to_json())

        except Exception:
            # Error parsing city or something else went wrong
            print("Missed city {}.".format(fname))
            pass

    print("Process complete!!!")
