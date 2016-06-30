import sys
sys.path.append("../modules/")

import numpy as np
import matplotlib.pyplot as plt
from skimage import feature

from utils import conf

if __name__ == "__main__":

    filename = conf.dir_data_temp + "slice.npy"
    img = np.load(filename)
    filename = conf.dir_data_mask + "endocardial_mask.npy"
    endocardial_mask = np.load(filename)
    filename = conf.dir_data_mask + "epicardial_mask.npy"
    epicardial_mask = np.load(filename)

    # get contour of masks

    endocardial_border = feature.canny(endocardial_mask, sigma=3)
    #endocardial_border = np.zeros((img.shape[0], img.shape[1]))
    #endocardial_border = _endocardial_border[

    epicardial_border = feature.canny(epicardial_mask, sigma=3)

    fig1 = plt.figure()
    ax11 = fig1.add_subplot(1, 3, 1)
    ax11.imshow(img, cmap=plt.cm.gray)
    ax11.set_xlim([0., img.shape[1]])
    ax11.set_ylim([img.shape[0], 0.])

    ax12 = fig1.add_subplot(1, 3, 2)
    ax12.imshow(epicardial_mask, cmap=plt.cm.gray)
    ax12.set_xlim([0., endocardial_mask.shape[1]])
    ax12.set_ylim([endocardial_mask.shape[0], 0.])

    ax13 = fig1.add_subplot(1, 3, 3)
    ax13.imshow(img, cmap=plt.cm.gray)
    ax13.set_xlim([0., endocardial_mask.shape[1]])
    ax13.set_ylim([endocardial_mask.shape[0], 0.])
    ax13.contour(epicardial_border, colors='r')



    plt.show()
