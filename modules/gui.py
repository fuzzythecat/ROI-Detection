import numpy as np

from matplotlib import use
use("Qt4Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt4 import QtCore
from PyQt4 import QtGui


class MainFrame(QtGui.QWidget):

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, master=None):

        super(MainFrame, self).__init__()

        self.setWindowTitle("Border Detection")
        self.grid = QtGui.QGridLayout()

        self.btn1 = QtGui.QPushButton("Load")
        self.btn1.clicked.connect(self.load_img)
        self.grid.addWidget(self.btn1, 0, 0)

        self.btn2 = QtGui.QPushButton("Save")
        self.btn2.clicked.connect(self.save_img)
        self.grid.addWidget(self.btn2, 1, 0)

        self.title1 = QtGui.QLabel("Endocardial detection: ")
        self.title1.setStyleSheet("font: bold")
        self.title1.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.title1, 0, 1)

        self.title2 = QtGui.QLabel("Epicardial  detection: ")
        self.title2.setStyleSheet("font: bold")
        self.title2.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.title2, 1, 1)

        self.btn3 = QtGui.QPushButton("All")
        self.btn3.clicked.connect(self.complete_endocardial_detection)
        self.grid.addWidget(self.btn3, 0, 2)
        self.btn4 = QtGui.QPushButton("Current")
        self.btn4.clicked.connect(self.singular_endocardial_detection)
        self.grid.addWidget(self.btn4, 0, 3)

        self.btn5 = QtGui.QPushButton("All")
        self.btn5.clicked.connect(self.complete_epicardial_detection)
        self.grid.addWidget(self.btn5, 1, 2)
        self.btn6 = QtGui.QPushButton("Current")
        self.btn6.clicked.connect(self.singular_epicardial_detection)
        self.grid.addWidget(self.btn6, 1, 3)

        self.fig = Figure(figsize=(10, 10), dpi=100)
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)

        self.canvas = FigureCanvas(self.fig)
        self.grid.addWidget(self.canvas, 2, 0, 5, 4)

        self.slider_t = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider_t.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider_t.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider_t.setTickInterval(5)
        self.slider_t.setSingleStep(1)
        self.grid.addWidget(self.slider_t, 7, 2, 1, 2)

        self.slider_z = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider_z.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.slider_z.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.slider_z.setTickInterval(5)
        self.slider_z.setSingleStep(1)
        self.grid.addWidget(self.slider_z, 8, 2, 1, 2)

        self.spinbox_t = QtGui.QSpinBox()
        self.spinbox_t.setRange(0, 29)
        self.spinbox_t.setSingleStep(1)
        self.grid.addWidget(self.spinbox_t, 7, 1)

        self.spinbox_z = QtGui.QSpinBox()
        self.spinbox_z.setRange(0, 14)
        self.spinbox_z.setSingleStep(1)
        self.grid.addWidget(self.spinbox_z, 8, 1)

        self.title3 = QtGui.QLabel("Time slice [0, 30): ")
        self.title3.setStyleSheet("font: bold")
        self.title3.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.title3, 7, 0)

        self.title4 = QtGui.QLabel("Z slice [0, 30): ")
        self.title4.setStyleSheet("font: bold")
        self.title4.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.title4, 8, 0)

        self.setLayout(self.grid)

    def load_img(self):
        print("load_img")

    def save_img(self):
        print("save_img")

    def singular_endocardial_detection(self):
        print("sin_end")

    def complete_endocardial_detection(self):
        print("com_end")

    def singular_epicardial_detection(self):
        print("sin_epi")

    def complete_epicardial_detection(self):
        print("com_epi")
