import random
import numpy

def crop(img):
    #TODO: crop 40 11*11 segment from each slice(:,:,2:9)

    lim = 11
    tl = img.shape[2]

    idx = 0
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


