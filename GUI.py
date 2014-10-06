import gc
import os
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
	#self.setIconSize(QSize(16,16))
	self.w = QWidget()
	self.setCentralWidget(self.w)
        self.opening = False
	self.initUI()
	self.saveFile()
	self.genFuncBox("coreFunc2")
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

	# Menu: Open (1.1) & Save (1.2)
	_file = self.menubar.addMenu('File')
	openAction = QAction("Open",self,triggered=self.openFile)
        openAction.setShortcut('Ctrl+O')
	_file.addAction(openAction)
	saveAction = QAction("Save",self,triggered=self.saveFile)
        saveAction.setShortcut('Ctrl+S')
	_file.addAction(saveAction)

	# Menu: Show/Hide (1.3) Switch (1.4) Run (1.5) Plot (2.4) & Cycle (2.6)
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

    # Read parameters from file and sets sim/graphValues (1.1)
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
	    # Requires GUI interaction (graphing settings) prior to opening file
	    # Populates proper fields of GraphParams with graphing values
	    """
	    for opt in self.opts:
                self.filterDataFiles()
		if self.opts[opt].styleSelect.currentText() == "Trial Plot":
		    self.opts[opt].dataBox.setEditText(self.graphValues[x]);x+=1
		elif self.opts[opt].styleSelect.currentText() == "Time Plot":
		    self.opts[opt].dataBox.setEditText(self.graphValues[x]);x+=1
		    self.opts[opt].xRange.setText(self.graphValues[x]);x+=1
		    self.opts[opt].trialSelect.setText(self.graphValues[x]);x+=1
		else:
		    self.opts[opt].dataBox.setEditText(self.graphValues[x]);x+=1
		    self.opts[opt].zLabel.setEditText(self.graphValues[x]);x+=1
		    self.opts[opt].zRange.setText(self.graphValues[x]);x+=1
	    """
	    self.plot()
            self.opening = False

    # Writes sim/graph values & data files to .sim (1.2)
    def saveFile(self):
	#self.filePath, _= QFileDialog.getSaveFileName(self, 'save file', \
	    # '~/', 'Simulations (*.sim)' )
	self.filePath = "/Users/aweeeezy/bin/ivry/Test/untitled"
	fileSplit = self.filePath.split("/")
	self.dirPath = "/".join(fileSplit[:-1])
	title = fileSplit[-1]
	self.w.setWindowTitle(title)
	# Doesn't yet grab condition values from self.runFuncs
	self.simValues = [str(self.numCond.text()),str(self.numSim.text()),
			str(self.numTrials.text()),str(self.numSteps.text()),
				str(self.dirPath)]
	self.graphValues = []
	# Grabs graphing values...each segment is prepended with a string
	# denoting what type of GraphParams instance to populate to
	"""
	for opt in self.opts:
	    if self.opts[opt].styleSelect.currentText() == "Trial Plot":
		self.graphValues.append("Trial Plot")
		self.graphValues.append(self.opts[opt].dataBox.currentText())
	    elif self.opts[opt].styleSelect.currentText() == "Time Plot":
                self.graphValues.append("Time Plot")
		self.graphValues.append(self.opts[opt].dataBox.currentText())
		self.graphValues.append(self.opts[opt].xRange.text())
                self.graphValues.append(self.opts[opt].trialSelect.text())
	    else:
                self.graphValues.append("Surface Plot")
                self.graphValues.append(self.opts[opt].zLabel.text())
		self.graphValues.append(self.opts[opt].zRange.text())
	"""
	with open(self.filePath, 'w') as f:
	    for item in self.simValues:
		f.write(str(item)+"\n")
	    f.write("\n")
	    for item in self.graphValues:
		f.write(str(item)+"\n")
	    f.write("\n")
#	    for item in self.files:
#		f.write(str(item)+"\n")

    # Shows/hides the settings window (1.3)
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

    # Switches between simulation and graph settings (1.4)
    def switch(self):
	if self.simOptions.isVisible() == True:
	    self.simOptions.setVisible(False)
	    self.graphOptions.setVisible(True)
	else:
	    self.graphOptions.setVisible(False)
	    self.simOptions.setVisible(True)

    # (a) if '.c', call subprocess that executes .c file (1.5.1)
    # (b) if '.sim', call subprocess w/ execArgs appended to cmd list
    def run(self):
	try:
	    extension = self.filePath[-2:]
	    if extension == ".c":
		self.runC()
	    else:
		if self.coreFunc.text() == "coreFunc2":
		    cmd = ['/Users/aweeeezy/bin/ivry/Simulator/coreFuncTrials']
		if self.coreFunc.text() == "coreFunc1":
		    cmd = ['/Users/aweeeezy/bin/ivry/Simulator/coreFuncNoTrials']
		cmd.append(str(self.dirPath)+'/')
		self.execArgs = [str(self.numCond.text()),str(self.numSim.text()),
				str(self.numTrials.text()),str(self.numSteps.text())]
		# If custom init params are to be used, append to execArgs
		if "Checked" in str(self.checkBox.checkState()):
		    self.execArgs.append(str(1))
		    for field in self.paramsList:
			self.execArgs.append(str(field.text()))
		else: self.execArgs.append(str(0))
		# Appends # of values & values from QComboBoxes in runFuncs{}
		for box in self.selectedFuncsMap.itervalues():
		    boxContent = [box.itemText(i) for i in range(box.count())]
		    self.execArgs.append(str(box.count()))
		    for content in boxContent:
			self.execArgs.append(str(content))
		for item in self.execArgs:
		    if item is not "": # Can't remember why I put this here...
			cmd.append(item)
		self.runC(cmd)
	except AttributeError:
	    self.console.insertPlainText("Double check inputs & save file first.\n")

    # Runs selected .c file or coreFunc.c (1.5.2)
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
	    self.filterDataFiles()

    # Filters files with "." in them (1.5.3)
    def filterDataFiles(self):
	self.files = os.listdir(self.dirPath)
	copy = list(self.files)
	for _file in copy:
	    if "." in _file:
		self.files.remove(_file)
	self.length1 = int(self.numTrials.text())
	self.length2 = int(self.numSteps.text())*int(self.length1)
	self.timeSteps = int(self.numSteps.text())

    def fileLength(self,_file):
	with open(self.dirPath+'/'+_file) as f:
	    data = f.readlines()
	return len(data)

    # Fills dataBoxes w/ files (size based) (1.5.4)
    def fillDataBoxes(self,fig,subplotNum):
        try:
	    dataBox = fig.boxes[subplotNum]
	    dataBox.addItems(self.files)
        except AttributeError:
	    self.console.insertPlainText("Double check inputs & save file first.\n")

  ###					     ###
  ### (2) Labels/layouts for setting options ###
  ###	    layouts & support functions	     ###

    def optionsInit(self):
	# Layout for simulator widgets (2.2)
	self.simOptions = QWidget()
	self.simOptLayout = QGridLayout()
	self.loopParams1 = QWidget()
	self.initParams1 = QWidget()
	self.loopParams2 = QWidget()
	self.initParams2 = QWidget()
	self.initParams1.setVisible(False)
	self.loopParams2.setVisible(False)
	self.initParams2.setVisible(False)
	self.coreFunc = QPushButton("coreFunc2")

	# Loop settings for first coreFunc
	self.loopSettings = QGridLayout()
	loopTitle = QLabel("<font size=6><b>Loop Parameters</b></font>")
	numConditions = QLabel("<b>Conditions:</b>")
	numSim = QLabel("<b>Simulations:</b>")
	numTrials =  QLabel("<b>Trials:</b>")
	numSteps =  QLabel("<b>Steps:</b>")
	self.numCond = QLineEdit("1")
	self.numCond.returnPressed.connect(self.lambdaGenFuncBox(self.coreFunc.text()))
	self.numSim = QLineEdit("1")
	self.numTrials = QLineEdit("300")
	self.numSteps = QLineEdit("3000")
	label1 = QLabel("<b>Possible Functions</b>")
	label2 = QLabel("<b>Selected Functions</b>")

	self.possibleFuncsMap = {} # (Dict) QComboBoxes w/ all sim funcs.
	self.selectedFuncsMap = {} # (Dict) QComboBoxes w/ selected sim funcs.
	self.clearFuncs = {} # (Dict) QButtons that clear selected sim funcs.

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

	# Loop settings for second coreFunc
	self.loopSettings2 = QGridLayout()
	loopTitle2 = QLabel("<font size=6><b>Loop Parameters</b></font>")
	numConditions2 = QLabel("<b>Conditions:</b>")
	numSim2 = QLabel("<b>Simulations:</b>")
	numSteps2 =  QLabel("<b>Steps:</b>")
	self.numCond2 = QLineEdit("1")
	self.numCond2.returnPressed.connect(self.lambdaGenFuncBox(self.coreFunc.text()))
	self.numSim2 = QLineEdit("1")
	self.numSteps2 = QLineEdit("3000")
	label3 = QLabel("<b>Possible Functions</b>")
	label4 = QLabel("<b>Selected Functions</b>")

	self.possibleFuncsMap = {} # (Dict) QComboBoxes w/ all sim funcs.
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

	# Optional initialization parameters for first coreFunc
	self.initParamSettings = QGridLayout()
	paramTitle = QLabel("<font size=6>Initialization Parameters</font>")
	checkBox = QLabel("Use custom init params:")
	self.checkBox = QCheckBox()
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

	self.tau = QLineEdit()
	self.cue_onset = QLineEdit()
	self.cue_duration = QLineEdit()
	self.alpha_func_a = QLineEdit()
	self.alpha_func_b = QLineEdit()
	self.alpha_func_a_camkII = QLineEdit()
	self.alpha_func_b_camkII = QLineEdit()
	self.sensory_amp = QLineEdit()
	self.pf_amp = QLineEdit()
	self.pause_mod_amp = QLineEdit()
	self.pause_decay = QLineEdit()
	self.w_tan_msn = QLineEdit()
	self.w_msn_mot = QLineEdit()
	self.w_pf_tan_init = QLineEdit()
	self.w_ctx_msn_init = QLineEdit()
	self.pr_alpha = QLineEdit()
	self.response_threshold = QLineEdit()
	self.AMPA_threshold = QLineEdit()
	self.NMDA_threshold = QLineEdit()
	self.DA_base = QLineEdit()
	self.LTP_msn = QLineEdit()
	self.LTD_msn = QLineEdit()
	self.LTP_tan = QLineEdit()
	self.LTD_tan = QLineEdit()

	self.paramsList = [self.tau, self.cue_onset, self.cue_duration,
	    self.alpha_func_a, self.alpha_func_b, self.alpha_func_a_camkII,
	    self.alpha_func_b_camkII, self.sensory_amp, self.pf_amp,
	    self.pause_mod_amp, self.pause_decay, self.w_tan_msn,
	    self.w_msn_mot, self.w_pf_tan_init, self.w_ctx_msn_init,
	    self.pr_alpha, self.response_threshold, self.AMPA_threshold,
	    self.NMDA_threshold, self.DA_base, self.LTP_msn, self.LTD_msn,
	    self.LTP_tan, self.LTD_tan]

	self.initParamSettings.addWidget(paramTitle,0,0,1,2,Qt.AlignCenter)
	self.initParamSettings.addWidget(checkBox,1,1)
	self.initParamSettings.addWidget(self.checkBox,1,2,Qt.AlignCenter)
	self.initParamSettings.addWidget(tau,2,0)
	self.initParamSettings.addWidget(cue_onset,3,0)
	self.initParamSettings.addWidget(cue_duration,4,0)
	self.initParamSettings.addWidget(alpha_func_a,5,0)
	self.initParamSettings.addWidget(alpha_func_b,6,0)
	self.initParamSettings.addWidget(alpha_func_a_camkII,7,0)
	self.initParamSettings.addWidget(alpha_func_b_camkII,8,0)
	self.initParamSettings.addWidget(sensory_amp,9,0)
	self.initParamSettings.addWidget(pf_amp,10,0)
	self.initParamSettings.addWidget(pause_mod_amp,11,0)
	self.initParamSettings.addWidget(pause_decay,12,0)
	self.initParamSettings.addWidget(w_tan_msn,13,0)
	self.initParamSettings.addWidget(w_msn_mot,14,0)
	self.initParamSettings.addWidget(w_pf_tan_init,15,0)
	self.initParamSettings.addWidget(w_ctx_msn_init,16,0)
	self.initParamSettings.addWidget(pr_alpha,17,0)
	self.initParamSettings.addWidget(response_threshold,18,0)
	self.initParamSettings.addWidget(AMPA_threshold,19,0)
	self.initParamSettings.addWidget(NMDA_threshold,20,0)
	self.initParamSettings.addWidget(DA_base,21,0)
	self.initParamSettings.addWidget(LTP_msn,22,0)
	self.initParamSettings.addWidget(LTD_msn,23,0)
	self.initParamSettings.addWidget(LTP_tan,24,0)
	self.initParamSettings.addWidget(LTD_tan,25,0)
	self.initParamSettings.addWidget(self.tau,2,1)
	self.initParamSettings.addWidget(self.cue_onset,3,1)
	self.initParamSettings.addWidget(self.cue_duration,4,1)
	self.initParamSettings.addWidget(self.alpha_func_a,5,1)
	self.initParamSettings.addWidget(self.alpha_func_b,6,1)
	self.initParamSettings.addWidget(self.alpha_func_a_camkII,7,1)
	self.initParamSettings.addWidget(self.alpha_func_b_camkII,8,1)
	self.initParamSettings.addWidget(self.sensory_amp,9,1)
	self.initParamSettings.addWidget(self.pf_amp,10,1)
	self.initParamSettings.addWidget(self.pause_mod_amp,11,1)
	self.initParamSettings.addWidget(self.pause_decay,12,1)
	self.initParamSettings.addWidget(self.w_tan_msn,13,1)
	self.initParamSettings.addWidget(self.w_msn_mot,14,1)
	self.initParamSettings.addWidget(self.w_pf_tan_init,15,1)
	self.initParamSettings.addWidget(self.w_ctx_msn_init,16,1)
	self.initParamSettings.addWidget(self.pr_alpha,17,1)
	self.initParamSettings.addWidget(self.response_threshold,18,1)
	self.initParamSettings.addWidget(self.AMPA_threshold,19,1)
	self.initParamSettings.addWidget(self.NMDA_threshold,20,1)
	self.initParamSettings.addWidget(self.DA_base,21,1)
	self.initParamSettings.addWidget(self.LTP_msn,22,1)
	self.initParamSettings.addWidget(self.LTD_msn,23,1)
	self.initParamSettings.addWidget(self.LTP_tan,24,1)
	self.initParamSettings.addWidget(self.LTD_tan,25,1)
	self.initParams1.setLayout(self.initParamSettings)

	self.toolbar = QToolBar()
	self.paramsButton = QPushButton("initParams/loopParams")
	self.paramsButton.pressed.connect(self.switchSettings)
	self.coreFunc.pressed.connect(self.switchCoreFuncs)
	self.toolbar.addWidget(self.paramsButton)
	self.toolbar.addWidget(self.coreFunc)
	self.simOptLayout.addWidget(self.toolbar,0,0)
	self.simOptLayout.addWidget(self.loopParams1,1,0)
	self.simOptLayout.addWidget(self.initParams1,1,0)
	self.simOptLayout.addWidget(self.loopParams2,1,0)
	self.simOptLayout.addWidget(self.initParams2,1,0)
	self.simOptions.setLayout(self.simOptLayout)

	# Optional initialization parameters for second coreFunc

	# Layout for graphing widgets (2.1)
	self.graphOptions = QWidget()
	self.graphOptions.setVisible(False)
	graphingSettings = QGridLayout()
	graphTitle = QLabel("<font size=6>Graphing Settings</font>")
	self.displayedGraph = QComboBox()
	self.displayedGraph.currentIndexChanged.connect(self.changePlot)
	self.graphParams = QStackedWidget()
	addFigureButton = QPushButton("Add Figure")
	addFigureButton.pressed.connect(self.addGraphOptions)
	removeFigures = QPushButton("Remove All")
	removeFigures.pressed.connect(self.initFigs)
	graphingSettings.addWidget(graphTitle,0,0,1,2,Qt.AlignCenter)
	graphingSettings.addWidget(removeFigures,1,0)
	graphingSettings.addWidget(addFigureButton,2,0)
	graphingSettings.addWidget(self.displayedGraph,2,1)
	graphingSettings.addWidget(self.graphParams,3,0,1,2,Qt.AlignCenter)
	self.graphOptions.setLayout(graphingSettings)
	self.initFigs()

    def initFigs(self):
	self.displayedGraph.clear()
	self.displayedGraph.addItem("Console")
	self.plots = {}
	self.opts = {}
	self.figCount = 0

    # Creates paired QComboBoxes with connected clear QPushButton (2.2.1)
    def genFuncBox(self,coreFuncText):
	for x in range(int(self.numCond.text())):
	    self.possibleFuncsMap[x] = QComboBox()
	    self.selectedFuncsMap[x] = QComboBox()
	    self.clearFuncs[x] = QPushButton("Clear")
	    funcs = ("simulate_acquisition_full","simulate_acquisition_partial",\
			"simulate_extinction","simulate_extinction_prf",\
			"simulate_reacquisition_2","simulate_reacquisition_8")
	    self.possibleFuncsMap[x].addItems(funcs)
	    self.possibleFuncsMap[x].activated.connect(self.pairComboBoxes(x))
	    ###
	    self.selectedFuncsMap[0].addItem(self.possibleFuncsMap[0].currentText())
	    ###
	    self.clearFuncs[x].pressed.connect(self.pairClearButton(x))
	    if coreFuncText == "coreFunc2":
		self.loopSettings.addWidget(self.possibleFuncsMap[x],x+7,0)
		self.loopSettings.addWidget(self.selectedFuncsMap[x],x+7,1)
		self.loopSettings.addWidget(self.clearFuncs[x],x+7,2)
	    elif coreFuncText == "coreFunc1":
		self.loopSettings2.addWidget(self.possibleFuncsMap[x],x+7,0)
		self.loopSettings2.addWidget(self.selectedFuncsMap[x],x+7,1)
		self.loopSettings2.addWidget(self.clearFuncs[x],x+7,2)

    def lambdaGenFuncBox(self, coreFuncText):
	return lambda : self.genFuncBox(coreFuncText)

    # Helper functions
    def pairComboBoxes(self,index):
	return lambda : self.addTrialFunc(index)

    def addTrialFunc(self,index):
	self.selectedFuncsMap[index].addItem(
				self.possibleFuncsMap[index].currentText())

    def pairClearButton(self,index):
	return lambda : self.clearBox(index)

    def clearBox(self,index):
	self.selectedFuncsMap[index].clear()

    def switchSettings(self):
	if self.coreFunc.text() == "coreFunc1":
	    if self.loopParams2.isVisible() == True:
		self.loopParams2.setVisible(False)
		self.initParams2.setVisible(True)
	    else:
		self.loopParams2.setVisible(True)
		self.initParams2.setVisible(False)
	elif self.coreFunc.text() == "coreFunc2":
	    if self.loopParams1.isVisible() == True:
		self.loopParams1.setVisible(False)
		self.initParams1.setVisible(True)
	    else:
		self.loopParams1.setVisible(True)
		self.initParams1.setVisible(False)

    def switchCoreFuncs(self):
	if self.coreFunc.text() == "coreFunc2":
	    self.loopParams1.setVisible(False)
	    self.initParams1.setVisible(False)
	    self.loopParams2.setVisible(True)
	    self.initParams2.setVisible(True)
	    self.coreFunc.setText("coreFunc1")
	elif self.coreFunc.text() == "coreFunc1":
	    self.loopParams2.setVisible(False)
	    self.initParams2.setVisible(False)
	    self.loopParams1.setVisible(True)
	    self.initParams1.setVisible(True)
	    self.coreFunc.setText("coreFunc2")

    # (2.3) Builds graphing option layout (GraphParams) for each plot
    def addGraphOptions(self):
	#for x in range(int(self.numGraphs.text())):
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
	for fig in self.opts:
	    for x in range(self.opts[fig].width*self.opts[fig].height):
		data.append(str(self.opts[fig].boxes[x].currentText()))
		try:
		    xRange.append(str(self.opts[fig].xRanges[x].text()))
		except AttributeError:
		    xRange.append("none")
		try:
		    zLabel.append(str(self.opts[fig].zLabel.text()))
		    zRange.append(str(self.opts[fig].zRange.text()))
		except AttributeError:
		    zLabel.append("none")
		    zRange.append("none")

	n = 0
	for i,figure in enumerate(self.plots): # each figure
	    try:
		# each plot inside a figure
		for x in range(self.opts[figure].width*self.opts[figure].height):
		    self.plots[figure].setGraphParams(self.dirPath,x,
			    data[i+x+n],xRange[i+x+n],zLabel[i+x+n],zRange[i+x+n]);
		n += 1
	    except AttributeError: print "GUI: setGraphParams exception"

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
    gui = GUI()
    gui.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

