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

if __name__ == "__main__":
    import conf
    from resize import resize
    from numpy import load
    img_ori = load(conf.dir_data_cine + "cinedata_1.npy")
    print(img_ori.shape)

    '''resized img to 256*256'''
    img_256 = resize(img_ori, mode=256)
    print(img_256.shape)

    img_normalized_256 = normalize(img_256)
    print(img_normalized_256.shape)
    print(img_normalized_256)
