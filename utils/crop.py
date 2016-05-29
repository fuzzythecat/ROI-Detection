import random
import numpy

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

    if img is None:
        raise AttributeError("User must provide <numpy.ndarray> image")

    lim = 11
    tl = img.shape[2]

    idx = 0

    # 9600 = 8 * 30 * 40
    patch = numpy.zeros((9600, lim, lim))

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


