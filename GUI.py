import os
import gc
import sys
import subprocess
from PySide.QtGui import *
from PySide.QtCore import *
from MplGrapher import MplGrapher
from GraphParams import GraphParams

# Simulator GUI class
class GUI(QMainWindow):
    def __init__(self):
	super(GUI, self).__init__()
	self.w = QWidget()
	self.setCentralWidget(self.w)
        self.opening = False
	self.initUI()
	""" Test code -- to speed up testing, un-comment lines 21-23, comment out
	the first command of `saveFile()` lines 122-123, un-comment line 124 after
	changing it to the proper path, and un-comment 509 """
	self.saveFile()
    	self.genFuncBox()
    	self.run()

  ###			   ###
  ### Builds Simulator GUI ###
  ###			   ###

    def initUI(self):
	# Setting up central widget & layout
	self.w.move(0,0)
	self.w.setWindowTitle("Simulator")
	self.w.layout = QGridLayout() # Contains (1), (2), (3)
	self.w.layout.setColumnStretch(0,0)
	self.w.layout.setColumnStretch(1,5)

	# Initializing sub-widgets
	self.menuInit()      # (1)
	self.optionsInit()   # (2)
	self.displayInit()   # (3)

        # More initialization stuff
	self.w.layout.addWidget(self.simOptions,0,0)
	self.w.layout.addWidget(self.graphOptions,0,0)
	self.w.layout.addWidget(self.display,0,1,2,1)
	self.w.setLayout(self.w.layout)

  ###				       ###
  ### (1) Menubar w/ support functions ###
  ###				       ###

    def menuInit(self):
	self.menubar = QMenuBar()

	# Menu: Open & Save
	_file = self.menubar.addMenu('File')
	openAction = QAction("Open",self,triggered=self.openFile)
        openAction.setShortcut('Ctrl+O')
	_file.addAction(openAction)
	saveAction = QAction("Save",self,triggered=self.saveFile)
        saveAction.setShortcut('Ctrl+S')
	_file.addAction(saveAction)

	# Menu: Show/Hide, Switch, Run, Plot, & Cycle
	simulation = self.menubar.addMenu('Simulation')
	collapseAction = QAction("Show/Hide Settings",self,triggered=self.collapse)
	collapseAction.setShortcut('Ctrl+E')
	simulation.addAction(collapseAction)
	switchAction = QAction("Switch Settings",self,triggered=self.switch)
	switchAction.setShortcut('Ctrl+F')
	simulation.addAction(switchAction)
	runAction = QAction("Run",self,triggered=self.run)
	runAction.setShortcut('Ctrl+R')
	simulation.addAction(runAction)
	plotAction = QAction("Plot",self,triggered=self.plot)
	plotAction.setShortcut('Ctrl+P')
	simulation.addAction(plotAction)
	nextAction = QAction("Next Graph",self,triggered=self.cyclePlot)
	nextAction.setShortcut('Ctrl+C')
	simulation.addAction(nextAction)

    # (1.1 )Read parameters from file and sets sim/graphValues ### NEEDS TO BE REIMPLEMENTED ###
    def openFile(self):
        self.opening = True
	self.filePath, _= QFileDialog.getOpenFileName(self, 'open file', \
	    '~/', 'Simulations (*.sim);;C Files (*.c)' )
	fullPath = self.filePath.split("/")
	title = fullPath[-1]
	self.w.setWindowTitle(title)
	# Read .sim & populate proper fields...types of values are deliminated
	# with a line break (types: simulator, graphing, files)
	if self.filePath[-4:] == ".sim":
	    with open(self.filePath, 'r') as f:
		self.simValues = [""]
		value = f.readline()
		while 1:
		    if value != "\n":
                        self.simValues.append(value)
			value = f.readline()
		    else: break
		self.graphValues = [""]
		value = f.readline()
		while 1:
		    if value != "\n":
			self.graphValues.append(value)
			value = f.readline()
		    else: break
		self.files = f.readlines()
	    # Populates fields for simulator settings
	    self.numCond.setText(self.simValues[1])
	    self.numSim.setText(self.simValues[2])
	    self.numTrials.setText(self.simValues[3])
	    self.numSteps.setText(self.simValues[4])
	    self.dirPath = self.simValues[5]
	    self.numGraphs.setText(self.simValues[6])
	    x = 1
	    self.plot()
            self.opening = False

    # (1.2) Writes sim/graph values & data files to .sim ### NEEDS TO BE REIMPLEMENTED ###
    def saveFile(self):
	self.filePath, _= QFileDialog.getSaveFileName(self, 'save file', \
	     '~/', 'Simulations (*.sim)' )
	#self.filePath = "/Users/aweeeezy/bin/ivry/Test/Untitled"
	fileSplit = self.filePath.split("/")
	self.dirPath = "/".join(fileSplit[:-1])
	title = fileSplit[-1]
	self.w.setWindowTitle(title)
	# Doesn't yet grab condition values from self.runFuncs
	self.simValues = [str(self.numCond.text()),str(self.numSim.text()),
			str(self.numTrials.text()),str(self.numSteps.text()),
				str(self.dirPath)]
	self.graphValues = []
	with open(self.filePath, 'w') as f:
	    for item in self.simValues:
		f.write(str(item)+"\n")
	    f.write("\n")
	    for item in self.graphValues:
		f.write(str(item)+"\n")
	    f.write("\n")
	    try:
		for item in self.files:
		    f.write(str(item)+"\n")
	    except AttributeError:
		print "Save again after running to record data files"

    # (1.3) Shows/hides the settings window
    def collapse(self):
	if self.simOptions.isVisible() == True or \
		self.graphOptions.isVisible() == True:
	    self.simOptions.setVisible(False)
	    self.graphOptions.setVisible(False)
	    self.w.layout.setColumnMinimumWidth(0,0)
	elif self.simOptions.isVisible() == False and \
		self.graphOptions.isVisible() == False:
	    self.simOptions.setVisible(True)
	    self.w.layout.setColumnMinimumWidth(0,100)

    # (1.4) Switches between simulation and graph settings
    def switch(self):
	if self.simOptions.isVisible() == True:
	    self.simOptions.setVisible(False)
	    self.graphOptions.setVisible(True)
	else:
	    self.graphOptions.setVisible(False)
	    self.simOptions.setVisible(True)

    # (1.5.1) if '.c', call subprocess that executes .c file
    # if '.sim', call subprocess w/ execArgs appended to cmd list
    def run(self):
	try:
	    extension = self.filePath[-2:]
	    if extension == ".c":
		self.runC()
	    else:
		if self.coreFunc.text() == "coreFuncNoTrials":
		    cmd = ['/Users/aweeeezy/bin/ivry/Simulator/coreFuncTrials']
		    cmd.append(str(self.dirPath)+'/')
		    self.execArgs = [str(self.numCond.text()),str(self.numSim.text()),
				    str(self.numTrials.text()),str(self.numSteps.text())]
		    # If custom init params are to be used, append to execArgs
		    if "Checked" in str(self.checkBox.checkState()):
			self.execArgs.append(str(1))
			for field in self.paramsList:
			    self.execArgs.append(str(field.text()))
		    else: self.execArgs.append(str(0))
		if self.coreFunc.text() == "coreFuncTrials":
		    cmd = ['/Users/aweeeezy/bin/ivry/Simulator/coreFuncNoTrials']
		    cmd.append(str(self.dirPath)+'/')
		    self.execArgs = [str(self.numCond2.text()),str(self.numSim2.text()),
				     str(self.numSteps2.text())]
		    # If custom init params are to be used, append to execArgs
		    if "Checked" in str(self.checkBox2.checkState()):
			self.execArgs.append(str(1))
			for field in self.paramsList2:
			    self.execArgs.append(str(field.text()))
		    else: self.execArgs.append(str(0))
		trialFuncLenghts = []
		for box in self.selectedFuncsMap.itervalues():
		    trialFuncLenghts.append(box.count())
		max_trialFunc = max(trialFuncLenghts)
		self.execArgs.append(str(max_trialFunc))
		# Appends # of values & values from QComboBoxes in runFuncs{}
		self.trialLengths = []
		self.timeStepLengths = []
		for box in self.selectedFuncsMap.itervalues():
		    boxContent = [box.itemText(i) for i in range(box.count())]
		    self.trialLengths.append(int(self.numTrials.text())*box.count())
		    self.timeStepLengths.append(int(self.numTrials.text())*int(self.numSteps.text())*box.count())
		    self.execArgs.append(str(box.count()))
		    for content in boxContent:
			self.execArgs.append(str(content))
		for item in self.execArgs:
		    if item is not "": # Can't remember why I put this here...
			cmd.append(item)
		self.runC(cmd)
	except AttributeError:
	    self.console.insertPlainText("Double check inputs & save file first.\n")

    # (1.5.2) Runs selected .c file or coreFunc.c
    def runC(self, cmd=0):
	if cmd == 0:
	    process = self.dirPath+"/a.out"
            core = subprocess.Popen(process, stdout=subprocess.PIPE)
            try:
                for line in core.stdout:
                    self.console.insertPlainText(line)
            except IOError: pass
	    self.filterDataFiles()
	else:
	    subprocess.call(cmd)
	    core = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	    self.filterDataFiles(cmd)

    # (1.5.3) Filters files with "." in them
    def filterDataFiles(self, cmd=0):
	try:
	    self.files = os.listdir(self.dirPath)
	    copy = list(self.files)
	    for _file in copy:
		if "." in _file:
		    self.files.remove(_file)
	    if cmd == 0:
		fileLengths = []
		for f in self.files:
		    with open(self.dirPath+'/'+f, 'r') as fi:
			data = fi.readlines()
			dataLength = len(data)
			if dataLength not in fileLengths:
			    fileLengths.append(dataLength)
	    self.timeSteps = int(self.numSteps.text())
	except NameError: pass

    # (1.5.4) Fills dataBoxes w/ files (size based)
    def fillDataBoxes(self,fig,subplotNum):
        try:
	    dataBox = fig.boxes[subplotNum]
	    # Sorts out trial data files if 3D plotting
	    if self.dimensionButton.text() == "2D Plot":
		for f in self.files:
		    with open(self.dirPath+'/'+f, 'r') as fi:
			data = fi.readlines()
			if len(data) in self.timeStepLengths:
			    dataBox.addItem(f)
	    else:
		dataBox.addItems(self.files)
        except AttributeError:
	    self.console.insertPlainText("Double check inputs & save file first.\n")

    # (1.5.5) Support function for GraphParams class
    def fileLength(self,_file):
	with open(self.dirPath+'/'+_file) as f:
	    data = f.readlines()
	return len(data)

  ###					     ###
  ### (2) Labels/layouts for setting options ###
  ###	    layouts & support functions	     ###

    def optionsInit(self):
	# (2.1) Layout for simulator widgets
	self.simOptions = QWidget()
	simOptLayout = QGridLayout()
	self.loopParams1 = QWidget()
	self.initParams1 = QWidget()
	self.loopParams2 = QWidget()
	self.initParams2 = QWidget()
	self.initParams1.setVisible(False)
	self.loopParams2.setVisible(False)
	self.initParams2.setVisible(False)
	self.coreFunc = QPushButton("coreFuncNoTrials")

	# (2.1.1) Loop settings for coreFuncTrials
	self.loopSettings = QGridLayout()
	loopTitle = QLabel("<font size=6><b>Loop Parameters</b></font>")
	numConditions = QLabel("<b>Conditions: (press enter)</b>")
	numSim = QLabel("<b>Simulations:</b>")
	numTrials =  QLabel("<b>Trials:</b>")
	numSteps =  QLabel("<b>Steps:</b>")
	self.numCond = QLineEdit("1")
	self.numCond.returnPressed.connect(self.lambdaGenFuncBox())
	self.numSim = QLineEdit("1")
	self.numTrials = QLineEdit("300")
	self.numSteps = QLineEdit("3000")
	label1 = QLabel("<b>Available functions</b>")
	label2 = QLabel("<b>Functions to simulate</b>")

	self.loopSettings.addWidget(loopTitle,0,0,1,2,Qt.AlignCenter)
	self.loopSettings.addWidget(numConditions,1,0)
	self.loopSettings.addWidget(numSim,2,0)
	self.loopSettings.addWidget(numTrials,3,0)
	self.loopSettings.addWidget(numSteps,4,0)
	self.loopSettings.addWidget(self.numCond,1,1,1,2)
	self.loopSettings.addWidget(self.numSim,2,1,1,2)
	self.loopSettings.addWidget(self.numTrials,3,1,1,2)
	self.loopSettings.addWidget(self.numSteps,4,1,1,2)
	self.loopSettings.addWidget(label1,5,0)
	self.loopSettings.addWidget(label2,5,1)
	self.loopParams1.setLayout(self.loopSettings)

	# (2.1.2) Optional initialization parameters for coreFuncTrials
	outerParamLayout = QGridLayout()
	paramTitle = QLabel("<font size=6>Initialization Parameters</font>")
	checkBox = QLabel("Use custom init params:")
	self.checkBox = QCheckBox()
	outerParamLayout.addWidget(paramTitle,0,0,1,2,Qt.AlignCenter)
	outerParamLayout.addWidget(checkBox,1,0)
	outerParamLayout.addWidget(self.checkBox,1,1)

	tau = QLabel("Tau:")
	cue_onset = QLabel("Cue Onset:")
	cue_duration = QLabel("Cue Duration:")
	alpha_func_a = QLabel("Alpha Func A:")
	alpha_func_b = QLabel("Alpha Func B:")
	alpha_func_a_camkII = QLabel("Alpha Func A CamkII:")
	alpha_func_b_camkII = QLabel("Alpha Func B CamkII:")
	sensory_amp = QLabel("Sensory Amp:")
	pf_amp = QLabel("PF Amp:")
	pause_mod_amp = QLabel("Pause Mod Amp:")
	pause_decay = QLabel("Pause Decay:")
	w_tan_msn = QLabel("Tan-Msn Weight:")
	w_msn_mot = QLabel("Msn-Mot Weight:")
	w_pf_tan_init = QLabel("PF-Tan Weight:")
	w_ctx_msn_init = QLabel("Ctx-Msn Weight:")
	pr_alpha = QLabel("PR Alpha:")
	response_threshold = QLabel("Response Threshold:")
	AMPA_threshold = QLabel("AMPA Threshold:")
	NMDA_threshold = QLabel("NMDA Theshold:")
	DA_base = QLabel("DA Base:")
	LTP_msn = QLabel("LTP Msn:")
	LTD_msn = QLabel("LTD Msn:")
	LTP_tan = QLabel("LTP Tan:")
	LTD_tan = QLabel("LTD Tan:")

	tau = QLineEdit()
	cue_onset = QLineEdit()
	cue_duration = QLineEdit()
	alpha_func_a = QLineEdit()
	alpha_func_b = QLineEdit()
	alpha_func_a_camkII = QLineEdit()
	alpha_func_b_camkII = QLineEdit()
	sensory_amp = QLineEdit()
	pf_amp = QLineEdit()
	pause_mod_amp = QLineEdit()
	pause_decay = QLineEdit()
	w_tan_msn = QLineEdit()
	w_msn_mot = QLineEdit()
	w_pf_tan_init = QLineEdit()
	w_ctx_msn_init = QLineEdit()
	pr_alpha = QLineEdit()
	response_threshold = QLineEdit()
	AMPA_threshold = QLineEdit()
	NMDA_threshold = QLineEdit()
	DA_base = QLineEdit()
	LTP_msn = QLineEdit()
	LTD_msn = QLineEdit()
	LTP_tan = QLineEdit()
	LTD_tan = QLineEdit()

	self.paramsList = [tau, cue_onset, cue_duration, alpha_func_a,
	    alpha_func_b, alpha_func_a_camkII, alpha_func_b_camkII,
	    sensory_amp, pf_amp, pause_mod_amp, pause_decay, w_tan_msn,
	    w_msn_mot, w_pf_tan_init, w_ctx_msn_init, pr_alpha,
	    response_threshold, AMPA_threshold, NMDA_threshold, DA_base,
	    LTP_msn, LTD_msn, LTP_tan, LTD_tan]

	innerParamLayout = QGridLayout()
	innerParamLayout.addWidget(tau,0,0)
	innerParamLayout.addWidget(cue_onset,1,0)
	innerParamLayout.addWidget(cue_duration,2,0)
	innerParamLayout.addWidget(alpha_func_a,3,0)
	innerParamLayout.addWidget(alpha_func_b,4,0)
	innerParamLayout.addWidget(alpha_func_a_camkII,5,0)
	innerParamLayout.addWidget(alpha_func_b_camkII,6,0)
	innerParamLayout.addWidget(sensory_amp,7,0)
	innerParamLayout.addWidget(pf_amp,8,0)
	innerParamLayout.addWidget(pause_mod_amp,9,0)
	innerParamLayout.addWidget(pause_decay,10,0)
	innerParamLayout.addWidget(w_tan_msn,11,0)
	innerParamLayout.addWidget(w_msn_mot,12,0)
	innerParamLayout.addWidget(w_pf_tan_init,13,0)
	innerParamLayout.addWidget(w_ctx_msn_init,14,0)
	innerParamLayout.addWidget(pr_alpha,15,0)
	innerParamLayout.addWidget(response_threshold,16,0)
	innerParamLayout.addWidget(AMPA_threshold,17,0)
	innerParamLayout.addWidget(NMDA_threshold,18,0)
	innerParamLayout.addWidget(DA_base,19,0)
	innerParamLayout.addWidget(LTP_msn,20,0)
	innerParamLayout.addWidget(LTD_msn,21,0)
	innerParamLayout.addWidget(LTP_tan,22,0)
	innerParamLayout.addWidget(LTD_tan,23,0)
	innerParamLayout.addWidget(tau,0,1)
	innerParamLayout.addWidget(cue_onset,1,1)
	innerParamLayout.addWidget(cue_duration,2,1)
	innerParamLayout.addWidget(alpha_func_a,3,1)
	innerParamLayout.addWidget(alpha_func_b,4,1)
	innerParamLayout.addWidget(alpha_func_a_camkII,5,1)
	innerParamLayout.addWidget(alpha_func_b_camkII,6,1)
	innerParamLayout.addWidget(sensory_amp,7,1)
	innerParamLayout.addWidget(pf_amp,8,1)
	innerParamLayout.addWidget(pause_mod_amp,9,1)
	innerParamLayout.addWidget(pause_decay,10,1)
	innerParamLayout.addWidget(w_tan_msn,11,1)
	innerParamLayout.addWidget(w_msn_mot,12,1)
	innerParamLayout.addWidget(w_pf_tan_init,13,1)
	innerParamLayout.addWidget(w_ctx_msn_init,14,1)
	innerParamLayout.addWidget(pr_alpha,15,1)
	innerParamLayout.addWidget(response_threshold,16,1)
	innerParamLayout.addWidget(AMPA_threshold,17,1)
	innerParamLayout.addWidget(NMDA_threshold,18,1)
	innerParamLayout.addWidget(DA_base,19,1)
	innerParamLayout.addWidget(LTP_msn,20,1)
	innerParamLayout.addWidget(LTD_msn,21,1)
	innerParamLayout.addWidget(LTP_tan,22,1)
	innerParamLayout.addWidget(LTD_tan,23,1)
	dummyWidget = QWidget()
	dummyLayout = QVBoxLayout()
	innerParamWidget = QWidget()
	innerParamWidget.setLayout(innerParamLayout)
	dummyLayout.addWidget(innerParamWidget)
	dummyWidget.setLayout(dummyLayout)
	scrollAreaParams1 = QScrollArea(dummyWidget)
	scrollAreaParams1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
	scrollAreaParams1.setFixedWidth(dummyWidget.width()-335)
	scrollAreaParams1.setFixedHeight(dummyWidget.height())
	scrollAreaParams1.setWidget(innerParamWidget)
	outerParamLayout.addWidget(dummyWidget,2,0,50,2)
	self.initParams1.setLayout(outerParamLayout)

	# (2.1.3) Loop settings for coreFuncNoTrials
	self.loopSettings2 = QGridLayout()
	loopTitle2 = QLabel("<font size=6><b>Loop Parameters</b></font>")
	numConditions2 = QLabel("<b>Conditions: (press enter)</b>")
	numSim2 = QLabel("<b>Simulations:</b>")
	numSteps2 =  QLabel("<b>Steps:</b>")
	self.numCond2 = QLineEdit("1")
	self.numCond2.returnPressed.connect(self.lambdaGenFuncBox())
	self.numSim2 = QLineEdit("1")
	self.numSteps2 = QLineEdit("3000")
	label3 = QLabel("<b>Available functions</b>")
	label4 = QLabel("<b>Functions to simulate</b>")

	self.availableFuncsMap = {} # (Dict) QComboBoxes w/ all sim funcs.
	self.selectedFuncsMap = {} # (Dict) QComboBoxes w/ selected sim funcs.
	self.clearFuncs = {} # (Dict) QButtons that clear selected sim funcs.

	self.loopSettings2.addWidget(loopTitle2,0,0,1,2,Qt.AlignCenter)
	self.loopSettings2.addWidget(numConditions2,1,0)
	self.loopSettings2.addWidget(numSim2,2,0)
	self.loopSettings2.addWidget(numSteps2,3,0)
	self.loopSettings2.addWidget(self.numCond2,1,1,1,2)
	self.loopSettings2.addWidget(self.numSim2,2,1,1,2)
	self.loopSettings2.addWidget(self.numSteps2,3,1,1,2)
	self.loopSettings2.addWidget(label3,4,0)
	self.loopSettings2.addWidget(label4,4,1)
	self.loopParams2.setLayout(self.loopSettings2)

	# (2.1.4) Optional initialization parameters for coreFuncNoTrials
	""" Yet to be implemented """
	innerParamLayout2 = QGridLayout()
	paramTitle2 = QLabel("<font size=6>Initialization Parameters</font>")
	checkBox2 = QLabel("Use custom init params:")
	self.checkBox2 = QCheckBox()

	self.paramsList2 = [tau, cue_onset, cue_duration, alpha_func_a,
	    alpha_func_b, alpha_func_a_camkII, alpha_func_b_camkII, sensory_amp,
	    pf_amp, pause_mod_amp, pause_decay, w_tan_msn, w_msn_mot,
	    w_pf_tan_init, w_ctx_msn_init, pr_alpha, response_threshold,
	    AMPA_threshold, NMDA_threshold, DA_base, LTP_msn, LTD_msn,
	    LTP_tan, LTD_tan]

	innerParamLayout2.addWidget(paramTitle2,0,0,1,2,Qt.AlignCenter)
	innerParamLayout2.addWidget(checkBox2,1,1)
	innerParamLayout2.addWidget(self.checkBox2,1,2,Qt.AlignCenter)
	#scrollAreaParams1 = QScrollArea()
	#simOptLayout.addWidget(scrollAreaParams1)
	self.initParams2.setLayout(innerParamLayout2)
	#scrollAreaParams1.setWidget(self.initParams1)

	# (2.1.5) Toolbar & layout setup
	simButtons = QToolBar()
	paramsButton = QPushButton("initParams/loopParams")
	paramsButton.pressed.connect(self.switchSettings)
	self.coreFunc.pressed.connect(self.switchCoreFuncs)
	simButtons.addWidget(paramsButton)
	simButtons.addWidget(self.coreFunc)
	simOptLayout.addWidget(simButtons,0,0)
	simOptLayout.addWidget(self.loopParams1,1,0)
	simOptLayout.addWidget(self.initParams1,1,0)
	simOptLayout.addWidget(self.loopParams2,1,0)
	simOptLayout.addWidget(self.initParams2,1,0)
	self.simOptions.setLayout(simOptLayout)

	# (2.2) Layout for graphing widgets
	self.graphOptions = QWidget()
	self.graphOptions.setVisible(False)
	graphingSettings = QGridLayout()
	graphTitle = QLabel("<font size=6>Graphing Settings</font>")
	self.displayedGraph = QComboBox()
	self.displayedGraph.currentIndexChanged.connect(self.changePlot)
	self.graphParams = QStackedWidget()
	graphButtons = QToolBar()
	addFigureButton = QPushButton("Add Figure")
	addFigureButton.pressed.connect(self.addGraphOptions)
	removeFigures = QPushButton("Remove All")
	removeFigures.pressed.connect(self.initFigs)
	self.dimensionButton = QPushButton("3D Plot")
	self.dimensionButton.pressed.connect(self.switchPlot)
	graphButtons.addWidget(addFigureButton)
	graphButtons.addWidget(removeFigures)
	graphButtons.addWidget(self.dimensionButton)
	graphingSettings.addWidget(graphButtons,0,0)
	graphingSettings.addWidget(graphTitle,1,0,1,2,Qt.AlignCenter)
	graphingSettings.addWidget(self.displayedGraph,2,1)
	graphingSettings.addWidget(self.graphParams,3,0,1,2,Qt.AlignCenter)
	self.graphOptions.setLayout(graphingSettings)
	self.initFigs()

    # (2.2.1) Support function for setting up graph settings
    def initFigs(self):
	self.displayedGraph.clear()
	self.displayedGraph.addItem("Console")
	self.plots = {}
	self.opts = {}
	self.figCount = 0

    # (2.2.2) Creates paired QComboBoxes with QPushButton
    def genFuncBox(self):
	if self.coreFunc.text() == "coreFuncNoTrials":
	    for x in range(int(self.numCond.text())):
		self.availableFuncsMap[x] = QComboBox()
		self.selectedFuncsMap[x] = QComboBox()
		self.clearFuncs[x] = QPushButton("Clear")
		funcs = ("simulate_acquisition_full","simulate_acquisition_partial",\
			    "simulate_extinction","simulate_extinction_prf",\
			    "simulate_reacquisition_2","simulate_reacquisition_8")
		self.availableFuncsMap[x].addItems(funcs)
		self.availableFuncsMap[x].activated.connect(self.pairComboBoxes(x))
	#########
		self.selectedFuncsMap[0].addItem(self.availableFuncsMap[0].currentText())
	#########
		self.clearFuncs[x].pressed.connect(self.pairClearButton(x))
		self.loopSettings.addWidget(self.availableFuncsMap[x],x+7,0)
		self.loopSettings.addWidget(self.selectedFuncsMap[x],x+7,1)
		self.loopSettings.addWidget(self.clearFuncs[x],x+7,2)
	elif self.coreFunc.text() == "coreFuncTrials":
	    for x in range(int(self.numCond2.text())):
		self.availableFuncsMap[x] = QComboBox()
		self.selectedFuncsMap[x] = QComboBox()
		self.clearFuncs[x] = QPushButton("Clear")
		funcs = ("simulate_acquisition_full","simulate_acquisition_partial",\
			    "simulate_extinction","simulate_extinction_prf",\
			    "simulate_reacquisition_2","simulate_reacquisition_8")
		self.availableFuncsMap[x].addItems(funcs)
		self.availableFuncsMap[x].activated.connect(self.pairComboBoxes(x))
		self.clearFuncs[x].pressed.connect(self.pairClearButton(x))
		self.loopSettings2.addWidget(self.availableFuncsMap[x],x+7,0)
		self.loopSettings2.addWidget(self.selectedFuncsMap[x],x+7,1)
		self.loopSettings2.addWidget(self.clearFuncs[x],x+7,2)

##### Support functions for `genFuncBox()`
    def lambdaGenFuncBox(self):
	self.availableFuncsMap = {} # (Dict) QComboBoxes w/ all sim funcs.
	self.selectedFuncsMap = {} # (Dict) QComboBoxes w/ selected sim funcs.
	self.clearFuncs = {} # (Dict) QButtons that clear selected sim funcs.
	return lambda : self.genFuncBox()

    def pairComboBoxes(self,index):
	return lambda : self.addTrialFunc(index)

    def addTrialFunc(self,index):
	self.selectedFuncsMap[index].addItem(
				self.availableFuncsMap[index].currentText())

    def pairClearButton(self,index):
	return lambda : self.clearBox(index)

    def clearBox(self,index):
	self.selectedFuncsMap[index].clear()
###########################################

    # (2.2.3) Alternates between loop & parameter settings
    def switchSettings(self):
	if self.coreFunc.text() == "coreFuncTrials":
	    if self.loopParams2.isVisible() == True:
		self.loopParams2.setVisible(False)
		self.initParams2.setVisible(True)
	    else:
		self.loopParams2.setVisible(True)
		self.initParams2.setVisible(False)
	elif self.coreFunc.text() == "coreFuncNoTrials":
	    if self.loopParams1.isVisible() == True:
		self.loopParams1.setVisible(False)
		self.initParams1.setVisible(True)
	    else:
		self.loopParams1.setVisible(True)
		self.initParams1.setVisible(False)

    # (2.2.4) Alternated between coreFuncTrials & coreFuncNoTrials
    def switchCoreFuncs(self):
	if self.coreFunc.text() == "coreFuncNoTrials":
	    self.loopParams1.setVisible(False)
	    self.initParams1.setVisible(False)
	    self.loopParams2.setVisible(True)
	    self.coreFunc.setText("coreFuncTrials")
	elif self.coreFunc.text() == "coreFuncTrials":
	    self.loopParams2.setVisible(False)
	    self.initParams2.setVisible(False)
	    self.loopParams1.setVisible(True)
	    self.coreFunc.setText("coreFuncNoTrials")

    # (2.2.5) Changes text of dimensionButton (support function for `plot()`)
    def switchPlot(self):
	if self.dimensionButton.text() == "3D Plot":
	    self.dimensionButton.setText("2D Plot")
	else:
	    self.dimensionButton.setText("3D Plot")

    # (2.3) Builds graphing option layout (GraphParams) for each plot
    def addGraphOptions(self):
	self.figCount+=1
	_next = "Fig"+str(self.figCount)
	graphInstance = MplGrapher(self)
	paramsInstance = GraphParams(self,graphInstance)
	self.plots[_next] = graphInstance
	self.opts[_next] = paramsInstance
	if self.opening == True:
	    value = self.graphValues.pop(1)
	    #self.opts[_next].styleSelect.setEditText(value)
	else:
	    pass
	    #self.opts[_next].styleSelect.setCurrentIndex(0)
	self.displayedGraph.addItem(_next)
	self.display.addWidget(graphInstance.getFig())
	self.graphParams.addWidget(paramsInstance)
	self.displayedGraph.setCurrentIndex(self.figCount)

    # (2.4) Generate plots from MplGrapher instances
    def plot(self):
	data = []
	xRange = []
        zLabel = []
        zRange = []
	n = 0

	for i,fig in enumerate(self.opts):
	    fig = self.opts[fig]
	    if fig.changed == True:
		for x in range(fig.width*fig.height):
		    data.append(str(fig.boxes[x].currentText()))
		    try:
			xRange.append(str(fig.xRanges[x].text()))
		    except AttributeError: print "\tAttribute Error (plot())"
		    except KeyError: xRange.append("none")
		    try:
			zLabel.append(str(fig.zLabels[x].text()))
			zRange.append(str(fig.zRanges[x].text()))
		    except AttributeError:
			zLabel.append("none")
			zRange.append("none")
		    except KeyError:
			zLabel.append("none")
			zRange.append("none")
		n = i+x

	n = 0
	for i,fig in enumerate(self.plots):
	    figure = self.opts[fig]
	    fig = self.plots[fig]
	    try:
		if fig.changed == True:
		    for x in range(figure.width*figure.height):
			fig.setGraphParams(self.dirPath,x,
				data[i+x+n],xRange[i+x+n],zLabel[i+x+n],zRange[i+x+n],
				int(figure.boxes[x].currentText().split('_')[-1]))
		    n = i+x
		    fig.changed = False
	    except AttributeError: print "GUI: setGraphParams exception"
	    except IndexError: print "IndexError..."

    # (2.5) Sets widget to displayedGraph & graphParams to paramsInstans
    def changePlot(self):
	selection = self.displayedGraph.currentText()
        if "Fig" in selection:
	    self.graphParams.setVisible(True)
	    objId = id(self.plots.get(selection))
	    obj = self.objects_by_id(objId)
	    self.display.setCurrentWidget(obj.getFig())
	    params = id(self.opts.get(selection))
	    paramsObj = self.objects_by_id(params)
	    self.graphParams.setCurrentWidget(paramsObj)
	else:
	    self.graphParams.setVisible(False)
	    try:
		self.display.setCurrentWidget(self.console)
	    except AttributeError: pass

    # (2.6) Cycles plots
    def cyclePlot(self):
	currentPlot = self.displayedGraph.currentIndex()
	if currentPlot < self.displayedGraph.count() - 1:
	    self.displayedGraph.setCurrentIndex(currentPlot+1)
	else:
	    self.displayedGraph.setCurrentIndex(0)

    # (2.7) Looks for object based on object ID
    def objects_by_id(self, id_):
	for obj in gc.get_objects():
	    if id(obj) == id_:
		return obj

  ###						     ###
  ### (3) Console output & cyclable Matplotlib plots ###
  ###						     ###

    def displayInit(self):
	self.display = QStackedWidget()
	self.console = QTextEdit()
	self.console.setStyleSheet("QTextEdit { background-color: black }")
	self.console.setTextColor(QColor(0,220,50))
	self.console.setCursorWidth(5)
	self.console.setReadOnly(True)
	self.console.ensureCursorVisible()
	self.console.append("Console display\n")
	self.display.addWidget(self.console)



def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Simulator")
    gui = GUI()
    gui.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

