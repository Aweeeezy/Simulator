from PySide.QtGui import *
from PySide.QtCore import *

# Widget for displaying graph options for each plot
class GraphParams(QWidget):
    def __init__(self, gui, mpl):
	super(GraphParams, self).__init__()
        self.mpl = mpl
        self.gui = gui
	self.layout = QGridLayout()
	self.styleSelect = QComboBox()
	self.styleSelect.currentIndexChanged.connect(self.initOptions)
	self.styleSelect.addItem("Trial Plot")
	self.styleSelect.addItem("Time Plot")
	self.styleSelect.addItem("Surface Plot")
	self.layout.addWidget(self.styleSelect,0,0)
	self.setLayout(self.layout)
	self.show()

    # Fills layout according to styleSelect selection
    def initOptions(self):
	if self.styleSelect.currentText() == "Trial Plot":
	    self.dataBox = QComboBox()
	    self.layout.addWidget(self.dataBox,0,1,Qt.AlignCenter)

	if self.styleSelect.currentText() == "Time Plot":
	    self.dataBox = QComboBox()
            self.trialSelect = QLineEdit("1")
	    self.xRange = QLineEdit("x range")
            self.trialSelect.textChanged.connect(self.changeTrial)
            self.trialSelect.returnPressed.connect(self.gui.plot)
	    self.layout.addWidget(self.dataBox,0,1,Qt.AlignCenter)
            self.layout.addWidget(self.trialSelect,1,0,Qt.AlignCenter)
	    self.layout.addWidget(self.xRange,1,1)

	if self.styleSelect.currentText() == "Surface Plot":
            self.mpl.plt.cla()
            self.mpl.plt = self.mpl.figure.add_subplot(111, projection='3d')
            self.mpl.figure.canvas.draw()
            self.dataBox1 = QComboBox()
            self.zLabel = QLineEdit("z label")
            self.zRange = QLineEdit("z range")
            self.zLabel.returnPressed.connect(self.gui.plot)
            self.zRange.returnPressed.connect(self.gui.plot)
	    self.layout.addWidget(self.dataBox,0,1,Qt.AlignCenter)
	    self.layout.addWidget(self.zLabel,1,0)
	    self.layout.addWidget(self.zRange,1,1)

        self.gui.fillDataBoxes()

    # Support method for Time Plot implementations
    def changeTrial(self, steps=0, trials=0):
        if self.xRange.text() == 'x range':
            self.numSteps = steps
            self.fillListRanges(trials)
            self.xRange.setText(self.ranges[int(self.trialSelect.text())-1])
        else:
            try:
                self.xRange.setText(self.ranges[int(self.trialSelect.text())-1])
            except ValueError: pass

    # Creates a list of ranges so changeTrial can operate
    def fillListRanges(self, trials):
        self.ranges = []
        start = 0
        end = self.numSteps
        for trial in range(trials):
            self.ranges.append(str(start)+'-'+str(end))
            start += self.numSteps
            end += self.numSteps

