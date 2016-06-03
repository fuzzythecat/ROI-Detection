from matplotlib import use
use("Qt5Agg")

import numpy
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt

if __name__ == "__main__":

    mask = numpy.load("/Users/Ellsbury/Desktop/arr.npy")
    points = []

    print(type(mask))

    for x in range(mask.shape[0]):
        for y in range(mask.shape[1]):
            if(mask[x][y] == 0):
                continue
            elif(mask[x][y] < 0):
                mask[x][y] = 0
            else:
                mask[x][y] = 1
                points.append([x, y])

    #hull = ConvexHull(mask)






    #plt.show()


