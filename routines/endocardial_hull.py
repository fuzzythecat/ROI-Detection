import sys
sys.path.append("../modules/")

import numpy as np
from scipy.spatial import ConvexHull

from utils import conf
import img2mask as i2m

if __name__ == "__main__":

    filename = conf.dir_data_temp + "endocardial_mask.npy"
    mask = np.load(filename)

    points = []

    for x in range(mask.shape[0]):
        for y in range(mask.shape[1]):
            if mask[x][y] > 0.0:
                points.append([y, x])

    hull = ConvexHull(points)

    position = []
    for idx in hull.vertices:
        position.append(points[idx])

    """
    x, y = zip(*points)
    xp, yp = zip(*position)

    plt.plot(x, y, 'r--', lw=2)
    plt.plot(xp, yp, 'b--', lw=2)

    plt.show()
    """

    filename = conf.dir_data_temp + "slice.npy"
    img = np.load(filename)
    endocardial_mask = i2m.img2mask(img, mask=mask, position=position)

    filename = conf.dir_data_mask + "endocardial_mask.npy"
    np.save(filename, endocardial_mask)

