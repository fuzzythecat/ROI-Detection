import sys
sys.path.append("../modules/")

import numpy as np
import img2mask as i2m
from utils import conf

if __name__ == "__main__":

    filename = conf.dir_data_temp + "slice.npy"
    img = np.load(filename)

    filename = conf.dir_data_temp + "endocardial_mask.npy"
    mask = np.load(filename)

    filename = conf.dir_data_temp + "endocardial_position.npy"
    position = np.load(filename)

    endocardial_mask = i2m.img2mask(img, mask=mask, position=position)
    #filename = fh.save_file_dialog()
    filename = conf.dir_data_mask + "endocardial_mask.npy"
    np.save(filename, endocardial_mask)


