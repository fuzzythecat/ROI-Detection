from matplotlib import use
use("Qt4Agg")
import numpy as np
import sys

from PyQt4.QtGui import *


import modules.io as io
import modules.algorithm as alg
import modules.gui as gui
import modules.conf as conf

''' when using .dcm file
fname = fh.get_file_path(filetypes=[("dicom", ".dcm")])
ds = dicom.read_file(fname)
dat = ds.pixel_array
'''

#fname = io.get_file_path()

fname = "/Users/Ellsbury/Desktop/cinedata_1.npy"
data = np.load(fname)
data = alg.resize(data, mode=256)
print(data.shape)

app = QApplication(sys.argv)
fig = gui.MainFrame()
fig.show()
app.exec_()

'''
fig1 = plt.figure()
ax1 = fig1.add_subplot(1, 1, 1)
ax1.imshow(dat, cmap=plt.cm.gray)

plt.show()
'''
