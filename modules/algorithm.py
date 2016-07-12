def resize(img, **kwargs):
    """
    Resize 272*232 2-dimensioanl image slice to 256*256 || 64*64.
    Defaults to 64*64.

    Parameters
    ----------
    img : numpy array of dim 4 (default shape: (272, 232, time, z)).

    (optional)
    mode : 64 || 256
        64 : resize using scipy.misc.imresize(interp='nearest') method

        256 : trim by 16 rows from top, and append padding to rightmost
              column.

    Returns
    -------
    img : array of dim 4 (shape (256||64, 256||64, time, z)).
    """

    from scipy.misc import imresize
    from numpy import zeros

    mode = kwargs.pop("mode", 64)

    tl = img.shape[2]
    zl = img.shape[3]

    if mode == 64:
        temp = zeros((256, 256, tl, zl))
        temp[:, :232, :, :] = img[16:, :232, :, :zl]

        ret = zeros((64, 64, tl, zl))
        for t in range(tl):
            for z in range(zl):
                ret[:, :, t, z] = imresize(
                        temp[:, :, t, z], (64, 64), interp='nearest')

    elif mode == 256:
        ret = zeros((256, 256, tl, zl))
        ret[:, :232, :, :] = img[16:, :232, :, :zl]

    return ret


def crop(img, **kwargs):
    """
    From 64*64 images of 30 time frames and z-slice-no's [2:9] (default),
    generate N = 2400 (default) random patches of size 11 (default).

    Parameters
    ----------
    img : numpy array of dim 4 (shape: (64, 64, time, z)).

    (optional)
    len : Length of the sides of generated patches.
    Defaults to 11.

    patch_no : Number of the generated patches per slice.
    Defaults to 10.

    zidx : List of z-indices of input image to be cropped from.
    Defaults to [2 : 9]

    Returns
    -------
    patch : array of dim 3 (shape (idx, len, len)).
    Idx is the total number of generated patches. (default : 10*30*8 = 2400)
    Each patch is of size len*len (default : 11*11).
    """

    from random import randrange
    from numpy import zeros

    if img is None:
        raise AttributeError("User must provide <numpy.ndarray> image")

    lim = 11
    tl = img.shape[2]

    idx = 0

    # 9600 = 8 * 30 * 40
    patch = zeros((9600, lim, lim))

    for z in range(2, 10):
        for t in range(tl):
            for i in range(40):
                xdisp = randrange(75, 175)
                ydisp = randrange(75, 175)

                for x in range(lim):
                    for y in range(lim):
                        patch[idx, x, y] = img[x+xdisp, y+ydisp, t, z]
                idx += 1

    return patch


def normalize(img):
    """
    Normalizes contents of 2-dimensional slice of N-dimensional
    input array to values between 0.0 ~ 1.0. Normalized value is proportional
    to the maximum value in each 2-dim slice.

    Parameters
    ----------
    img : N-dimensional ndarray image containing gray-scale pixel values.
    Ndarray must be either 3 || 4 dimensional.
    if 3-dimensional, iterate through 2-dim slices by 1-dim index.
        img[idx][:, :]

    if 4-dimensional, iterate through 2-dim slices by 3, 4-dim indices
        img[:, :][time][zidx]

    Returns
    -------
    ret : Normalized n-dimensional ndarray
    """

    from numpy import amax
    from copy import deepcopy

    def _determine_dim(img):
        """determine whether input array is 3 || 4 dimension"""
        if len(img.shape) == 3:
            return 3
        elif len(img.shape) == 4:
            return 4
        else:
            return -1

    def _img_rescale(ret):
        """rescale 4-dim img set to values 0.0 ~ 1.0"""
        xl = img.shape[0]
        yl = img.shape[1]
        tl = img.shape[2]
        zl = img.shape[3]

        for t in range(tl):
            for z in range(zl):
                m = amax(ret[:, :, t, z])
                for x in range(xl):
                    for y in range(yl):
                        ret[x, y, t, z] /= m
        return ret

    def _patch_rescale(ret):
        """rescale 3-dim patch set to values between 0.0 ~ 1.0"""
        idx = img.shape[0]
        xl = img.shape[1]
        yl = img.shape[2]

        for i in range(idx):
            m = amax(ret[i, :, :])
            for x in range(xl):
                for y in range(yl):
                    ret[i, x, y] /= m
        return ret

    dim = _determine_dim(img)
    if dim == -1:
        raise AttributeError("ndarray must be [3/4] dimensional")

    ret = deepcopy(img)
    if dim == 3:
        return _patch_rescale(ret)
    elif dim == 4:
        return _img_rescale(ret)


