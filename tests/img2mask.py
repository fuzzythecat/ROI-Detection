# Script Name		: img2mask.py
# Author			: Younjoon Chung
# Description		: Wrapper + Clicker combined
# Details of Change :

import numpy as np
from matplotlib import use
use("Qt5Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from matplotlib.mlab import dist_point_to_segment
from copy import deepcopy

import warnings


class ClickerClass(object):

    showverts = True
    epsilon = 5
    modes = True # True: Place Landmarks False: Connect Landmarks
    title = {True: "LEFT: add landmark, RIGHT: delete landmark\n"
                    "Press 'm' to switch modes",
             False: "'i': insert, 't': toggle vertex, 'RIGHT': delete\n"
                     "Press 'Enter' to crop, 'm' to switch modes"}
    number_of_verticies_for_calib = 20
    alpha = 0.30

    def __init__(self, img, ax1, ax2, **kwargs):

        self.subplotnum = 0
        print("initiating")
        self.ax1 = ax1
        self.ax2 = ax2
        self.canvas1 = self.ax1.get_figure().canvas
        # self.canvas2 = self.ax2.get_figure().canvas

        self.img = img
        self.mask = kwargs.pop('mask', None)
        self.verts = kwargs.pop('position', [])

        self.covered_pixels = []

        self._ind = None # the active vertex

        self.plot = ax1.plot([], [], marker='o', markerfacecolor='b',
                              linestyle='none', markersize = 5)[0]
        self.line = None
        self.poly = None

        self.set_modes()
        self.connect_activity()

        self.background = None

        plt.show()

    def set_modes(self):
        if self.img is None:
            raise AttributeError("User must provide numpy.ndarray image")
        if not self.verts:
            self.verts = []

        if len(self.verts) > 0:
            self.plot_init()
            self.switch_modes()
            if self.mask is not None:
                self.update_mask()
        elif self.mask is not None:
            self.mask_init()
        else:
            self.plot_init()

        if self.mask is None:
            self.mask = self.img
        self.canvas1.draw()

    def mask_init(self):
        self.auto_calibration()
        self.poly_init()
        self.update_mask()

    def plot_init(self):
        self.ax1.set_title(self.title[True])
        self.modes = True
        self.replot()

    def poly_init(self):
        self.ax1.set_title(self.title[False])
        self.modes = False
        self.ax1.set_ylabel("Alpha: %.2f" % self.alpha)

        if self.poly is None:
            self.create_polygon()
        else:
            self.poly.xy = np.array(self.verts[:])
            self.line.set_data(zip(*self.poly.xy))
        self.plot.set_data([],[])

    def create_polygon(self):
        self.poly = Polygon(self.verts,
                            animated = True, alpha = self.alpha)
        self.ax1.add_patch(self.poly)

        x, y = zip(*self.poly.xy)
        self.line = Line2D(x, y, marker='o',
                           markerfacecolor='r', animated=True, markersize = 5)
        self.ax1.add_line(self.line)

    def switch_modes(self):
        if not self.showverts:
            return

        if self.modes:
            self.switch2poly()
        else:
            self.switch2plot()

    def switch2plot(self):
        self.modes = True
        self.ax1.set_title(self.title[True])
        self.ax1.set_ylabel("")

        self.replot()
        if self.poly:
            self.poly.xy = [(0, 0)]

    def switch2poly(self):
        if len(self.verts) <= 1:
                raise AttributeError("Requires 2 or more vertices to draw region")
        self.modes = False
        self.ax1.set_title(self.title[False])
        self.ax1.set_ylabel("Alpha: %.2f" % self.alpha)

        #self.verts_sort()
        if self.poly is None:
            self.create_polygon()
        else:
            self.poly.xy = np.array(self.verts[:])
            self.line.set_data(zip(*self.poly.xy))
        self.plot.set_data([],[])

    def connect_activity(self):
        self.canvas1.mpl_connect('button_press_event',  self.button_press_callback)
        self.canvas1.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas1.mpl_connect('scroll_event', self.scroll_callback)
        self.canvas1.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas1.mpl_connect('draw_event', self.draw_callback)
        self.canvas1.mpl_connect('key_press_event', self.key_press_callback)


    def button_press_callback(self, event):
        if not self.showverts: return
        if not event.inaxes: return

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
        if not self.showverts:
            return

        self._ind = None

    def scroll_callback(self, event):
        if not self.showverts: return
        if self.modes: return

        if event.button == 'up':
            if self.alpha < 1.00:
                self.alpha += 0.05
        elif event.button == 'down':
            self.alpha -= 0.05
            if self.alpha <= 0.00:
                self.alpha = 0.00

        self.ax1.set_ylabel("Alpha: %.2f" % self.alpha)
        self.poly.set_alpha(self.alpha)
        self.canvas1.draw()

    def motion_notify_callback(self, event):
        """on mouse movement"""
        if not self.showverts: return
        if not event.inaxes: return
        if event.button != 1: return
        if self._ind is None: return

        self.move_vertex_to(event)
        self.canvas1.restore_region(self.background)
        self.redraw()

    def draw_callback(self, event):
        if not self.modes:
            self.background = self.canvas1.copy_from_bbox(self.ax1.bbox)
            self.redraw()

    def key_press_callback(self, event):
        if not event.inaxes:
            return

        if event.key == 't':
            self.switch_vis()
        elif event.key == 'm':
            self.switch_modes()
        elif event.key == 'i':
            self.insert_vertex(event)
        elif event.key == 'enter':
            self.poly2mask()
        elif event.key == 'c':
            self.mask_init()

        self.canvas1.draw()

    def poly2mask(self):
        if self.modes: return
        # if not self.verts: return

        #self.covered_pixels = []
        for x in range(self.img.shape[1]):
            for y in range(self.img.shape[0]):
                if self.poly.get_path().contains_point((x,y)):
                    #self.covered_pixels.append((x,y))
                    self.mask[y][x] = 1
                else:
                    self.mask[y][x] = 0

        #self.update_mask()

        figi = plt.figure()
        ax = figi.add_subplot(1, 1, self.subplotnum+1)
        ax.imshow(self.mask, cmap=plt.cm.gray)
        figi.show()

        '''
        fig2, ax2 = plt.subplots()
        ax2.imshow(self.mask, cmap = plt.cm.gray)

        plt.ion()
        plt.pause(2)
        plt.close(fig2)
        print ("mask updated")

        plt.close(self.ax1.get_figure())
        '''

    '''
    def update_mask(self):
        self.ax2.imshow(self.mask, cmap = plt.cm.gray)
        self.canvas2.draw()
    '''

    def switch_vis(self):
        if self.modes:
            return

        self.showverts = not self.showverts
        if not self.showverts:
            self.line.set_marker(None)
            self._ind = None
        else:
            self.line.set_marker('o')

    def add_vertex(self, event):
        # Adds a point at cursor
        if not self.modes:
            return

        if self.modes:
            self.verts.append((event.xdata, event.ydata))

    def insert_vertex(self, event):
        if self.modes: return
        if not self.showverts: return

        p = event.xdata, event.ydata  # display coords
        mod = len(self.verts)
        for i in range(len(self.verts)):
            s0 = self.verts[i%mod]
            s1 = self.verts[(i + 1)%mod]
            d = dist_point_to_segment(p, s0, s1)
            if d <= 5:
                self.poly.xy = np.array(
                    list(self.poly.xy[:i+1]) +
                    [(event.xdata, event.ydata)] +
                    list(self.poly.xy[i+1:]))
                self.line.set_data(zip(*self.poly.xy))
                self.verts = [tup for i, tup in enumerate(self.poly.xy) if i != len(self.poly.xy)-1]
                break

    def remove_vertex(self, event):
        # Removes the point closest to the cursor
        index = self._ind
        if not index is None:
            del self.verts[index]
            if not self.modes:
                if len(self.verts) <= 1:
                    self.switch_modes()
                else:
                    self.poly.xy = [x for x in self.verts]
                    self.line.set_data(zip(*self.poly.xy))

    def get_nearest_vertex_idx(self, event):
        if len(self.verts) > 0:
            distance = [(v[0] - event.xdata) ** 2 +
                        (v[1] - event.ydata) ** 2 for v in self.verts]
            if np.sqrt(min(distance)) <= self.epsilon:
                return distance.index(min(distance))
        return None

    def move_vertex_to(self, event):
        x, y = event.xdata, event.ydata

        self.poly.xy[self._ind] = x, y
        self.verts[self._ind] = x, y
        if self._ind == 0:
            self.poly.xy[-1] = self.poly.xy[self._ind]
        self.line.set_data(zip(*self.poly.xy))

    def replot(self):
        # Apply the changes to the vertices / canvas
        if len(self.verts) > 0:
            x, y = zip(*self.verts)
        else:
            x, y = [], []

        if self.modes:
            self.plot.set_xdata(x)
            self.plot.set_ydata(y)

    def redraw(self):
        self.ax1.draw_artist(self.poly)
        self.ax1.draw_artist(self.line)
        self.canvas1.blit(self.ax1.bbox)

    def calculate_accuracy(self, xs, ys):
        wanted = 0.
        unwanted = 0.

        verts = list(zip(xs, ys))
        poly = Polygon(verts)

        for x in range(self.img.shape[1]):
            for y in range(self.img.shape[0]):
                if poly.get_path().contains_point((x,y)):
                    if self.mask[y][x] == 1:
                        wanted += 1
                    else:
                        unwanted += 1

        return (wanted-unwanted)/(wanted+unwanted)

    def set_bounds(self):
        xl, xh = self.mask.shape[1], 0
        yl, yh = self.mask.shape[0], 0

        for x in range(self.mask.shape[1]):
            for y in range(self.mask.shape[0]):
                if self.mask[y][x] == 1:
                    if y > yh: yh = y
                    if y < yl: yl = y
                    if x > xh: xh = x
                    if x < xl: xl = x

        return int((xl+xh)/2), int((yl+yh)/2)

    def auto_calibration(self):
        cnt = 0
        thr = 0

        xmid, ymid = self.set_bounds()
        xmargin = int(self.mask.shape[1]/10)
        ymargin = int(self.mask.shape[0]/10)

        xl = xmid - xmargin; xh = xmid + xmargin
        yl = ymid - ymargin; yh = ymid + ymargin

        for x in range(xl + xmargin, xh):
            for y in range(yl + ymargin, yh):
                if self.mask[y][x] == 1:
                    cnt += 1
                    center = [(x, y)]
                    xs, ys = self.calibrate(center = center)
                    acc = self.calculate_accuracy(xs, ys)
                    if acc > thr:
                        thr = acc
                        #print(thr)
                        self.verts = list(zip(xs, ys))
                    if cnt > 5:
                        break
            if cnt > 5:
                break

    def calibrate(self, **kwargs):

        img = kwargs.pop("img", self.mask)
        center = kwargs.pop("center")

        theta = np.arange(0, 2*np.pi, (1/(self.number_of_verticies_for_calib/2))*np.pi)
        xs = np.cos(theta)
        ys = np.sin(theta)

        for i in range(len(xs)):
            x, y = xs[i], ys[i]
            for r in range(10000):
                if center[0][0] + r*x >= img.shape[1] or \
                   center[0][0] + r*x < 0:
                    break
                if center[0][1] + r*y >= img.shape[0] or \
                   center[0][1] + r*y < 0:
                    break

                if img[center[0][1] + r*y][center[0][0] + r*x] != 0:
                    xs[i] = center[0][0] + r*x
                    ys[i] = center[0][1] + r*y

        return xs, ys

  #temporary version
    def verts_sort(self):
        ret, arr = [], self.verts[1:]
        ret.append(self.verts[0])
        size = len(arr)
        for i in range(size):
            distance = [(v[0] - ret[i][0]) ** 2 +
                        (v[1] - ret[i][1]) ** 2 for v in arr]
            idx = distance.index(min(distance))
            ret.append(arr[idx])
            del arr[idx]
        self.verts = ret[:]


def img2mask(img, **kwargs):

    mask = None
    position = None

    if img is None:
        raise AttributeError("User must provide <numpy.ndarray> image")
    tmask = kwargs.pop("mask", None)
    tposition = kwargs.pop("position", None)
    if tmask is not None:
        mask = deepcopy(tmask)
    if tposition is not None:
        position = deepcopy(tposition)

    """define axis and corresponding figure it falls under:"""
    fig1, ax1 = plt.subplots()
    """load image onto the axis"""
    ax1.imshow(img, cmap = plt.cm.gray)

    """preventing plot from rescaling image:"""
    ax1.set_xlim([0.0, img.shape[1]])
    ax1.set_ylim([img.shape[0], 0.0])
    ax1.autoscale = False

    """preventing plot from clearing image:"""
    ax1.hold(True)

    '''
    fig2, ax2 = plt.subplots()
    ax2.set_xlim([0.0, img.shape[1]])
    ax2.set_ylim([img.shape[0], 0.0])
    ax2.autoscale = False
    ax2.hold(True)
    '''

    cc = ClickerClass(deepcopy(img), ax1, None, mask = mask, position = position)
    return cc.mask

if __name__ == '__main__':
    import sys
    sys.path.append("../utils")

    import os
    import conf
    import file_handler as fh

    zslice = 7
    tslice = 1

    warnings.filterwarnings("ignore")

    file_path = fh.get_file_paths()

    for i in range(len(file_path)):
        token = file_path[i].split('/')
        file_name = token[-1].split('.')[0]
        file_name = file_name + "_mask"

        full_path = os.path.join(conf.dir_data_mask, file_name)

        img_ori = np.load(file_path[i])
        img = img_ori[:, :, tslice, zslice]
        print("==="+file_name+"===")
        print(img.shape)
        mask = img2mask(img, mask = None)
        np.save(full_path, mask)
        print(i)
    """define axis and corresponding figure it falls under:
    fig1, ax1 = plt.subplots()
    ax1.imshow(mask, cmap = plt.cm.gray)

    ax1.set_xlim([0.0, mask.shape[1]])
    ax1.set_ylim([mask.shape[0], 0.0])
    ax1.autoscale = False

    ax1.hold(True)
    plt.show()
    """


    print("mask complete")
