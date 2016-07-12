import file_handler as fh
import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt

if __name__ == "__main__":
    path = fh.get_file_path()
    mask = np.load(path)

    points = []


    for x in range(mask.shape[0]):
        for y in range(mask.shape[1]):
            if mask[x][y] > 0.0:
                points.append([y, x])

    #points = np.random.rand(30, 2)
    #print(points.shape)

    #print(points)

    hull = ConvexHull(points)

    p = []
    for idx in hull.vertices:
        p.append(points[idx])



    x, y = zip(*points)
    xp, yp = zip(*p)

    '''
    for simplex in hull.simplices:
        plt.plot(points[simplex][0], points[simplex][1], 'k-')
    '''

    plt.plot(x, y, 'r--', lw=2)
    plt.plot(xp, yp, 'b--', lw=2)
#plt.plot(points[hull.vertices[0], 0], points[hull.vertices[0], 1], 'ro')

    plt.show()


    filename = fh.save_file_dialog()
    np.save(filename, p)

