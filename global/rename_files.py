# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 00:07:29 2017

@author: Alex
"""

import os
import numpy as np

file_dir = "./data/output/" # No longer a correct path - Kevin, 05/26/2017

zfill_val = int(np.ceil(np.log10(len(os.listdir(file_dir)))))

for filename in os.listdir(file_dir):
    number = filename.split("_")[1].split(".")[0]
    new_filename = "city_" + number.zfill(zfill_val) + ".json"
    os.rename(file_dir + filename, file_dir + new_filename)
    