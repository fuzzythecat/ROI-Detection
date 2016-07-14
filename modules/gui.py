import numpy as np
from matplotlib import use
use("Qt4Agg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt4 import QtCore
from PyQt4 import QtGui

from modules import io

class MainFrame(QtGui.QWidget):

    _tidx = 0
    _zidx = 0
    _loadflag = False

    _img = None
    _mask = None
    _slice = None

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, master=None):

        super(MainFrame, self).__init__()

        self.setWindowTitle("Border Detection")
        self.grid = QtGui.QGridLayout()

        self.btn1 = QtGui.QPushButton("Load")
        self.btn1.clicked.connect(self.load_img)

        self.btn2 = QtGui.QPushButton("Save")
        self.btn2.clicked.connect(self.save_img)

        self.title1 = QtGui.QLabel("Endocardial detection: ")
        self.title1.setStyleSheet("font: bold")
        self.title1.setAlignment(QtCore.Qt.AlignCenter)

        self.title2 = QtGui.QLabel("Epicardial  detection: ")
        self.title2.setStyleSheet("font: bold")
        self.title2.setAlignment(QtCore.Qt.AlignCenter)

        self.btn3 = QtGui.QPushButton("All")
        self.btn3.clicked.connect(self.complete_endocardial_detection)

        self.btn4 = QtGui.QPushButton("Current")
        self.btn4.clicked.connect(self.singular_endocardial_detection)

        self.btn5 = QtGui.QPushButton("All")
        self.btn5.clicked.connect(self.complete_epicardial_detection)

        self.btn6 = QtGui.QPushButton("Current")
        self.btn6.clicked.connect(self.singular_epicardial_detection)

        self.fig1 = Figure(figsize=(5, 5), dpi=100)
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvas(self.fig1)

        self.fig2 = Figure(figsize=(5, 5), dpi=100)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvas(self.fig2)

        self.slider_t = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider_t.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider_t.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider_t.setTickInterval(5)
        self.slider_t.setSingleStep(1)
        self.slider_t.setTracking(True)
        self.slider_t.setRange(0, 29)

        self.slider_z = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider_z.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider_z.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider_z.setTickInterval(5)
        self.slider_z.setSingleStep(1)
        self.slider_z.setTracking(True)
        self.slider_z.setRange(0, 14)

        self.title3 = QtGui.QLabel("Time slice [0, 30): ")
        self.title3.setStyleSheet("font: bold")
        self.title3.setAlignment(QtCore.Qt.AlignCenter)

        self.title4 = QtGui.QLabel("Z slice [0, 15): ")
        self.title4.setStyleSheet("font: bold")
        self.title4.setAlignment(QtCore.Qt.AlignCenter)

        self.spinbox_t = QtGui.QSpinBox()
        self.spinbox_t.setRange(0, 29)
        self.spinbox_t.setSingleStep(1)

        self.spinbox_z = QtGui.QSpinBox()
        self.spinbox_z.setRange(0, 14)
        self.spinbox_z.setSingleStep(1)

        self.spinbox_t.valueChanged.connect(self.slider_t.setValue)
        self.slider_t.valueChanged.connect(self.spinbox_t.setValue)
        self.slider_t.valueChanged.connect(self.update_t)

        self.spinbox_z.valueChanged.connect(self.slider_z.setValue)
        self.slider_z.valueChanged.connect(self.spinbox_z.setValue)
        self.slider_z.valueChanged.connect(self.update_z)

        self.grid.addWidget(self.btn1, 0, 0)
        self.grid.addWidget(self.btn2, 1, 0)
        self.grid.addWidget(self.title1, 0, 1)
        self.grid.addWidget(self.title2, 1, 1)
        self.grid.addWidget(self.btn3, 0, 2)
        self.grid.addWidget(self.btn4, 0, 3)
        self.grid.addWidget(self.btn5, 1, 2)
        self.grid.addWidget(self.btn6, 1, 3)
        self.grid.addWidget(self.canvas1, 2, 0, 5, 2)
        self.grid.addWidget(self.canvas2, 2, 2, 5, 2)
        self.grid.addWidget(self.slider_t, 7, 2, 1, 2)
        self.grid.addWidget(self.slider_z, 8, 2, 1, 2)
        self.grid.addWidget(self.spinbox_t, 7, 1)
        self.grid.addWidget(self.spinbox_z, 8, 1)
        self.grid.addWidget(self.title3, 7, 0)
        self.grid.addWidget(self.title4, 8, 0)

        self.setLayout(self.grid)

    def initialize(self):
        self._loadflag = False

        self.slider_t.setValue(0)
        self.slider_z.setValue(0)

        self.spinbox_t.setValue(0)
        self.spinbox_t.setValue(0)

        self._tidx, self._zidx = 0, 0

        self._img, self._mask, self._slice = None, None, None

    def update_t(self, value):
        if self._loadflag == True:
            self._tidx = value
            #self._slice = self._img[:, :, self._tidx, self._zidx]

            self.redraw_img()


    def update_z(self, value):
        if self._loadflag == True:
            self._zidx = value
            #self._slice = self._img[:, :, self._tidx, self._zidx]

            self.redraw_img()

    def load_img(self):
        fname = io.get_file_path()
        if len(fname) == 0:
            return

        print("loading [{}]...".format(fname))

        self.initialize()
        self._loadflag = True
        self._img = np.load(fname)
        self._slice = self._img[:, :, self._tidx, self._zidx]
        self._mask = np.zeros(self._slice.shape)

        self.redraw()

    def redraw_img(self):
        self.ax1.imshow(self._img[:, :, self._tidx, self._zidx],
                        cmap=plt.cm.gray)
        self.canvas1.draw()


    def redraw_mask(self):
        self.ax2.imshow(self._mask, cmap=plt.cm.gray)
        self.canvas2.draw()


    def redraw(self):
        self.ax1.imshow(self._img[:, :, self._tidx, self._zidx],
                        cmap=plt.cm.gray)
        self.ax2.imshow(self._mask, cmap=plt.cm.gray)

        self.canvas1.draw()
        self.canvas2.draw()

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
