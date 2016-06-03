import sys
sys.path.append("../modules/")

import numpy as np
from scipy.spatial import ConvexHull

from utils import conf

if __name__ == "__main__":

    filename = conf.dir_data_temp + "mask.npy"
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

    filename = conf.dir_data_temp + "position.npy"
    np.save(filename, position)

