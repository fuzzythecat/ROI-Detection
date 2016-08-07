def endocardial_detection(img, seed):
    """
    Wrapper function for SimpleITK image segmetation.
    Detect and crop binary mask from image from given seed point.

    Parameters
    ----------
    img : 2-dimensional numpy array image

    seed : [(x, y)] position value to run segmentation from

    Returns
    -------
    seg_arr : 2-dimensional numpy array binary mask
    """
    import SimpleITK as sitk

    img_itk = sitk.GetImageFromArray(img)
    seg = sitk.Image(img_itk.GetSize(), sitk.sitkUInt8)
    seg.CopyInformation(img_itk)
    seg[seed] = 1

    seg = sitk.BinaryDilate(seg, 3)
    seg = sitk.ConnectedThreshold(img_itk, seedList=[seed],
                                  lower=300, upper=650)

    seg_arr = sitk.GetArrayFromImage(seg)

    return seg_arr


def convex_hull(binary_mask):
    """
    Wrapper funcion for scipy.spatial.ConvexHull. From 2-dimensional
    binary mask, return 1-dimensional list of hull vertices.

    Parameters
    ----------
    binary_mask : A binary mask, numpy array of dimension 4.

    Returns
    -------
    position : 1-dimensional list of hull vertices.
    """
    from scipy.spatial import ConvexHull

    points = []

    for x in range(binary_mask.shape[0]):
        for y in range(binary_mask.shape[1]):
            if binary_mask[x][y] > 0.:
                points.append([y, x])

    if len(points) < 3:
        return points

    hull = ConvexHull(points)


    position = []
    for idx in hull.vertices:
        position.append(points[idx])

    return position


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

    xl = img.shape[0]
    yl = img.shape[1]
    tl = img.shape[2]
    zl = img.shape[3]

    print("resizing cine data..... ", end="")

    if mode == 64:
        temp = zeros((256, 256, tl, zl))
        temp[:, :232, :, :] = img[16:, :232, :, :zl]

        ret = zeros((64, 64, tl, zl))
        for t in range(tl):
            if(t % (tl/5) == 0):
                print(".", end="", flush=True)

            for z in range(zl):
                ret[:, :, t, z] = imresize(
                        temp[:, :, t, z], (64, 64), interp='nearest')

    elif mode == 256:
        ret = zeros((256, 256, tl, zl))

        if(xl >= 256 and yl >= 256):
            ret[:, :, :, :] = img[xl-256:, yl-256:, :, :]
        elif (xl >= 256 and yl <= 256):
            ret[:, 256-yl:, :, :] = img[xl-256:, :, :, :]
        elif(xl <= 256 and yl >= 256):
            ret[256-xl:, :, :, :] = img[:, yl-256:, :, :]
        elif(xl <= 256 and yl <= 256):
            ret[256-xl:, 256-yl:, :, :] = img[:, :, :, :]

    print("complete")
    print("resized dimension: ", ret.shape)

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





