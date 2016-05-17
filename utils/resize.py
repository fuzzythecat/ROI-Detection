import scipy.misc
from numpy import zeros

def resize(img, **kwargs):
    '''resize 272*232 image slice into 256*256 || 64*64'''

    '''default mode set to 64*64'''
    mode = kwargs.pop("mode", 64)

    tl = img.shape[2]
    zl = img.shape[3]

    if mode == 64:
        temp = zeros((256, 256, tl, zl))
        temp[:, :232, :, :] = img[16:, :232, :, :zl]

        ret = zeros((64, 64, tl, zl))
        for t in range(tl):
            for z in range(zl):
                ret[:, :, t, z] = scipy.misc.imresize(temp[:, :, t, z], (64, 64), interp = 'nearest')

    elif mode == 256:
        ret = zeros((256, 256, tl, zl))
        ret[:, :232, :, : ] = img[16:, :232, :, :zl]

    return ret


if __name__ == "__main__":
    import conf
    import matplotlib.pyplot as plt
    from numpy import load

    tslice = 1
    zslice = 7

    img_ori = load(conf.dir_data_cine + "cinedata_1.npy")
    print(img_ori.shape)
    img_64 = resize(img_ori, mode = 64)
    print(img_64.shape)
    img_256 = resize(img_ori, mode = 256)
    print(img_256.shape)

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.imshow(img_64[:, :, tslice, zslice], cmap = plt.cm.gray)
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.imshow(img_256[:, :, tslice, zslice], cmap = plt.cm.gray)

    plt.show()


