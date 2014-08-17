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
	self.w = QWidget()
	self.setCentralWidget(self.w)
        self.opening = False
	self.initUI()

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
	    self.plot()
            self.opening = False

    # Writes sim/graph values & data files to .sim (1.2)
    def saveFile(self):
	self.filePath, _= QFileDialog.getSaveFileName(self, 'save file', \
	     '~/', 'Simulations (*.sim)' )
	fileSplit = self.filePath.split("/")
	self.dirPath = "/".join(fileSplit[:-1])
	title = fileSplit[-1]
	self.w.setWindowTitle(title)
	# Doesn't yet grab condition values from self.runFuncs
	self.simValues = [str(self.numCond.text()),str(self.numSim.text()),
			str(self.numTrials.text()),str(self.numSteps.text()),
				str(self.dirPath),str(self.numGraphs.text())]
	self.graphValues = []
	# Grabs graphing values...each segment is prepended with a string
	# denoting what type of GraphParams instance to populate to
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
	with open(self.filePath, 'w') as f:
	    for item in self.simValues:
		f.write(str(item)+"\n")
	    f.write("\n")
	    for item in self.graphValues:
		f.write(str(item)+"\n")
	    f.write("\n")
	    for item in self.files:
		f.write(str(item)+"\n")

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
		cmd = ['/Users/aweeeezy/bin/ivry/Simulator/a.out']
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
	# If dataBox (first) is empty, categorize files by length
	# If !empty, user reselected a different # of graphs to add
	# so recategoriztion is not necessary
	if self.opts["Fig1"].dataBox.count() == 0:
	    self.dataLengths = []
	    for _file in self.files:
		with open(self.dirPath+'/'+_file) as f:
		    data = f.readlines()
		    print "Length of",_file,"is",len(data)
		    if len(data) != 0:
			self.dataLengths.append(len(data))
	    # These 3 *should* work; but, for reasons further down the
	    # line, they may not (see README for details)
	    self.dataLength_1 = min(self.dataLengths)
	    self.dataLength_2 = max(self.dataLengths)
	    self.timeSteps = self.dataLength_2/self.dataLength_1
	    #self.dataLengths_1 = int(self.numTrials.text())*int(self.numCond.text())
	    #self.dataLengths_2 = int(self.numSteps.text())*int(self.dataLengths_1)
	    #self.timeSteps = int(self.numSteps.text())
	    self.trialData = []
	    self.timeStepData = []
	    for _file in self.files:
		print "opening", _file
		with open(self.dirPath+'/'+_file) as f:
		    data = f.readlines()
		if len(data) == self.dataLength_1:
		    print "\tputting data in trialData"
		    self.trialData.append(_file)
		elif len(data) == self.dataLength_2:
		    print "\tputting data in timeStepData"
		    self.timeStepData.append(_file)
	    self.fillDataBoxes()

    # Fills dataBoxes w/ files (size based) according to styleSelect (1.5.4)
    def fillDataBoxes(self):
        try:
            for fig in self.opts:
                if self.opts[fig].styleSelect.currentText() == 'Trial Plot':
                    self.console.insertPlainText("\n\nAdding to dataBox:\n\t"+\
                    '\n\t'.join('%s' % (x) for x in self.trialData))
                    self.opts[fig].dataBox.addItems(self.trialData)
                elif self.opts[fig].styleSelect.currentText() == 'Time Plot':
                    self.console.insertPlainText("\n\nAdding to dataBox:\n\t"+\
                    '\n\t'.join('%s' % (x) for x in self.timeStepData))
                    self.opts[fig].dataBox.addItems(self.timeStepData)
                    self.opts[fig].changeTrial(steps=self.timeSteps,\
                                                       trials=self.dataLength_1)
		# Until I get a better feel for how suface plot data will be
		# structured, this adds all files to surface plot dataBox
                elif self.opts[fig].styleSelect.currentText() == 'Surface Plot':
                    self.opts[fig].dataBox.addItems(self.files)
        except AttributeError:
	    self.console.insertPlainText("Double check inputs & save file first.\n")


  ###					     ###
  ### (2) Labels/layouts for setting options ###
  ###	    layouts & support functions	     ###

    def optionsInit(self):
	# Layout for simulator widgets (2.2)
	#self.simOptions = QStackedWidget()
	self.simOptions = QWidget()
	self.simOptLayout = QGridLayout()
	self.loopParams1 = QWidget()
	self.initParams1 = QWidget()
	self.loopParams2 = QWidget()
	self.initParams2 = QWidget()
	self.initParams1.setVisible(False)
	self.loopParams2.setVisible(False)
	self.initParams2.setVisible(False)

	# Loop settings
	self.loopSettings = QGridLayout()
	loopTitle = QLabel("<font size=6>Loop Parameters</font>")
	numConditions = QLabel("Conditions:")
	numSim = QLabel("Simulations:")
	numTrials =  QLabel("Trials:")
	numSteps =  QLabel("Steps:")
	self.numCond = QLineEdit()
	self.numCond.returnPressed.connect(self.genFuncBox)
	self.numSim = QLineEdit("1")
	self.numTrials = QLineEdit("300")
	self.numSteps = QLineEdit("3000")

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
	self.loopParams1.setLayout(self.loopSettings)

	# Optional initialization parameters
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

	#self.simOptions.addWidget(self.loopParams1)
	#self.simOptions.addWidget(self.initParams1)
	self.toolbar = QToolBar()
	self.paramsButton = QPushButton("initParams/loopParams")
	self.coreFunc = QPushButton("coreFunc2")
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

	# Layout for graphing widgets (2.1)
	self.graphOptions = QWidget()
	self.graphOptions.setVisible(False)
	graphingSettings = QGridLayout()
	graphTitle = QLabel("<font size=6>Graphing Settings</font>")
	numGraphs = QLabel("Plots:")
	self.numGraphs = QLineEdit("1")
	self.numGraphs.textChanged.connect(self.addGraphOptions)
	self.displayedGraph = QComboBox()
	self.displayedGraph.currentIndexChanged.connect(self.changePlot)
	self.graphParams = QStackedWidget()
	graphingSettings.addWidget(graphTitle,0,0,1,2,Qt.AlignCenter)
	graphingSettings.addWidget(self.displayedGraph,1,1)
	graphingSettings.addWidget(numGraphs,2,0)
	graphingSettings.addWidget(self.numGraphs,2,1)
	graphingSettings.addWidget(self.graphParams,3,0,1,2,Qt.AlignCenter)
	self.graphOptions.setLayout(graphingSettings)

    # Creates paired QComboBoxes with connected clear QPushButton (2.2.1)
    def genFuncBox(self):
	for x in range(int(self.numCond.text())):
	    self.possibleFuncsMap[x] = QComboBox()
	    self.selectedFuncsMap[x] = QComboBox()
	    self.clearFuncs[x] = QPushButton("Clear")
	    funcs = ("simulate_acquisition_full","simulate_acquisition_partial",\
			"simulate_acquisition","simulate_extinction",\
			"simulate_extinction_ext","simulate_extinction_prf",\
			"simulate_reacquisition_2","simulate_reacquisition_8")
	    self.possibleFuncsMap[x].addItems(funcs)
	    self.possibleFuncsMap[x].activated.connect(self.pairComboBoxes(x))
	    self.clearFuncs[x].pressed.connect(self.pairClearButton(x))
	    self.loopSettings.addWidget(self.possibleFuncsMap[x],x+6,0)
	    self.loopSettings.addWidget(self.selectedFuncsMap[x],x+6,1)
	    self.loopSettings.addWidget(self.clearFuncs[x],x+6,2)

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
	self.plots = {}
	self.opts = {}
	self.displayedGraph.clear()
	self.displayedGraph.addItem("Console")
	for x in range(int(self.numGraphs.text())):
	    _next = "Fig"+str(x+1)
	    graphInstance = MplGrapher()
	    paramsInstance = GraphParams(self,graphInstance)
	    self.plots[_next] = graphInstance
	    self.opts[_next] = paramsInstance
            if self.opening == True:
                value = self.graphValues.pop(1)
                self.opts[_next].styleSelect.setEditText(value)
	    else:
                self.opts[_next].styleSelect.setCurrentIndex(0)
	    self.displayedGraph.addItem(_next)
	    self.display.addWidget(graphInstance.getFig())
	    self.graphParams.addWidget(paramsInstance)
	self.displayedGraph.setCurrentIndex(0)
	# May be redundant...just call fillDataBoxes()?
        try:
            for fig in self.opts:
                if self.opts[fig].styleSelect.currentText() == 'Trial Plot':
                    self.opts[fig].dataBox.addItems(self.trialData)
                elif self.opts[fig].styleSelect.currentText() == 'Time Plot':
                    self.opts[fig].dataBox.addItems(self.timeStepData)
                elif self.opts[fig].styleSelect.currentText() == 'Surface Plot':
                    self.opts[fig].dataBox.addItems(self.files)
        except AttributeError:
            self.console.insertPlainText("Run the simulation to fill dataBox")

    # (2.4) Generate plots from MplGrapher instances
    def plot(self):
	data = []
	xRange = []
        zLabel = []
        zRange = []
	for fig in self.opts:
	    data.append(str(self.opts[fig].dataBox.currentText()))
	    try:
		xRange.append(str(self.opts[fig].xRange.text()))
	    except AttributeError:
		xRange.append("none")
            try:
                zLabel.append(str(self.opts[fig].zLabel.text()))
                zRange.append(str(self.opts[fig].zRange.text()))
            except AttributeError:
                zLabel.append("none")
                zRange.append("none")

	for i,figure in enumerate(self.plots):
	    try:
		self.plots[figure].setGraphParams(self.dirPath, data[i], \
						xRange[i],zLabel[i],zRange[i]);
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
	    self.display.setCurrentWidget(self.console)

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
	self.displayedGraph.addItem("Console")



def main():
    app = QApplication(sys.argv)
    gui = GUI()
    gui.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

