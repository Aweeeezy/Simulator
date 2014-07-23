import sys
import matplotlib.pyplot as plt
import numpy as np
from PySide.QtGui import *
from PySide.QtCore import *
import matplotlib
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib import cm
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from math import floor, ceil

# FigureCanvas to be embedded in PySide GUI
class MplGrapher(QWidget):
    def __init__(self,parent=None):
	super(MplGrapher, self).__init__(parent)
	self.initFigure()

    def initFigure(self):
	self.figure = Figure()
	self.canvas = FigureCanvas(self.figure)
	self.plt = self.figure.add_subplot(111)
	self.navbar = NavigationToolbar(self.canvas,self)
	self.layout = QVBoxLayout()
	self.layout.addWidget(self.navbar)
	self.layout.addWidget(self.canvas)
	self.setLayout(self.layout)

    # Sets up labels and axis' ranges
    def setGraphParams(self,path,file_,xRange,zLabel,zRange):
        self.plt.clear()
	if "\n" in path: # Used if opening from .sim
	    _file = path[:-1]+"/"+file_[:-1]
	    xRange = xRange[:-1]
	    zLabel = zLabel[:-1]
	    zRange = zRange[:-1]
	else:
	    _file = path+"/"+file_
	if "none" in zLabel:
	    with open(_file, 'r') as f:
	       data = f.readlines()
	    self.plt.plot(data, 'b-')
	    x = xRange.split("-")
	    try:
		self.computeRanges(data, x, xRange)
	    except AttributeError: pass
	    except ValueError: pass
	else:
	    self.plot3D(_file,xRange,zLabel,zRange)
        try: self.figure.canvas.draw()
        except ValueError: pass

    # Until I can examine a working .c file that generates data, I won't be
    # able to abstract this functionality
    def plot3D(self,file_,xRange,zLabel,zRange):
	try:
            _file = "/Users/aweeeezy/bin/ivry/instrumental_discrete/surface_plot/w_d1_A.txt"
            with open(_file, 'r') as f:
                data = f.readline()
            line  = data.split(' ')
            data = []
            for x in range(10000):
                data.append(float(line[x]))
            X = np.arange(0,100)
            Y = np.arange(0,100)
            Z = np.reshape(data, (100,100))
            X,Y = np.meshgrid(X,Y)
            self.plt.plot_surface(X,Y,Z,cmap=cm.jet)
            self.plt.set_zlabel(zLabel)
            z = zRange.split("-")
	except ValueError:
	    print "this is that ValueError"

    def computeRanges(self, data, x, xRange):
	try:
	    if 'x range' in xRange:
		self.plt.axis([0, len(data), floor(float(min(data))),
					      ceil(float(max(data)))])
	    else:
		self.plt.axis([floor(float(x[0])), ceil(float(x[1])),
			  floor(float(min(data))), ceil(float(max(data)))])
	except NameError:
	    print "NameError"

    def getFig(self):
	return self
