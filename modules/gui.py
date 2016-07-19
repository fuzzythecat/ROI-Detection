import os
import sys
import dicom
import numpy as np

from matplotlib import use
use("Qt4Agg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt4 import QtCore
from PyQt4 import QtGui

from modules import io
from modules import algorithm

class MainFrame(QtGui.QWidget):

    _tidx = 0 # active t slice index
    _zidx = 0 # active z slice index

    _loadflag = False

    _tslicenum = 100 # original index range [0, _tslicenum)
    _zslicenum = 100 # original index range [0, _zslicenum)
    _tmin, _tmax = 0, 100 # index range [_tmin, _tmax) for t index in use
    _zmin, _zmax = 0, 100 # index range [_zmin, _zmax) for z index in use

    cine_img = None
    cine_mask = None

    mask_slice = None
    img_slice = None

    # gui-variables
    btn = {}
    spinbox = {}
    slider = {}
    title = {}

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, master=None):

        super(MainFrame, self).__init__()

        self.grid = QtGui.QGridLayout()

        self.fig1 = Figure(figsize=(5, 5), dpi=100)
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvas(self.fig1)

        self.fig2 = Figure(figsize=(5, 5), dpi=100)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvas(self.fig2)

        # gui setup
        self.set_button()
        self.set_title()
        self.set_slider()
        self.set_spinbox()

        self.add_widget()
        self.connect_activity()

        self.setLayout(self.grid)


    def set_button(self):
        self.btn["load"] = QtGui.QPushButton("Load Subject Directory")
        self.btn["save"] = QtGui.QPushButton("Save")
        self.btn["endo1"] = QtGui.QPushButton("All")
        self.btn["endo2"] = QtGui.QPushButton("Current")
        self.btn["epic1"] = QtGui.QPushButton("All")
        self.btn["epic2"] = QtGui.QPushButton("Current")


    def set_title(self):
        self.setWindowTitle("Border Detection")

        self.title["endo"] = QtGui.QLabel("Endocardial detection: ")
        self.title["endo"].setStyleSheet("font: bold")
        self.title["endo"].setAlignment(QtCore.Qt.AlignCenter)

        self.title["epic"] = QtGui.QLabel("Epicardial  detection: ")
        self.title["epic"].setStyleSheet("font: bold")
        self.title["epic"].setAlignment(QtCore.Qt.AlignCenter)

        self.title["tslice"] = QtGui.QLabel("Time slice [0, 30): ")
        self.title["tslice"].setStyleSheet("font: bold")
        self.title["tslice"].setAlignment(QtCore.Qt.AlignCenter)

        self.title["zslice"] = QtGui.QLabel("Z slice [0, 15): ")
        self.title["zslice"].setStyleSheet("font: bold")
        self.title["zslice"].setAlignment(QtCore.Qt.AlignCenter)

        self.title["tmax"] = QtGui.QLabel("T maximum: ")
        self.title["tmax"].setStyleSheet("font: bold")
        self.title["tmax"].setAlignment(QtCore.Qt.AlignCenter)

        self.title["tmin"] = QtGui.QLabel("T minimum: ")
        self.title["tmin"].setStyleSheet("font: bold")
        self.title["tmin"].setAlignment(QtCore.Qt.AlignCenter)

        self.title["zmax"] = QtGui.QLabel("Z maximum: ")
        self.title["zmax"].setStyleSheet("font: bold")
        self.title["zmax"].setAlignment(QtCore.Qt.AlignCenter)

        self.title["zmin"] = QtGui.QLabel("Z minimum: ")
        self.title["zmin"].setStyleSheet("font: bold")
        self.title["zmin"].setAlignment(QtCore.Qt.AlignCenter)


    def set_slider(self):
        # slides on the time-axis
        self.slider["tidx"] = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider["tidx"].setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider["tidx"].setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider["tidx"].setTickInterval(5)
        self.slider["tidx"].setSingleStep(1)
        self.slider["tidx"].setTracking(True)
        self.slider["tidx"].setRange(0, 29)

        # slides on the z-axis
        self.slider["zidx"] = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider["zidx"].setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider["zidx"].setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider["zidx"].setTickInterval(5)
        self.slider["zidx"].setSingleStep(1)
        self.slider["zidx"].setTracking(True)
        self.slider["zidx"].setRange(0, 14)


    def set_spinbox(self):
        # sets active t indices of self.cine_img
        self.spinbox["tidx"] = QtGui.QSpinBox()
        self.spinbox["tidx"].setRange(0, 29)
        self.spinbox["tidx"].setSingleStep(1)

        # sets active z indices of self.cine_img
        self.spinbox["zidx"] = QtGui.QSpinBox()
        self.spinbox["zidx"].setRange(0, 14)
        self.spinbox["zidx"].setSingleStep(1)

        # sets lower t-index limit of slices in effect
        self.spinbox["tmin"] = QtGui.QSpinBox()
        self.spinbox["tmin"].setRange(0, 29)
        self.spinbox["tmin"].setSingleStep(1)
        # sets upper t-index limit of slices in effect
        self.spinbox["tmax"] = QtGui.QSpinBox()
        self.spinbox["tmax"].setRange(0, 29)
        self.spinbox["tmax"].setSingleStep(1)
        self.spinbox["tmax"].setValue(1)

        # sets lower z-index limit of slices in effect
        self.spinbox["zmin"] = QtGui.QSpinBox()
        self.spinbox["zmin"].setRange(0, 14)
        self.spinbox["zmin"].setSingleStep(1)
        # sets upper z-index limit of slices in effect
        self.spinbox["zmax"] = QtGui.QSpinBox()
        self.spinbox["zmax"].setRange(0, 14)
        self.spinbox["zmax"].setSingleStep(1)
        self.spinbox["zmax"].setValue(1)


    def connect_activity(self):
        # connect buttons
        self.btn["load"].clicked.connect(self.load_directory)
        self.btn["save"].clicked.connect(self.save_img)
        self.btn["endo1"].clicked.connect(self.complete_endocardial_detection)
        self.btn["endo2"].clicked.connect(self.singular_endocardial_detection)
        self.btn["epic1"].clicked.connect(self.complete_epicardial_detection)
        self.btn["epic2"].clicked.connect(self.singular_epicardial_detection)

        # connect spinboxes
        self.spinbox["tidx"].valueChanged.connect(self.slider["tidx"].setValue)
        self.spinbox["zidx"].valueChanged.connect(self.slider["zidx"].setValue)

        self.spinbox["tmin"].valueChanged.connect(self.update_tmin)
        self.spinbox["tmax"].valueChanged.connect(self.update_tmax)
        self.spinbox["zmin"].valueChanged.connect(self.update_zmin)
        self.spinbox["zmax"].valueChanged.connect(self.update_zmax)

        # connect sliders
        self.slider["tidx"].valueChanged.connect(self.spinbox["tidx"].setValue)
        self.slider["tidx"].valueChanged.connect(self.update_tidx)
        self.slider["zidx"].valueChanged.connect(self.spinbox["zidx"].setValue)
        self.slider["zidx"].valueChanged.connect(self.update_zidx)


    def update_tmin(self, value):
        self._tmin = value
        self.spinbox["tmin"].setValue(value)
        self.spinbox["tmin"].setRange(0, self._tmax-1)

        self.slider["tidx"].setRange(self._tmin, self._tmax)
        self.spinbox["tidx"].setRange(self._tmin, self._tmax)


    def update_tmax(self, value):
        self._tmax = value
        self.spinbox["tmax"].setValue(value)
        self.spinbox["tmax"].setRange(self._tmin+1, self._tslicenum-1)

        self.slider["tidx"].setRange(self._tmin, self._tmax)
        self.spinbox["tidx"].setRange(self._tmin, self._tmax)


    def update_zmin(self, value):
        self._zmin = value
        self.spinbox["zmin"].setValue(value)
        self.spinbox["zmin"].setRange(0, self._zmax-1)

        self.slider["zidx"].setRange(self._zmin, self._zmax)
        self.spinbox["zidx"].setRange(self._zmin, self._zmax)


    def update_zmax(self, value):
        self._zmax = value
        self.spinbox["zmax"].setValue(value)
        self.spinbox["zmax"].setRange(self._zmin+1, self._zslicenum-1)

        self.slider["zidx"].setRange(self._zmin, self._zmax)
        self.spinbox["zidx"].setRange(self._zmin, self._zmax)


    def add_widget(self):
        # add buttons
        self.grid.addWidget(self.btn["load"], 0, 0)
        self.grid.addWidget(self.btn["save"], 1, 0)
        self.grid.addWidget(self.btn["endo1"], 0, 2)
        self.grid.addWidget(self.btn["endo2"], 0, 3)
        self.grid.addWidget(self.btn["epic1"], 1, 2)
        self.grid.addWidget(self.btn["epic2"], 1, 3)

        # add titles
        self.grid.addWidget(self.title["endo"], 0, 1)
        self.grid.addWidget(self.title["epic"], 1, 1)
        self.grid.addWidget(self.title["tslice"], 7, 0)
        self.grid.addWidget(self.title["zslice"], 8, 0)
        self.grid.addWidget(self.title["tmin"], 9, 0)
        self.grid.addWidget(self.title["tmax"], 9, 2)
        self.grid.addWidget(self.title["zmin"], 10, 0)
        self.grid.addWidget(self.title["zmax"], 10, 2)

        # add sliders
        self.grid.addWidget(self.slider["tidx"], 7, 2, 1, 2)
        self.grid.addWidget(self.slider["zidx"], 8, 2, 1, 2)

        # add spinboxes
        self.grid.addWidget(self.spinbox["tidx"], 7, 1)
        self.grid.addWidget(self.spinbox["zidx"], 8, 1)
        self.grid.addWidget(self.spinbox["tmin"], 9, 1)
        self.grid.addWidget(self.spinbox["tmax"], 9, 3)
        self.grid.addWidget(self.spinbox["zmin"], 10, 1)
        self.grid.addWidget(self.spinbox["zmax"], 10, 3)

        # add canvas for image display
        self.grid.addWidget(self.canvas1, 2, 0, 5, 2)
        self.grid.addWidget(self.canvas2, 2, 2, 5, 2)


    def reset_setting(self):
        self._tslicenum = self.cine_img.shape[2]
        self._zslicenum = self.cine_img.shape[3]

        self._tidx, self._zidx = 0, 0
        self._tmin, self._zmin = 0, 0
        self._tmax = self._tslicenum-1
        self._zmax = self._zslicenum-1

        self.slider["tidx"].setRange(self._tmin, self._tmax)
        self.slider["zidx"].setRange(self._zmin, self._zmax)
        self.spinbox["tidx"].setRange(self._tmin, self._tmax)
        self.spinbox["zidx"].setRange(self._zmin, self._zmax)

        self.spinbox["tmin"].setRange(0, self._tmax-1)
        self.spinbox["zmin"].setRange(0, self._zmax-1)
        self.spinbox["tmax"].setRange(self._tmin+1, self._tslicenum-1)
        self.spinbox["zmax"].setRange(self._zmin+1, self._zslicenum-1)

        self.slider["tidx"].setValue(self._tidx)
        self.slider["zidx"].setValue(self._zidx)

        self.spinbox["tidx"].setValue(self._tidx)
        self.spinbox["zidx"].setValue(self._zidx)

        self.spinbox["tmin"].setValue(0)
        self.spinbox["zmin"].setValue(0)
        self.spinbox["tmax"].setValue(self._tmax)
        self.spinbox["zmax"].setValue(self._zmax)


    def update_tidx(self, value):
        if self._loadflag == True:
            self._tidx = value
            self.update_slice()

            self.redraw_img()


    def update_zidx(self, value):
        if self._loadflag == True:
            self._zidx = value
            self.update_slice()

            self.redraw_img()


    def update_slice(self):
        self.img_slice = self.cine_img[:, :, self._tidx, self._zidx]
        self.mask_slice = self.cine_mask[:, :, self._tidx, self._zidx]


    def load_directory(self):
        dirname = io.get_directory()

        # directory not chosen
        if len(dirname) == 0:
            return

        # invalid directory chosen
        if "cine" not in os.listdir(dirname):
            print("Subject directory must contain 'cine/'\n")
            return

        print("\nstart of new session======")
        print("Subject directory: [%s]" % dirname)
        cinedir = dirname + "/cine/"

        temp = io.load_cine_from_directory(cinedir)
        if(len(temp.shape) != 4):
            print("Inavlid cine image")
            return
        elif(temp is None):
            print("Failed to load cine image")
            return

        self.cine_img = temp
        self._loadflag = True
        self.cine_img = algorithm.resize(self.cine_img, mode=256)

        self.img_slice = self.cine_img[:, :, 0, 0]
        self.cine_mask = np.zeros(self.cine_img.shape)
        self.mask_slice = self.cine_mask[:, :, 0, 0]
        self.reset_setting()

        self.redraw()


    def redraw_img(self):
        self.ax1.imshow(self.img_slice, cmap=plt.cm.gray)
        self.canvas1.draw()


    def redraw_mask(self):
        self.ax2.imshow(self.mask_slice, cmap=plt.cm.gray)
        self.canvas2.draw()


    def redraw(self):
        self.redraw_img()
        self.redraw_mask()


    def save_img(self):
        fname = io.save_file_dialog()
        print(fname)


    def singular_endocardial_detection(self):
        print("sin_end")


    def complete_endocardial_detection(self):
        print("com_end")


    def singular_epicardial_detection(self):
        print("sin_epi")


    def complete_epicardial_detection(self):
        print("com_epi")
