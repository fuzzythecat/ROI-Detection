import numpy
import matplotlib.pyplot as plt

if __name__ == "__main__":

    img2d = numpy.load("test2d.npy")

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.imshow(img2d, cmap = plt.cm.gray)

    plt.show()
