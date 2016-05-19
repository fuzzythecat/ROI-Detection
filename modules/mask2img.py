import numpy as np
import matplotlib.pyplot as plt
from skimage import feature
from matplotlib.lines import Line2D

def get_center(img):
    # return (xcenter, ycenter)
    xmin = 1000
    xmax = 0
    ymin = 1000
    ymax = 0

    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            if img[x][y] == 1:
                if x < xmin: xmin = x
                if x > xmax: xmax = x
                if y < ymin: ymin = y
                if y > ymax: ymax = y
    xcenter = (xmax + xmin) // 2
    ycenter = (ymax + ymin) // 2

    # print("derived center: ", (xcenter, ycenter))

    center = [xcenter, ycenter]

    return center

tslice = 1
zslice = 7

img_64 = np.load('img_64.npy')
cmask = np.load('circular_mask.npy')
bmask = np.load('boxed_mask.npy')


# read 32*32 boxed mask
bmask_32 = np.load('boxed_mask_32.npy')

# calculate the center
bcenter = get_center(bmask_32)
print(bcenter)

# read 256*256 image
img_256 = np.load('img_256.npy')

# recalculate cetner = 8 * center
bcenter[0] = bcenter[0] * 8
bcenter[1] = bcenter[1] * 8


# crop 100*100 thumbnail, centered at 'recalculated center'

thumbnail = np.zeros((100, 100))
thumbnail[:, :] = img_256[bcenter[0]-50:bcenter[0]+50, bcenter[1]-50:bcenter[1]+50, tslice, zslice]

# get contour of cmask
edges = feature.canny(cmask, sigma = 3)
ccenter = get_center(cmask)

# crop 100*100 thumbnail of the contour, centered at ccenter
cthumbnail = np.zeros((100, 100))
cthumbnail = edges[bcenter[0]-50:bcenter[0]+50, bcenter[1]-50:bcenter[1]+50]


# display cropped image, with the center plotted(50, 50)

fig1 = plt.figure()
ax11 = fig1.add_subplot(1, 4, 1)
ax11.imshow(img_256[:, :, tslice, zslice], cmap=plt.cm.gray, interpolation = 'nearest')
"""preventing plot from rescaling image:"""
ax11.set_xlim([0.0, img_256.shape[1]])
ax11.set_ylim([img_256.shape[0], 0.0])
ax11.autoscale = False

"""preventing plot from clearing image:"""
ax11.hold(True)
ax11.plot(bcenter[1], bcenter[0], marker='o', markerfacecolor='b', linestyle='none', markersize=5)

ax12 = fig1.add_subplot(1, 4, 2)
ax12.imshow(thumbnail[:, :], cmap = plt.cm.gray, interpolation = 'nearest')
ax12.set_xlim([0.0, thumbnail.shape[1]])
ax12.set_ylim([thumbnail.shape[0], 0.0])
ax12.autoscale = False

"""preventing plot from clearing image:"""
ax12.hold(True)
ax12.plot(50, 50, marker='o', markerfacecolor='b', linestyle='none', markersize=5)

ax13 = fig1.add_subplot(1, 4, 3)
ax13.imshow(cthumbnail[:, :], cmap = plt.cm.gray, interpolation = 'nearest')


extent = 100, 0, 100, 0

ax14 = fig1.add_subplot(1, 4, 4)
ax14.imshow(thumbnail[:, :], cmap=plt.cm.gray, interpolation = 'nearest')
"""preventing plot from rescaling image:"""
ax14.set_xlim([0.0, thumbnail.shape[1]])
ax14.set_ylim([thumbnail.shape[0], 0.0])
ax14.autoscale = False

"""preventing plot from clearing image:"""
ax14.hold(True)
ax14.contour(cthumbnail, colors='r')



# save thumbnail
np.save("thumbnail_100", thumbnail)


'''compare with the original set'''


fig2 = plt.figure()
ax21 = fig2.add_subplot(1, 5, 1)
ax21.imshow(img_256[:, :, tslice, zslice], cmap=plt.cm.gray, interpolation='nearest')
"""preventing plot from rescaling image:"""
ax21.set_xlim([0.0, img_256.shape[1]])
ax21.set_ylim([img_256.shape[0], 0.0])
ax21.autoscale = False

"""preventing plot from clearing image:"""
ax21.hold(True)
ax21.plot(ccenter[1], ccenter[0], marker='o', markerfacecolor='b', linestyle='none', markersize=5)

ax22 = fig2.add_subplot(1, 5, 2)
ax22.imshow(img_64[:, :, tslice, zslice], cmap=plt.cm.gray, interpolation='nearest')

ax23 = fig2.add_subplot(1, 5, 3)
ax23.imshow(cmask[:, :], cmap=plt.cm.gray, interpolation='nearest')

ax24 = fig2.add_subplot(1, 5, 4)
ax24.imshow(bmask[:, :], cmap=plt.cm.gray, interpolation='nearest')

ax25 = fig2.add_subplot(1, 5, 5)
ax25.imshow(bmask_32[:, :], cmap=plt.cm.gray, interpolation='nearest')

plt.show()
