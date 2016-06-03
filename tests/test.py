#import matplotlib
import sys
import numpy
#import tkinter as tk
#from tkinter import filedialog

#with open('a.txt', 'w') as f:
#    f.write('asdsfafsdsad')


sys.path.append ('../utils')
sys.path.append ('../modules')
sys.path.append ('../data/cine')

#from conf import config_test
#import img2mask
import file_handler as fh

filepath = fh.load_file_npy()
img_ori = numpy.load(filepath[0])

zslice = 7
tslice = 1

img = img_ori[:, :, tslice, zslice]
numpy.save("test2d", img)



#img = numpy.load('cinedata_1.npy')
#img2mask(img[:,:,1,1])
#config_test()
