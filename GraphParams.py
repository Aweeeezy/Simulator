from PySide.QtGui import *
from PySide.QtCore import *

# Widget for displaying graph options for each plot
class GraphParams(QWidget):
    def __init__(self, gui, mpl):
	super(GraphParams, self).__init__()
        self.mpl = mpl
        self.gui = gui
	self.layout = QGridLayout()
	self.trialSelects = {}
	self.xRanges = {}
	subplotLabel = QLabel("Dimensions (w,h):")
	self.subplotDimensions = QLineEdit()
	self.subplotDimensions.returnPressed.connect(self.fillBoxes)
	self.layout.addWidget(subplotLabel,0,0)
	self.layout.addWidget(self.subplotDimensions,0,1)
	self.setLayout(self.layout)
	self.show()

    # Fills layout according to styleSelect selection
    def fillBoxes(self):
	self.labels = {}
	self.boxes = {}
	self.args = self.subplotDimensions.text().split(",")
	self.width = int(self.args[0])
	self.height = int(self.args[1])
	for x in range(self.width*self.height):
	    self.mpl.adjustSubplots(self.width,self.height,x+1)
	    self.labels[x] = QLabel("DataBox for subplot %i:" % (int(x)+1))
	    self.boxes[x] = QComboBox()
	    self.gui.fillDataBoxes(self,x)
	    self.boxes[x].activated.connect(self.lambdaFunc(x))
	    self.layout.addWidget(self.labels[x],(x*2)+1,0,Qt.AlignCenter)
	    self.layout.addWidget(self.boxes[x],(x*2)+1,1,Qt.AlignCenter)
	    self.layout.addWidget(QLabel(),(x*2)+2,0)
	    self.layout.addWidget(QLabel(),(x*2)+2,1)

    def lambdaFunc(self,index):
	return lambda : self.initOptions(index)

    def otherLambda(self, index):
	return lambda : self.changeTrial(index)

    def initOptions(self,x):
	if self.gui.fileLength(self.boxes[x].currentText()) == self.gui.length2:
            self.trialSelects[x] = QLineEdit("Enter trial #")
	    self.xRanges[x] = QLineEdit("x range")
	    self.fillListRanges(self.gui.length1)
            #self.trialSelect.returnPressed.connect(self.changeTrial)
            self.trialSelects[x].returnPressed.connect(self.otherLambda(x))
            self.layout.addWidget(self.trialSelects[x],(x*2)+2,0,Qt.AlignCenter)
	    self.layout.addWidget(self.xRanges[x],(x*2)+2,1,Qt.AlignCenter)
	elif self.gui.fileLength(self.boxes[x].currentText()) == self.gui.length1:
	    w1 = self.layout.itemAtPosition((x*2)+2,0)
	    self.layout.removeWidget(w1.widget())
	    w2 = self.layout.itemAtPosition((x*2)+2,1)
	    self.layout.removeWidget(w2.widget())
	    self.layout.addWidget(QLabel(),(x*2)+2,0)
	    self.layout.addWidget(QLabel(),(x*2)+2,1)
	"""
	elif self.gui.fileLength(self.boxes[x].currentText()) == self.gui.length3:
            self.mpl.plt.cla()
            self.mpl.plt = self.mpl.figure.add_subplot(111, projection='3d')
            self.mpl.figure.canvas.draw()
            self.dataBox1 = QComboBox()
            self.zLabel = QLineEdit("z label")
            self.zRange = QLineEdit("z range")
            self.zLabel.returnPressed.connect(self.gui.plot)
            self.zRange.returnPressed.connect(self.gui.plot)
	    self.layout.addWidget(self.dataBox,1,0,Qt.AlignCenter) self.layout.addWidget(self.zLabel,2,0)
	    self.layout.addWidget(self.zRange,2,1)
	"""

    # Support method for Time Plot implementations
    def changeTrial(self,x):
	self.xRanges[x].setText(self.ranges[int(self.trialSelects[x].text())-1])

    # Creates a list of ranges so changeTrial can operate
    def fillListRanges(self, trials):
        self.ranges = []
        start = 0
        end = self.gui.timeSteps
        for trial in range(trials):
            self.ranges.append(str(start)+'-'+str(end))
            start += self.gui.timeSteps
            end += self.gui.timeSteps

