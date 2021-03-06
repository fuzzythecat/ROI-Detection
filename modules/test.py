import os
import sys
import dicom
import numpy as np
# import SimpleITK as sitk

from matplotlib import use
use("Qt4Agg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from matplotlib.mlab import dist_point_to_segment

from PyQt4 import QtCore
from PyQt4 import QtGui

import io
import algorithm


from pprint import pprint


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

    # ClickerClass connected with given axis
    cc = None

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, master=None):

        super(MainFrame, self).__init__()



        self.grid = QtGui.QGridLayout()

        self.fig1 = Figure(figsize=(6, 6), dpi=65)
        self.ax1 = self.fig1.add_subplot(111)
        self.canvas1 = FigureCanvas(self.fig1)
        self.canvas1.setParent(self)

        self.fig2 = Figure(figsize=(6, 6), dpi=65)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvas(self.fig2)
        self.canvas2.setParent(self)

        # connect axis activities
        self.cc = ClickerClass(self.ax1, self.ax2, self.canvas1, self.canvas2)

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
        self.btn["endo1"] = QtGui.QPushButton("Multiple")
        self.btn["endo2"] = QtGui.QPushButton("Singular")
        self.btn["epic1"] = QtGui.QPushButton("Multiple")
        self.btn["epic2"] = QtGui.QPushButton("Singular")


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
        self.btn["endo1"].clicked.connect(self.multiple_endocardial_detection)
        self.btn["endo2"].clicked.connect(self.singular_endocardial_detection)
        self.btn["epic1"].clicked.connect(self.multiple_epicardial_detection)
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

        # update slider titles to fit current slicenums
        self.grid.removeWidget(self.title["tslice"])
        self.grid.removeWidget(self.title["zslice"])
        self.title["tslice"].deleteLater()
        self.title["zslice"].deleteLater()
        del self.title["tslice"]
        del self.title["zslice"]

        # set new titles
        self.title["tslice"] = QtGui.QLabel("Time slice [0, {}): ".format(self._tslicenum))
        self.title["tslice"].setStyleSheet("font: bold")
        self.title["tslice"].setAlignment(QtCore.Qt.AlignCenter)

        self.title["zslice"] = QtGui.QLabel("Z slice [0, {}): ".format(self._zslicenum))
        self.title["zslice"].setStyleSheet("font: bold")
        self.title["zslice"].setAlignment(QtCore.Qt.AlignCenter)

        # add title widgets
        self.grid.addWidget(self.title["tslice"], 7, 0)
        self.grid.addWidget(self.title["zslice"], 8, 0)

        # update cc settings
        self.cc.reset_setting()
        self.cc.init_mask(self.cine_mask)
        self.cc.init_img(self.cine_img)
        self.cc.init_vertex()
        self.cc.update_tlimit(self._tmin, self._tmax)
        self.cc.update_zlimit(self._zmin, self._zmax)

        # self.canvas1.draw()
        # self.canvas2.draw()

    def update_tidx(self, value):
        if self._loadflag == True:
            self._tidx = value
            self.update_slice()

            self.cc.update_index(self._tidx, self._zidx)
            self.redraw_img()


    def update_zidx(self, value):
        if self._loadflag == True:
            self._zidx = value
            self.update_slice()

            self.cc.update_index(self._tidx, self._zidx)
            self.redraw_img()


    def update_tmin(self, value):
        self._tmin = value
        self.spinbox["tmin"].setValue(value)
        self.spinbox["tmin"].setRange(0, self._tmax-1)

        self.slider["tidx"].setRange(self._tmin, self._tmax)
        self.spinbox["tidx"].setRange(self._tmin, self._tmax)

        self.cc.update_tlimit(self._tmin, self._tmax)


    def update_tmax(self, value):
        self._tmax = value
        self.spinbox["tmax"].setValue(value)
        self.spinbox["tmax"].setRange(self._tmin+1, self._tslicenum-1)

        self.slider["tidx"].setRange(self._tmin, self._tmax)
        self.spinbox["tidx"].setRange(self._tmin, self._tmax)

        self.cc.update_tlimit(self._tmin, self._tmax)


    def update_zmin(self, value):
        self._zmin = value
        self.spinbox["zmin"].setValue(value)
        self.spinbox["zmin"].setRange(0, self._zmax-1)

        self.slider["zidx"].setRange(self._zmin, self._zmax)
        self.spinbox["zidx"].setRange(self._zmin, self._zmax)

        self.cc.update_zlimit(self._zmin, self._zmax)


    def update_zmax(self, value):
        self._zmax = value
        self.spinbox["zmax"].setValue(value)
        self.spinbox["zmax"].setRange(self._zmin+1, self._zslicenum-1)

        self.slider["zidx"].setRange(self._zmin, self._zmax)
        self.spinbox["zidx"].setRange(self._zmin, self._zmax)

        self.cc.update_zlimit(self._zmin, self._zmax)


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

        # print("\n======start of new session")
        print("\nSubject directory: [%s]" % dirname)
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
        if self._loadflag == False:
            return

        fname = io.save_file_dialog()
        print(fname)


    def singular_endocardial_detection(self):
        if self._loadflag == False:
            return

        print("\nInitializing singular endocardial detection..... ", end="")
        self.cc.set_singular()
        self.cc.switch2seed()
        # print("complete")


    def multiple_endocardial_detection(self):
        if self._loadflag == False:
            return

        print("\nInitializing multiple endocardial detection..... ", end="")
        self.cc.set_multiple()
        self.cc.switch2seed()
        # print("complete")


    def singular_epicardial_detection(self):
        if self._loadflag == False:
            return

        self.cc.set_singular()
        print("sin_epi")


    def multiple_epicardial_detection(self):
        if self._loadflag == False:
            return

        self.cc.set_multiple()
        print("com_epi")


class ClickerClass(object):
    _title = {"plot": "LEFT: add landmark, RIGHT: delete landmark\n"
                    "Press 'm' to switch modes",
              "connect": "'i': insert, 't': toggle vertex, 'RIGHT': delete\n"
                     "Press 'Enter' to crop, 'm' to switch modes",
              "seed": "LEFT: select seed\n"
                      "Press 'enter' to complete",
              "mask": "Binary mask\n",
              "init": "Cine image\n"}

    _tidx, _zidx = 0, 0 # active slice index
    _tmin, _tmax = 0, 100 # index range [_tmin, _tmax] for detection
    _zmin, _zmax = 0, 100 # index range [_zmin, _zmax] for detection

    _detectionflag = None
    _loadflag = False
    _showverts = True
    _epsilon = 5 # cursor sensitivity in pixels
    _modes = "init"
    # True: Place landmarks, False: Connect landmarks
    _alpha = 0.30
    _ind = None # active vertex
    _seed = [] # seed point for endocardial detection

    _cid = []

    cine_img = None # 4d numpy array
    cine_mask = None # 4d numpy array
    mask_slice = None # active mask slice
    cropped = None # 4d numpy array

    # artist objects
    line = None
    plot = None
    poly = None
    verts = None # active position: verts[_tidx][_zidx]
    position = None
    background = None


    def __init__(self, ax1, ax2, canvas1, canvas2):
        # get axis object
        self.ax1 = ax1
        self.ax2 = ax2

        # get figure object
        self.fig1 = ax1.get_figure()
        self.fig2 = ax2.get_figure()

        # get canvas object
        self.canvas1 = canvas1
        self.canvas2 = canvas2

        # quick solution for inactive key_press_event
        self.canvas1.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas1.setFocus()

        self.ax1.set_title(self._title["init"])
        self.ax2.set_title(self._title["mask"])

        # initiate artist objects
        self.plot = self.ax1.plot([], [], marker='o', markerfacecolor='b',
                                        linestyle='none', markersize=5)[0]
        self.poly = Polygon([(0, 0)], animated=True,
                                        alpha=self._alpha)
        self.line = Line2D([], [], marker='o', markerfacecolor='r',
                                        animated=True, markersize=5)

        # add artist objects to the axis
        self.ax1.add_patch(self.poly)
        self.ax1.add_line(self.line)

        self.connect_activity()


    def init_vertex(self):
        tl = self.cine_mask.shape[2]
        zl = self.cine_mask.shape[3]

        # access: position[tl][zl]
        self.position = [[[] for i in range(zl)] for j in range(tl)]
        self.verts = self.position[self._tidx][self._zidx]


    def init_img(self, img):
        self.cine_img = img


    def init_mask(self, mask):
        self.cine_mask = mask
        self.mask_slice = self.cine_mask[:, :, self._tidx, self._zidx]
        self.cropped = np.zeros((self.cine_mask.shape[2], self.cine_mask.shape[3]))


    def reset_setting(self):
        self._showverts = True
        self._modes = "plot"
        self.ax1.set_title(self._title[self._modes])

        self.cine_mask = None
        self.mask_slice = None
        self._seed = []
        self._tidx, self._zidx = 0, 0
        self._tmin, self._zmax = 0, 100
        self._tmin, self._zmax = 0, 100
        self._loadflag = True
        self._detectionflag = None


    def update_index(self, tidx, zidx):
        self._tidx = tidx
        self._zidx = zidx

        self.switch_slice()


    def update_tlimit(self, tmin, tmax):
        self._tmin = tmin
        self._tmax = tmax


    def update_zlimit(self, zmin, zmax):
        self._zmin = zmin
        self._zmax = zmax


    def redraw(self):
        self.ax1.draw_artist(self.poly)
        self.ax1.draw_artist(self.line)
        self.canvas1.blit(self.ax1.bbox)


    def replot(self):
        if self._modes == "seed":
            verts = self._seed[:]
        else:
            verts = self.verts[:]

        if len(verts) > 0:
            x, y = zip(*verts)
        else:
            x, y = [], []

        if not self._modes == "connect":
            self.plot.set_xdata(x)
            self.plot.set_ydata(y)


    def switch_slice(self):
        self.verts = self.position[self._tidx][self._zidx]
        self.mask_slice = self.cine_mask[:, :, self._tidx, self._zidx]
        self.ax2.imshow(self.mask_slice, cmap=plt.cm.gray)

        if self._modes == "connect":
            if len(self.verts) <= 1:
                self.switch_modes()
            else:
                self.poly.xy = np.array(self.verts[:])
                self.line.set_data(zip(*self.poly.xy))
        else:
            self.replot()
            self.poly.xy = [(0, 0)]

        self.canvas1.draw()
        self.canvas2.draw()


    def switch_modes(self):
        if not self._loadflag: return
        if not self._showverts: return
        if self._modes == "seed": return

        if self._modes == "plot":
            self.switch2poly()
        elif self._modes == "connect":
            self.switch2plot()


    def switch2seed(self):
        self._modes = "seed"
        self.ax1.set_title(self._title["seed"])
        self.ax1.set_ylabel("")

        # clears the existing plot
        # self.verts.clear()
        self.replot()
        if self.poly:
            self.poly.xy = [(0, 0)]

        self.canvas1.draw()


    def switch2plot(self):
        self._modes = "plot"
        self.ax1.set_title(self._title["plot"])
        self.ax1.set_ylabel("")

        self.replot()
        if self.poly:
            self.poly.xy = [(0, 0)]


    def switch2poly(self):
        if len(self.verts) == 0:
            return

        self._modes = "connect"
        self.ax1.set_title(self._title["connect"])
        self.ax1.set_ylabel("Alpha: %.2f" %self._alpha)

        self.poly.xy = np.array(self.verts[:])
        self.line.set_data(zip(*self.poly.xy))
        self.plot.set_data([], [])


    def connect_activity(self):
        self.canvas1.mpl_connect('button_press_event',  self.button_press_callback)
        self.canvas1.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas1.mpl_connect('scroll_event', self.scroll_callback)
        self.canvas1.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas1.mpl_connect('draw_event', self.draw_callback)
        self.canvas1.mpl_connect('key_press_event', self.key_press_callback)


    def button_press_callback(self, event):
        if not self._showverts: return
        if not event.inaxes: return
        if not self._loadflag: return

        self._ind = self.get_nearest_vertex_idx(event)
        # Do whichever action corresponds to the mouse button clicked
        if event.button == 1:
            self.add_vertex(event)
        elif event.button == 3:
            self.remove_vertex(event)
        # Re-plot the landmarks on canvas
        self.replot()
        self.canvas1.draw()


    def button_release_callback(self, event):
        if not self._loadflag: return
        if not self._showverts: return

        self._ind = None


    def scroll_callback(self, event):
        if not self._loadflag: return
        if not self._showverts: return
        if not self._modes == "connect": return

        if event.button == 'up':
            if self._alpha < 1.00:
                self._alpha += 0.05
        elif event.button == 'down':
            self._alpha -= 0.05
            if self._alpha <= 0.00:
                self._alpha = 0.00

        #print("alpha changed")
        self.ax1.set_ylabel("Alpha: %.2f" % self._alpha)
        self.poly.set_alpha(self._alpha)
        # self.ax1.draw_artist(self.ax1.yaxis)
        self.canvas1.draw()


    def motion_notify_callback(self, event):
        # on mouse movement
        if self._ind is None: return
        if not self._showverts: return
        if self._modes == "seed": return
        if not self._loadflag: return
        if event.button != 1: return
        if not event.inaxes: return


        self.move_vertex_to(event)
        self.canvas1.restore_region(self.background)
        self.redraw()


    def draw_callback(self, event):
        if not self._loadflag:
            return

        if self._modes == "connect":
            self.background = self.canvas1.copy_from_bbox(self.ax1.bbox)
            self.redraw()


    def key_press_callback(self, event):
        if not self._loadflag: return
        if not event.inaxes: return

        # print("key_press active")

        if event.key == 't':
            # self.switch_vis()
            pass
        elif event.key == 'm':
            self.switch_modes()
        elif event.key == 'i':
            self.insert_vertex(event)
        elif event.key == 'enter':
            if self._modes == "connect":
                self.poly2mask()
            elif self._detectionflag == "singular":
                self.singular_endocardial_detection()
            elif self._detectionflag == "multiple":
                self.multiple_endocardial_detection()

        self.canvas1.draw()


    def poly2mask(self):
        if not self._modes == "connect":
            return

        for x in range(self.cine_mask.shape[1]):
            for y in range(self.cine_mask.shape[0]):
                if self.poly.get_path().contains_point((x,y)):
                    #self.covered_pixels.append((x,y))
                    self.mask_slice[y][x] = 1
                else:
                    self.mask_slice[y][x] = 0

        if(len(self.verts) > 2):
            self.cropped[self._tidx][self._zidx] = True
        else:
            self.cropped[self._tidx][self._zidx] = False

        self.ax2.imshow(self.mask_slice, cmap=plt.cm.gray)
        self.canvas2.draw()


    def add_vertex(self, event):
        # Adds a point at cursor
        if self._modes == "connect":
            return
        if not self._loadflag:
            return

        if self._modes == "seed":
            verts = self._seed
            verts.clear()
        else:
            verts = self.verts
        verts.append((int(event.xdata), int(event.ydata)))


    def insert_vertex(self, event):
        if not self._modes == "connect": return
        if not self._showverts: return
        if not self._loadflag: return

        p = event.xdata, event.ydata  # display coords
        mod = len(self.verts)
        for i in range(len(self.verts)):
            s0 = self.verts[i % mod]
            s1 = self.verts[(i + 1) % mod]
            d = dist_point_to_segment(p, s0, s1)
            if d <= 5:
                self.poly.xy = np.array(
                               list(self.poly.xy[: i+1]) +
                               [(event.xdata, event.ydata)] +
                               list(self.poly.xy[i+1 :]))
                self.line.set_data(zip(*self.poly.xy))
                self.verts = [tup for i,
                              tup in enumerate(self.poly.xy) if i != len(self.poly.xy)-1]
                break

        self.position[self._tidx][self._zidx] = self.verts


    def remove_vertex(self, event):
        # Removes the point closest to the cursor
        if not self._loadflag:
            return
        if self._modes == "seed":
            return

        index = self._ind
        if not index is None:
            del self.verts[index]
            if self._modes == "connect":
                if len(self.verts) <= 1:
                    self.switch_modes()
                else:
                    self.poly.xy = [x for x in self.verts]
                    self.line.set_data(zip(*self.poly.xy))


    def get_nearest_vertex_idx(self, event):
        if len(self.verts) > 0:
            distance = [(v[0] - event.xdata) ** 2 +
                        (v[1] - event.ydata) ** 2 for v in self.verts]
            if np.sqrt(min(distance)) <= self._epsilon:
                return distance.index(min(distance))
        return None


    def move_vertex_to(self, event):
        x, y = event.xdata, event.ydata
        self.poly.xy[self._ind] = x, y
        self.verts[self._ind] = x, y
        if self._ind == 0:
            self.poly.xy[-1] = self.poly.xy[self._ind]
        self.line.set_data(zip(*self.poly.xy))


    def singular_endocardial_detection(self):
        if not self._modes == "seed":
            return

        img_slice = self.cine_img[:, :, self._tidx, self._zidx]
        if len(self._seed) == 0:
            return

        print("complete")
        print("seed set at", (int(self._seed[0][0]),\
                              int(self._seed[0][1])))
        print("segmenting mask..... ", end="")

        self.mask_slice[:, :] = \
            algorithm.endocardial_detection(img_slice,
            (int(self._seed[0][0]), int(self._seed[0][1])))[:, :]

        # if valid mask
        if int(np.sum(self.mask_slice)) != 0:
            self.cropped[self._tidx][self._zidx] = True

            print("complete")
            print("calculating hull..... ", end="")

            try:
                self.verts[:] = algorithm.convex_hull(self.mask_slice)
            except:
                print("failure")

            print("complete")

            self.switch2poly()
            self.poly2mask()
        else:
            print("segmentation failure")
            self.switch2plot()
            self.cropped[self._tidx][self._zidx] = False

        self._seed = []
        self.canvas1.draw()


    def multiple_endocardial_detection(self):
        if not self._modes == "seed":
            return

        if len(self._seed) == 0:
            return

        print("complete")
        print("seed set at", (int(self._seed[0][0]),\
                              int(self._seed[0][1])))

        print("segmenting mask ", end="")
        # mod = int(((self._tmin+self._tmax)/5)+0.5)
        for t in range(self._tmin, self._tmax+1):

            # status bar
            # if mod != 0 && t%mod == 0:
            #    print(".", end="", flush=True)

            for z in range(self._zmin, self._zmax+1):
                img_slice = self.cine_img[:, :, t, z]
                self.mask_slice = self.cine_mask[:, :, t, z]
                self.mask_slice[:, :] = \
                               algorithm.endocardial_detection(img_slice,
                               (int(self._seed[0][0]), int(self._seed[0][1])))[:, :]

                if int(np.sum(self.mask_slice)) != 0:
                   self.cropped[t][z] = True
                else:
                    self.cropped[t][z] = False

        print("complete")

        print("calculating hull", end="")
        for t in range(self._tmin, self._tmax):

            # status bar
            #if t%(mod) == 0:
            #    print(".", end="", flush=True)

            for z in range(self._zmin, self._zmax):

                if self.cropped[t][z] == False:
                    continue
                self.mask_slice = self.cine_mask[:, :, t, z]
                # self.verts = self.position[t][z]

                self.position[t][z] = algorithm.convex_hull(self.mask_slice)

                self.poly.xy = np.array(self.position[t][z])
                for x in range(self.mask_slice.shape[1]):
                    for y in range(self.mask_slice.shape[0]):
                        if self.poly.get_path().contains_point((x,y)):
                            self.mask_slice[y][x] = 1
                        else:
                            self.mask_slice[y][x] = 0

        print(" complete")
        # print("")

        self.verts = self.position[self._tidx][self._zidx]
        self.mask_slice = self.cine_mask[:, :, self._tidx, self._zidx]

        self.ax2.imshow(self.mask_slice, cmap=plt.cm.gray)
        self._seed = []

        if len(self.verts) <= 2:
            self.switch2plot()
        else:
            self.switch2poly()

        self.canvas1.draw()
        self.canvas2.draw()


    def set_singular(self):
        self._detectionflag = "singular"


    def set_multiple(self):
        self._detectionflag = "multiple"



class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()

        '''
        self.fig = MainFrame()
        _widget = QtGui.QWidget()
        _layout = QtGui.QVBoxLayout(_widget)
        _layout.addWidget(self.fig)
        self.setCentralWidget(_widget)
        '''




        self.setWindowTitle("Fuzzy Rocks!")

        extractAction = QtGui.QAction("sdg", self)
        extractAction.setShortcut("Ctrl+K")
        extractAction.setStatusTip("leave the App")
        extractAction.triggered.connect(self.close_application)

        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addMenu("&work")
        fileMenu.addAction(extractAction)







        self.show()


    def download(self):
        self.completed = 0

        while self.completed < 100:
            self.completed += 0.00001
            self.progress.setValue(self.completed)


    def home(self):
        btn = QtGui.QPushButton("Quit", self)
        btn.resize(100, 100)
        btn.move(100, 100)

        btn.clicked.connect(self.close_application)





        self.show()


    def close_application(self):
        self.setWindowTitle("QUit")
        sys.exit()


def main():

    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())


main()
