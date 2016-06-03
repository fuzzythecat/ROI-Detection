import sys
sys.path.append("../modules/")

import numpy as np
import img2mask as i2m
from utils import conf

if __name__ == "__main__":

    filename = conf.dir_data_temp + "slice.npy"
    img = np.load(filename)

    filename = conf.dir_data_temp + "mask.npy"
    mask = np.load(filename)

    filename = conf.dir_data_temp + "position.npy"
    position = np.load(filename)

    ret = i2m.img2mask(img, mask=mask, position=position)

