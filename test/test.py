import matplotlib
import sys
import numpy

sys.path.append ('../utils')
sys.path.append ('../modules')
sys.path.append ('../data/cine')

from config import config_test
import img2mask

img = numpy.load('cinedata_1.npy')


img2mask(img[:,:,1,1])

config_test()
