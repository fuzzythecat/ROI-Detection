import numpy as np

from matplotlib import use
use("Qt4Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MainFrame(QWidget):

    def __init__(self, master=None):

        super(MainFrame, self).__init__()

        self.grid = QGridLayout()

        self.btn1 = QPushButton("Load")
        self.btn.clicked.connect(self.load_img)
        self.grid.addWidget(self.btn1, 0, 0)

        self.btn2 = QPushButton("Save")
        self.btn2.clicked.connect(self.save_img)




        def load_img(self):
            pass

        def save_img(self):
            pass
