import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import copy
import random
import sys

''' global variables '''

lim = 21 # row / col length of patch

def resize(img):
    # resize each img slice into 256*256 array

    tl = img.shape[2]
    zl = img.shape[3]

    ret = np.zeros((256,256,tl,zl))
    ret[:,:232,:,:] = img[16:,:232,:,:zl]

    return ret


def normalize(img, **kwargs):

    def img_rescale(ret):
        '''rescale entire img set to values 0.0 ~ 1.0'''
        xl = img.shape[0]
        yl = img.shape[1]
        tl = img.shape[2]
        zl = img.shape[3]

        for t in range(tl):
            for z in range(zl):
                max = np.amax(img[:,:,t,z])
                for i in range(xl):
                    for j in range(yl):
                        ret[i,j,t,z] /= max
        return ret

    def patch_rescale(ret):
        '''rescale entire patch set to values between 0.0 ~ 1.0'''
        idx = img.shape[0]
        xl = img.shape[1]
        yl = img.shape[2]

        for i in range(idx):
            max = np.amax(img[i,:,:])
            for x in range(xl):
                for y in range(yl):
                    ret[i,x,y] /= max
        return ret


    flag = kwargs.pop("flag", None)

    if flag is None:
        raise AttributeError("specify flag = [img/patch]")

    ret = copy.deepcopy(img)
    if flag == "img":
        return img_rescale(ret)
    elif flag == "patch":
        return patch_rescale(ret)


def crop(img):
    #TODO: crop 40 11*11 segment from each slice(:,:,2:9)

    tl = img.shape[2]

    idx = 0
    patch = np.zeros((9600, lim, lim))

    for z in range(2, 10):
        for t in range(tl):
            for i in range(40):
                xdisp = random.randrange(75, 175)
                ydisp = random.randrange(75, 175)

                for x in range(lim):
                    for y in range(lim):
                        patch[idx,x,y] = img[x+xdisp,y+ydisp,t,z]
                idx += 1

    return patch


img2 = np.load('cinedata/cinedata_1.npy')
print(img2.shape)

''' resized img '''
img3 = resize(img2)

'''
0 : crop and normalize
1 : normalize and crop
'''
mode = 1

''' output stored in patch_normalized '''
if mode == 0:
    '''crop and normalize'''
    patch = crop(img3)
    patch_normalized = normalize(patch, flag = "patch")

elif mode == 1:
    '''normalize and crop'''
    img3_normalized = normalize(img3, flag = "img")
    patch_normalized = crop(img3_normalized)


''' convert each 2-dimensional array into 1-dimensional array '''
patch_data_x = np.zeros((9600, lim*lim))
for i in range(9600):
    patch_data_x[i] = patch_normalized[i].flatten()

print(patch_data_x.shape[0], patch_data_x.shape[1])

np.save("cine_patch", patch_data_x)





























''' test resize

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.imshow(img3[:,:,1,1], cmap = plt.cm.gray)

plt.show()
'''

''' test img normalization

fig = plt.figure()
for ind_seg in range(nz):

    ax = fig.add_subplot(3, 5, ind_seg+1)
    ax.imshow(img3_normalized[:,:,1,ind_seg], cmap = plt.cm.gray)

plt.show()
'''

''' test patch normalization

fig = plt.figure()
ax2 = fig.add_subplot(2, 1, 2)
ax2.imshow(patch_normalized[555,:,:], cmap = plt.cm.gray)
plt.show()
'''

