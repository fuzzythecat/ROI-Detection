import os
import numpy as np
import pprint
import pickle
import platform 

from matplotlib import use
use("Qt4Agg")
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from matplotlib.mlab import dist_point_to_segment
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from PyQt4 import QtCore
from PyQt4 import QtGui
from copy import deepcopy
from scipy.ndimage.measurements import center_of_mass

from modules import io
from modules import algorithm
from modules import conf

class MainWindow(QtGui.QMainWindow):


    def __init__(self):
        super(MainWindow, self).__init__()

        # add main widget
        self.fig = MainFrame()
        _widget = QtGui.QWidget()
        _layout = QtGui.QVBoxLayout(_widget)
        _layout.addWidget(self.fig)
        self.setCentralWidget(_widget)

        # set window title
        self.setWindowTitle("Border Detection")

        self.set_menubar()
        self.show()


    def set_menubar(self):
        loadDirectory = QtGui.QAction("Load", self)
        loadDirectory.setShortcut("Ctrl+L")
        loadDirectory.setStatusTip("Load patient directory")
        loadDirectory.triggered.connect(self.fig.load_directory)

        saveData = QtGui.QAction("Save", self)
        saveData.setShortcut("Ctrl+S")
        saveData.setStatusTip("Save patient data")
        saveData.triggered.connect(self.fig.save_img)

        showEndocardium = QtGui.QAction("Endocardium", self)
        showEndocardium.setStatusTip("Show endocardial binary mask")
        showEndocardium.triggered.connect(self.fig.show_endocardium)

        showEpicardium = QtGui.QAction("Epicardium", self)
        showEpicardium.setStatusTip("Show epicardial binary mask")
        showEpicardium.triggered.connect(self.fig.show_epicardium)

        showMyocardium = QtGui.QAction("Myocardium", self)
        showMyocardium.setStatusTip("Show mycardial binary mask")
        showMyocardium.triggered.connect(self.fig.show_myocardium)

        singularEndoDetection = QtGui.QAction("Singular", self)
        singularEndoDetection.setStatusTip("Detect endocardial border on the current slice")
        singularEndoDetection.triggered.connect(self.fig.singular_endocardial_detection)

        multipleEndoDetection = QtGui.QAction("Multiple", self)
        multipleEndoDetection.setStatusTip("Detect endocardial borders on valid slices")
        multipleEndoDetection.triggered.connect(self.fig.multiple_endocardial_detection)

        singularEpicDetection = QtGui.QAction("Singular", self)
        singularEpicDetection.setStatusTip("Detect epicardial border on the current slice")
        singularEpicDetection.triggered.connect(self.fig.singular_epicardial_detection)

        multipleEpicDetection = QtGui.QAction("Multiple", self)
        multipleEpicDetection.setStatusTip("Detect epicardial borders on valid slices")
        multipleEpicDetection.triggered.connect(self.fig.multiple_epicardial_detection)

        self.statusBar()

        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu("&File")
        fileMenu.addAction(loadDirectory)
        fileMenu.addAction(saveData)

        detectionMenu = mainMenu.addMenu("&Detection")
        endoMenu = detectionMenu.addMenu("&Endocardial Detection")
        epicMenu = detectionMenu.addMenu("&Epicardial Detection")

        endoMenu.addAction(singularEndoDetection)
        endoMenu.addAction(multipleEndoDetection)
        epicMenu.addAction(singularEpicDetection)
        epicMenu.addAction(multipleEpicDetection)

        viewMenu = mainMenu.addMenu("&Display")
        viewMenu.addAction(showEndocardium)
        viewMenu.addAction(showEpicardium)
        viewMenu.addAction(showMyocardium)


class MainFrame(QtGui.QWidget):

    tidx = 0 # active t slice index
    zidx = 0 # active z slice index

    loadflag = False

    tslicenum = 100 # original index range [0, _tslicenum)
    zslicenum = 100 # original index range [0, _zslicenum)
    tmin, tmax = 0, 100 # index range [_tmin, _tmax) for t index in use
    zmin, zmax = 0, 100 # index range [_zmin, _zmax) for z index in use

    cine_img = None # original cine image

    display_mode = None # "endocardial", "epicardial", myocardial"

    cine_mask = None # temp
    endocardial_mask = None # 4d numpy binary mask
    epicardial_mask = None # 4d numpy binary mask
    myocardial_mask = None # 4d numpy binary mask

    mask_slice = None
    img_slice = None
    subject_idx = ""

    # gui-variables
    btn = {}
    spinbox = {}
    slider = {}
    title = {}

    # ClickerClass connected with given axis
    cc = None


    def __init__(self, master=None):

        super(MainFrame, self).__init__()
        QtCore.pyqtSignal(int)

        self.grid = QtGui.QGridLayout()

        self.fig1 = Figure(figsize=(6, 6), dpi=65)
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.set_xlim([0, 256])
        self.ax1.set_ylim([256, 0])
        self.canvas1 = FigureCanvas(self.fig1)
        self.canvas1.setParent(self)

        self.fig2 = Figure(figsize=(6, 6), dpi=65)
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_xlim([0, 256])
        self.ax2.set_ylim([256, 0])
        self.canvas2 = FigureCanvas(self.fig2)
        self.canvas2.setParent(self)

        # connect axis activities
        self.cc = ClickerClass(self)

        # gui setup
        self.set_title()
        self.set_slider()
        self.set_spinbox()

        self.add_widget()
        self.connect_activity()

        self.setLayout(self.grid)


    def set_title(self):

        self.title["cineimg"] = QtGui.QLabel("Cine image\n")
        self.title["cineimg"].setStyleSheet("font: bold")
        self.title["cineimg"].setAlignment(QtCore.Qt.AlignCenter)

        self.title["maskimg"] = QtGui.QLabel("Binary mask\n")
        self.title["maskimg"].setStyleSheet("font: bold")
        self.title["maskimg"].setAlignment(QtCore.Qt.AlignCenter)

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

        self.grid.addWidget(self.title["cineimg"], 0, 0, 2, 2)
        self.grid.addWidget(self.title["maskimg"], 0, 2, 2, 2)

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
        self.tslicenum = self.cine_img.shape[2]
        self.zslicenum = self.cine_img.shape[3]

        self.tidx, self.zidx = 0, 0
        self.tmin, self.zmin = 0, 0
        self.tmax = self.tslicenum-1
        self.zmax = self.zslicenum-1


        self.display_mode = "endocardial"
        self.update_mask_title("Binary endocardial mask")
        self.cine_mask = self.endocardial_mask
        self.mask_slice = self.cine_mask[:, :, self.tidx, self.zidx]
        self.redraw_mask()


        self.slider["tidx"].setRange(self.tmin, self.tmax)
        self.slider["zidx"].setRange(self.zmin, self.zmax)
        self.spinbox["tidx"].setRange(self.tmin, self.tmax)
        self.spinbox["zidx"].setRange(self.zmin, self.zmax)

        self.spinbox["tmin"].setRange(0, self.tmax-1)
        self.spinbox["zmin"].setRange(0, self.zmax-1)
        self.spinbox["tmax"].setRange(self.tmin+1, self.tslicenum-1)
        self.spinbox["zmax"].setRange(self.zmin+1, self.zslicenum-1)

        self.slider["tidx"].setValue(self.tidx)
        self.slider["zidx"].setValue(self.zidx)

        self.spinbox["tidx"].setValue(self.tidx)
        self.spinbox["zidx"].setValue(self.zidx)

        self.spinbox["tmin"].setValue(0)
        self.spinbox["zmin"].setValue(0)
        self.spinbox["tmax"].setValue(self.tmax)
        self.spinbox["zmax"].setValue(self.zmax)

        # update slider titles to fit current slicenums
        self.grid.removeWidget(self.title["tslice"])
        self.grid.removeWidget(self.title["zslice"])
        self.title["tslice"].deleteLater()
        self.title["zslice"].deleteLater()
        del self.title["tslice"]
        del self.title["zslice"]

        # set new titles
        self.title["tslice"] = QtGui.QLabel("Time slice [0, {}): ".format(self.tslicenum))
        self.title["tslice"].setStyleSheet("font: bold")
        self.title["tslice"].setAlignment(QtCore.Qt.AlignCenter)

        self.title["zslice"] = QtGui.QLabel("Z slice [0, {}): ".format(self.zslicenum))
        self.title["zslice"].setStyleSheet("font: bold")
        self.title["zslice"].setAlignment(QtCore.Qt.AlignCenter)

        # add title widgets
        self.grid.addWidget(self.title["tslice"], 7, 0)
        self.grid.addWidget(self.title["zslice"], 8, 0)

        # update cc settings
        self.cc.reset_setting()


    def update_image_title(self, title):
        # update slider titles to fit current slicenums
        self.grid.removeWidget(self.title["cineimg"])
        self.title["cineimg"].deleteLater()
        del self.title["cineimg"]

        # set new titles
        self.title["cineimg"] = QtGui.QLabel(title)
        self.title["cineimg"].setStyleSheet("font: bold")
        self.title["cineimg"].setAlignment(QtCore.Qt.AlignCenter)

        # add title widgets
        self.grid.addWidget(self.title["cineimg"], 0, 0, 2, 2)


    def update_mask_title(self, title):
        self.grid.removeWidget(self.title["maskimg"])
        self.title["maskimg"].deleteLater()
        del self.title["maskimg"]

        # set new titles
        self.title["maskimg"] = QtGui.QLabel(title)
        self.title["maskimg"].setStyleSheet("font: bold")
        self.title["maskimg"].setAlignment(QtCore.Qt.AlignCenter)

        # add title widgets
        self.grid.addWidget(self.title["maskimg"], 0, 2, 2, 2)


    def update_subject_idx(self, idx):
        if self.loadflag != True:
            return

        self.subject_idx = idx
        self.cc.update_subject_idx(idx)


    def update_tidx(self, value):
        if self.loadflag != True:
            return
        self.tidx = value
        self.update_slice()

        self.cc.update_index(self.tidx, self.zidx)
        self.redraw_img()


    def update_zidx(self, value):
        if self.loadflag != True:
            return
        self.zidx = value
        self.update_slice()

        self.cc.update_index(self.tidx, self.zidx)
        self.redraw_img()


    def update_tmin(self, value):
        if self.loadflag != True:
            return
        self.tmin = value
        self.spinbox["tmin"].setValue(value)
        self.spinbox["tmin"].setRange(0, self.tmax-1)

        self.slider["tidx"].setRange(self.tmin, self.tmax)
        self.spinbox["tidx"].setRange(self.tmin, self.tmax)

        self.cc.update_tlimit(self.tmin, self.tmax)


    def update_tmax(self, value):
        if self.loadflag != True:
            return
        self.tmax = value
        self.spinbox["tmax"].setValue(value)
        self.spinbox["tmax"].setRange(self.tmin+1, self.tslicenum-1)

        self.slider["tidx"].setRange(self.tmin, self.tmax)
        self.spinbox["tidx"].setRange(self.tmin, self.tmax)

        self.cc.update_tlimit(self.tmin, self.tmax)


    def update_zmin(self, value):
        if self.loadflag != True:
            return
        self.zmin = value
        self.spinbox["zmin"].setValue(value)
        self.spinbox["zmin"].setRange(0, self.zmax-1)

        self.slider["zidx"].setRange(self.zmin, self.zmax)
        self.spinbox["zidx"].setRange(self.zmin, self.zmax)

        self.cc.update_zlimit(self.zmin, self.zmax)


    def update_zmax(self, value):
        if self.loadflag != True:
            return
        self.zmax = value
        self.spinbox["zmax"].setValue(value)
        self.spinbox["zmax"].setRange(self.zmin+1, self.zslicenum-1)

        self.slider["zidx"].setRange(self.zmin, self.zmax)
        self.spinbox["zidx"].setRange(self.zmin, self.zmax)

        self.cc.update_zlimit(self.zmin, self.zmax)


    def update_slice(self):
        self.img_slice = self.cine_img[:, :, self.tidx, self.zidx]
        self.mask_slice = self.cine_mask[:, :, self.tidx, self.zidx]


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
        self.cine_img = algorithm.resize(self.cine_img, mode=256)

        self.img_slice = self.cine_img[:, :, 0, 0]

        if(self.endocardial_mask != None): del self.endocardial_mask
        if(self.epicardial_mask != None): del self.epicardial_mask
        if(self.myocardial_mask != None): del self.myocardial_mask

        self.endocardial_mask = np.zeros(self.cine_img.shape)
        self.epicardial_mask = np.zeros(self.cine_img.shape)
        self.myocardial_mask = np.zeros(self.cine_img.shape)

        self.reset_setting()
        self.loadflag = True
        
        '''
        osname = platform.system()
        is_windows = (osname.lower().find("win") > -1)
        if is_windows:
            subject_idx = dirname.split('\\')[-1]
        else:
            subject_idx = dirname.split('/')[-1]
        '''
        subject_idx = dirname.replace('\\','/').split('/')[-1] 
        self.update_subject_idx(subject_idx)

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
        if self.loadflag == False:
            return

        fname = io.save_file_dialog()
        data = io.init_mask_io_format()

        tmax = self.cine_img.shape[2]
        zmax = self.cine_img.shape[3]

        COM = []
        frame_idx = []
        slice_idx = []

        emask = []
        boxmask = []
        cinedata = []
        subject_idx = []

        cnt = 0
        for t in range(tmax):
            for z in range(zmax):
                if self.cc.cropped[t][z]:
                    cnt += 1
                    ori_img = deepcopy(self.cine_img[:,:,t,z])
                    bmask = deepcopy(self.endocardial_mask[:,:,t,z])
                    com = center_of_mass(bmask)
                    xmask = algorithm.c2bmask(bmask, com)

                    COM.append(com)
                    frame_idx.append(t)
                    slice_idx.append(z)
                    emask.append(bmask)
                    cinedata.append(ori_img)
                    boxmask.append(xmask)
                    subject_idx.append(self.subject_idx)

        data["box_mask"] = boxmask
        data["cine_data"] = cinedata
        data["COM"] = COM
        data["endocardial_mask"] = emask
        data["frame_idx"] = frame_idx
        data["slice_idx"] = slice_idx
        data["subject_idx"] = subject_idx

        with open(fname, 'wb') as output:
            pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

        print("data saved at :", fname)


    def show_endocardium(self):
        if self.loadflag != True:
            return

        self.display_mode = "endocardial"
        self.update_mask_title("Binary endocardial mask\n")
        print("\nDisplaying endocardium")

        self.cine_mask = self.endocardial_mask
        self.mask_slice = self.cine_mask[:, :, self.tidx, self.zidx]

        self.redraw_mask()
        self.cc.switch2endo()


    def show_epicardium(self):
        if self.loadflag != True:
            return

        self.display_mode = "epicardial"
        self.update_mask_title("Binary epicardial mask\n")
        print("\nDisplaying epicardium")

        self.cine_mask = self.epicardial_mask
        self.mask_slice = self.cine_mask[:, :, self.tidx, self.zidx]

        self.redraw_mask()
        self.cc.switch2epic()


    def show_myocardium(self):
        if self.loadflag != True:
            return

        self.display_mode = "myocardial"
        self.update_mask_title("Binary myocardial mask\n")
        self.update_image_title("Cine image\n")
        print("\nDisplaying myocardium")

        self.cine_mask = self.myocardial_mask
        self.mask_slice = self.cine_mask[:, :, self.tidx, self.zidx]

        self.redraw_mask()
        self.cc.switch2myo()


    def singular_endocardial_detection(self):
        if self.loadflag != True:
            return

        print("\nInitializing singular endocardial detection..... ", end="")
        self.cc.set_singular()
        self.cc.switch2seed()


    def multiple_endocardial_detection(self):
        if self.loadflag != True:
            return

        print("\nInitializing multiple endocardial detection..... ", end="")
        self.cc.set_multiple()
        self.cc.switch2seed()


    def singular_epicardial_detection(self):
        if self.loadflag != True:
            return

        print("disabled")
        return
        print("\nInitializing singular epicardial detection..... ", end="")

        # check if mask set.
        if self.cc.cropped[self.tidx][self.zidx] != True:
            print("endocardinal mask must be set")
            return

        print("complete")

        self.cc.singular_epicardial_detection()

        # self.cc.switch2epic()


    def multiple_epicardial_detection(self):
        if self.loadflag != True:
            return

        print("disabled")
        return

        print("\nInitializing multiple epicardial detection..... ", end="")
        print("complete")

        self.cc.multiple_epicardial_detection()



class ClickerClass(object):
    _title = {"plot": "LEFT: add landmark, RIGHT: delete landmark\n"
                    "Press 'm' to switch modes",
              "connect": "'i': insert, 't': toggle vertex, 'RIGHT': delete\n"
                     "Press 'Enter' to crop, 'm' to switch modes",
              "seed": "LEFT: select seed\n"
                      "Press 'Enter' to complete",
              "mask": "Binary mask\n",
              "init": "Cine image\n"}

    _tidx, _zidx = 0, 0 # active slice index
    _tmin, _tmax = 0, 100 # index range [_tmin, _tmax] for detection
    _zmin, _zmax = 0, 100 # index range [_zmin, _zmax] for detection

    _subject_idx = ""
    _loadflag = False
    _detectionflag = None
    _epsilon = 5 # cursor sensitivity in pixels
    _modes = "init"
    # True: Place landmarks, False: Connect landmarks

    _alpha = 0.30
    _ind = None # active vertex
    _seed = None # seed point for endocardial detection
    _tseed = [] # temporary seed container

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
    position = None # active position set

    endo_position = None
    epic_position = None

    background = None


    def __init__(self, Window):

        self.Window = Window

        # get axis object
        self.ax1 = Window.ax1
        self.ax2 = Window.ax2

        # get figure object
        self.fig1 = Window.fig1
        self.fig2 = Window.fig2

        # get canvas object
        self.canvas1 = Window.canvas1
        self.canvas2 = Window.canvas2

        # quick solution for inactive key_press_event
        self.canvas1.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas1.setFocus()

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
        self.endo_position = [[[] for i in range(zl)] for j in range(tl)]
        self.epic_position = [[[] for i in range(zl)] for j in range(tl)]

        self.position = self.endo_position
        self.verts = self.position[self._tidx][self._zidx]

        # access: _seed[tl][zl]
        self._seed = [[[] for i in range(zl)] for j in range(tl)]


    def init_img(self):
        self.cine_img = self.Window.cine_img
        self._loadflag = True
        self.cropped = np.zeros((self.cine_img.shape[2], self.cine_img.shape[3]))


    def init_mask(self):
        self.cine_mask = self.Window.cine_mask
        self.mask_slice = self.cine_mask[:, :, self._tidx, self._zidx]


    def reset_setting(self):
        self._modes = "plot"
        self.Window.update_image_title(self._title[self._modes])

        self.cine_mask = None
        self.mask_slice = None

        self._tidx, self._zidx = self.Window.tidx, self.Window.zidx
        self._tmin, self._tmax = self.Window.tmin, self.Window.tmax
        self._zmin, self._zmax = self.Window.zmin, self.Window.zmax

        self._loadflag = True
        self._detectionflag = None

        self.init_mask()
        self.init_img()
        self.init_vertex()


    def switch2endo(self):
        self.position = self.endo_position
        self.verts = self.position[self._tidx][self._zidx]
        self.init_mask()

        if self._modes == "connect":
            if len(self.verts) <= 1:
                self.switch_modes()
            else:
                self.poly.xy = np.array(self.verts[:])
                self.line.set_data(zip(*self.poly.xy))
        elif self._modes == "plot":
            self.replot()
            self.poly.xy = [(0, 0)]

        if self._modes != "seed":
            self.redraw()
            self.canvas1.draw()


    def switch2epic(self):
        self.position = self.epic_position
        self.verts = self.position[self._tidx][self._zidx]
        self.init_mask()

        if self._modes == "connect":
            if len(self.verts) <= 1:
                self.switch_modes()
            else:
                self.poly.xy = np.array(self.verts[:])
                self.line.set_data(zip(*self.poly.xy))
        elif self._modes == "plot":
            self.replot()
            self.poly.xy = [(0, 0)]

        if self._modes != "seed":
            self.redraw()
            self.canvas1.draw()


    def switch2myo(self):
        self.cine_mask = self.Window.cine_mask
        self.position = []
        self.verts = []

        self.init_mask()
        if self._modes == "connect":
            self.poly.xy = [(0, 0)]
            self.line.set_data(zip(*self.poly.xy))
        elif self._modes == "plot":
            self.replot()
            self.poly.xy = [(0, 0)]

        if self._modes != "seed":
            self.redraw()
            self.canvas1.draw()


    def update_subject_idx(self, idx):
        self._subject_idx = idx


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
            if(len(self._tseed) == 1):
                verts = self._tseed
            else:
                verts = self._seed[self._tidx][self._zidx]
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
        if self.Window.display_mode == "myocardial":
            self.verts = []
        else:
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
        if self.Window.display_mode == "myocardial": return
        if self._modes == "seed": return

        if self._modes == "plot":
            self.switch2poly()
        elif self._modes == "connect":
            self.switch2plot()


    def switch2seed(self):
        self._modes = "seed"
        self.Window.update_image_title(self._title[self._modes])
        if self.Window.display_mode != "endocardial":
            self.Window.show_endocardium()

        # access: _seed[tl][zl]
        # self._seed = [[[] for i in range(zl)] for j in range(tl)]
        self._tseed.clear()
        if len(self._seed[self._tidx][self._zidx]) == 1:
            self._tseed.append((self._seed[self._tidx][self._zidx][0][0],\
                                self._seed[self._tidx][self._zidx][0][1]))

        # clears the existing plot
        self.replot()
        if self.poly:
            self.poly.xy = [(0, 0)]

        self.canvas1.draw()


    def switch2plot(self):
        self._modes = "plot"
        self.Window.update_image_title(self._title[self._modes])

        self.replot()
        if self.poly:
            self.poly.xy = [(0, 0)]


    def switch2poly(self):
        if len(self.verts) == 0:
            return

        self._modes = "connect"
        self.Window.update_image_title(self._title[self._modes])

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
        if not event.inaxes: return
        if not self._loadflag: return
        if self.Window.display_mode == "myocardial": return

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
        if self.Window.display_mode == "myocardial": return

        self._ind = None


    def scroll_callback(self, event):
        if not self._loadflag: return
        if self.Window.display_mode == "myocardial": return
        if not self._modes == "connect": return

        if event.button == 'up':
            if self._alpha < 1.00:
                self._alpha += 0.05
        elif event.button == 'down':
            self._alpha -= 0.05
            if self._alpha <= 0.00:
                self._alpha = 0.00

        self.poly.set_alpha(self._alpha)
        self.canvas1.draw()


    def motion_notify_callback(self, event):
        # on mouse movement
        if self._ind is None: return
        if self._modes == "seed": return
        if not self._loadflag: return
        if event.button != 1: return
        if not event.inaxes: return
        if self.Window.display_mode == "myocardial": return

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
        if self.Window.display_mode == "myocardial": return

        if event.key == 't':
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
                    self.mask_slice[y][x] = 1
                else:
                    self.mask_slice[y][x] = 0

        if(self.Window.display_mode == "endocardial"):
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
            # verts = self._seed[self._tidx][self._zidx]
            verts = self._tseed
            verts.clear()
        else:
            verts = self.verts
        verts.append((int(event.xdata), int(event.ydata)))


    def insert_vertex(self, event):
        if not self._modes == "connect": return
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
        if len(self._tseed) == 0:
            return

        print("complete",
              "\nseed set at",
              (self._tseed[0][0],self._tseed[0][1]),
              "\nsegmenting mask..... ", end="")

        self.mask_slice[:, :] = \
                    algorithm.endocardial_detection(
                    self.cine_img[:, :, self._tidx, self._zidx], \
                    (self._tseed[0][0], self._tseed[0][1]))[:, :]

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

            self._seed[self._tidx][self._zidx].clear()
            self._seed[self._tidx][self._zidx].append(\
                      (self._tseed[0][0], self._tseed[0][1]))
            print("Seed updated")

            self.switch2poly()
            self.poly2mask()
        else:
            print("segmentation failure")
            self.switch2plot()
            self.cropped[self._tidx][self._zidx] = False

        self.canvas1.draw()


    def multiple_endocardial_detection(self):
        if not self._modes == "seed":
            return
        if len(self._tseed) == 0:
            return

        print("complete",
              "\nseed set at", (self._tseed[0][0], \
                                self._tseed[0][1]),
              "\nsegmenting mask..... ", end="")

        queue = []
        epsilon = 15 #Manhattan distance
        dirx = [3,3,3,-3,-3,-3,0,0]
        diry = [0,3,-3,0,3,-3,3,-3]
        tot_cnt = 0
        success_cnt = 0
        failed_index = []

        for t in range(self._tmin, self._tmax):

            for z in range(self._zmin, self._zmax):
                flag = False
                tot_cnt += 1

                xseed, yseed = self._tseed[0][0], self._tseed[0][1]
                self.mask_slice = self.cine_mask[:, :, t, z]
                visited = np.zeros((self.cine_mask.shape[0],\
                                    self.cine_mask.shape[1]))
                queue.append((self._tseed[0][0], self._tseed[0][1]))

                while queue:
                    center = queue.pop(0)

                    if not visited[center[0]][center[1]]:
                        visited[center[0]][center[1]] = True

                        self.mask_slice[:, :] = \
                            algorithm.endocardial_detection(
                            self.cine_img[:, :, t, z], \
                            (center[0], center[1]))[:, :]

                        if int(np.sum(self.mask_slice)) != 0:
                            success_cnt += 1
                            flag = True
                            self._seed[t][z].clear()
                            self._seed[t][z].append((center[0], center[1]))
                            self._tseed.clear()
                            self._tseed.append((center[0],center[1]))
                            self.cropped[t][z] = True
                            del visited
                            queue.clear()
                            break;

                        for i in range(8):
                            if ((abs(center[0]+dirx[i]-self._tseed[0][0])+\
                                 abs(center[1]+diry[i]-self._tseed[0][1]))<epsilon):
                                queue.append(((center[0]+dirx[i]),(center[1]+diry[i])))
                if(not flag):
                    failed_index.append((z, t))

        queue.clear()
        print("complete")
        print("calculating hull.....", end="")
        for t in range(self._tmin, self._tmax):

            for z in range(self._zmin, self._zmax):
                if self.cropped[t][z] != True:
                    continue
                self.mask_slice = self.cine_mask[:, :, t, z]

                try:
                    self.position[t][z] = algorithm.convex_hull(self.mask_slice)
                except:
                    print("failed on ({}, {})".format(t, z))
                    continue

                self.poly.xy = np.array(self.position[t][z])

                # sub-window vertices, reduced search space
                xcenter = self._seed[t][z][0][0]
                ycenter = self._seed[t][z][0][1]
                xllim, xulim = xcenter-50, xcenter+50
                yllim, yulim = ycenter-50, ycenter+50

                if xllim < 0: xllim = 0
                if xulim > self.mask_slice.shape[0]: xulim = self.mask_slice.shape[0]
                if yllim < 0: yllim = 0
                if yulim > self.mask_slice.shape[1]: yulim = self.mask_slice.shape[1]

                for x in range(xllim, xulim):
                    for y in range(yllim, yulim):
                        if self.poly.get_path().contains_point((x,y)):
                            self.mask_slice[y][x] = 1
                        else:
                            self.mask_slice[y][x] = 0

        print(" complete")
        print("Successfully segmented {} slices out of {}".format(success_cnt, tot_cnt))
        if(success_cnt != tot_cnt):
            print("failed on: ")
            print(failed_index)
        del failed_index

        self.verts = self.position[self._tidx][self._zidx]
        self.mask_slice = self.cine_mask[:, :, self._tidx, self._zidx]

        self.ax2.imshow(self.mask_slice, cmap=plt.cm.gray)

        if len(self.verts) <= 2:
            self.switch2plot()
        else:
            self.switch2poly()

        self.canvas1.draw()
        self.canvas2.draw()


    def singular_epicardial_detection(self):
        print("using endocardial mask as seed")
        print("segmenting mask..... ", end="")

        epi_mask = self.Window.epicardial_mask
        endo_mask = self.Window.endocardial_mask

        self.position = self.epic_position
        self.verts = self.position[self._tidx][self._zidx]

        epi_slice = epi_mask[:, :, self._tidx, self._zidx]
        endo_slice = endo_mask[:, :, self._tidx, self._zidx]

        epi_slice[:, :] = \
                    algorithm.epicardial_detection(
                    self.cine_img[:, :, self._tidx, self._zidx], \
                    endo_slice)[:, :]

        # if valid mask
        if int(np.sum(epi_slice)) != 0:

            print("complete")
            print("calculating hull..... ", end="")

            try:
                self.verts[:] = algorithm.convex_hull(epi_slice)
            except:
                print("failure")
                return

            self.poly.xy = np.array(self.position[self._tidx][self._zidx])
            for x in range(epi_slice.shape[1]):
                for y in range(epi_slice.shape[0]):
                    if self.poly.get_path().contains_point((x,y)):
                        epi_slice[y][x] = 1
                    else:
                        epi_slice[y][x] = 0

            print("complete")
            self.Window.show_epicardium()


    def multiple_epicardial_detection(self):
        pass


    def set_singular(self):
        self._detectionflag = "singular"


    def set_multiple(self):
        self._detectionflag = "multiple"


