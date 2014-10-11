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
	self.zLabels = {}
	self.zRanges = {}
	subplotLabel = QLabel("Dimensions (w,h):")
	self.subplotDimensions = QLineEdit()
	self.subplotDimensions.returnPressed.connect(self.fillBoxes)
	self.layout.addWidget(subplotLabel,0,0)
	self.layout.addWidget(self.subplotDimensions,0,1)
	self.setLayout(self.layout)
	self.show()

    # Fills data boxes with files
    def fillBoxes(self):
	self.labels = {}
	self.boxes = {}
	self.args = self.subplotDimensions.text().split(",")
	self.width = int(self.args[0])
	self.height = int(self.args[1])
	for x in range(self.width*self.height):
	    if self.gui.dimensionButton.text() == "2D Plot":
		self.mpl.adjustSubplots(self.width,self.height,x+1,d=True)
	    else:
		self.mpl.adjustSubplots(self.width,self.height,x+1)
	    self.labels[x] = QLabel("DataBox for subplot %i:" % (int(x)+1))
	    self.boxes[x] = QComboBox()
	    self.gui.fillDataBoxes(self,x)
	    self.boxes[x].activated.connect(self.lambdaFunc(x))
	    self.layout.addWidget(self.labels[x],(x*2)+1,0,Qt.AlignCenter)
	    self.layout.addWidget(self.boxes[x],(x*2)+1,1,Qt.AlignCenter)
	    self.layout.addWidget(QLabel(),(x*2)+2,0)
	    self.layout.addWidget(QLabel(),(x*2)+2,1)

##### Helper functions
    def lambdaFunc(self,index):
	return lambda : self.initOptions(index)

    def otherLambda(self, index):
	return lambda : self.changeTrial(index)
################################################

    # Initialized graphing parameters
    def initOptions(self,x):
	if self.gui.fileLength(self.boxes[x].currentText()) == self.gui.length2:
	    if self.gui.dimensionButton.text() == "2D Plot":
		self.zLabels[x] = QLineEdit("z label")
		self.zRanges[x] = QLineEdit("z range")
		self.layout.addWidget(self.zLabels[x],(x*2)+2,0)
		self.layout.addWidget(self.zRanges[x],(x*2)+2,1)
	    else:
		self.trialSelects[x] = QLineEdit("Enter trial #")
		self.xRanges[x] = QLineEdit("x range")
		self.fillListRanges(self.gui.length1)
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
	else:
	    print self.boxes[x].currentText(), "is not a proper file length"

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

