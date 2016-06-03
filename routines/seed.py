import sys
sys.path.append("../modules/")
import numpy as np

import img2mask as i2m
from utils import file_handler as fh
from utils import conf

if __name__ == "__main__":

    zslice = conf.default_z
    tslice = conf.default_t

    path = fh.get_file_path()

    data = np.load(path)
    img = data[:, :, tslice, zslice]
    seed = i2m.select_seed(img)

    filename = conf.dir_data_temp + "slice.npy"
    np.save(filename, img)
    filename = conf.dir_data_temp + "seed.npy"
    np.save(filename, seed)


