import sys
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
    def __init__(self,gui,parent=None):
	super(MplGrapher, self).__init__(parent)
	self.initFigure()
	self.gui = gui

    def initFigure(self):
	self.figure = Figure()
	self.canvas = FigureCanvas(self.figure)
	self.plotContainer = {}
	self.navbar = NavigationToolbar(self.canvas,self)
	self.layout = QVBoxLayout()
	self.layout.addWidget(self.navbar)
	self.layout.addWidget(self.canvas)
	self.setLayout(self.layout)

    # Sets up subplot grid length and width...adds plot to container
    def adjustSubplots(self,w,h,p,d=False):
	if d == True:
	    self.plotContainer[p-1] = self.figure.add_subplot(w,h,p,projection='3d')
	else:
	    self.plotContainer[p-1] = self.figure.add_subplot(w,h,p)


    # Sets up labels and axis' ranges, then plots
    def setGraphParams(self,path,plot,file_,xRange,zLabel,zRange):
        self.plotContainer[plot].clear()
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
	    data = self.stringToFloat(data)
	    if len(data) == self.gui.length2:
		x = xRange.split("-")
		try:
		    self.computeRanges(plot,data,x,xRange)
		except AttributeError: pass
		except ValueError: pass
	    self.plotContainer[plot].plot(data, 'b-')
	else:
	    self.plot3D(_file,plot,xRange,zLabel,zRange)
        try: self.figure.canvas.draw()
        except ValueError: pass

    def computeRanges(self, plot, data, x, xRange):
	try:
	    if 'x range' in xRange:
		self.plotContainer[plot].axis([0, self.gui.timeSteps,
				    float(min(data)), float(max(data))])
	    else:
		self.plotContainer[plot].axis([floor(float(x[0])), ceil(float(x[1])),
			  float(min(data)), float(max(data))])
	except NameError:
	    print "NameError"

    # Helper function
    def stringToFloat(self,batch):
	newList = []
	for string in batch:
	    string = string.strip("\n")
	    newList.append(float(string))
	return newList

    # Plots in 3D
    def plot3D(self,file_,plot,xRange,zLabel,zRange):
	try:
	    with open(file_, 'r') as f:
		data = f.readlines()
	    data = self.stringToFloat(data)
	    X = np.arange(0,self.gui.length1)
	    Y = np.arange(0,(self.gui.timeSteps))
	    Z = np.reshape(data, (self.gui.length1,self.gui.timeSteps))
	    X,Y = np.meshgrid(Y,X)
	    surf = self.plotContainer[plot].plot_surface(X,Y,Z,linewidth=0.1,cmap=cm.jet)
	    surf.set_clim([np.min(Z),np.max(Z)])
	    self.plotContainer[plot].set_zlabel(zLabel)
	    z = zRange.split("-")
	except ValueError:
	    print "this is that ValueError"

    def getFig(self):
	return self
