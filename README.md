Simulator(R) Version 1.0 7/31/14
================================

*OVERVIEW*

This package provides a GUI for customizing and analyzing models for simulating cognitive action (instrumental learning).
    * Open & run .c files:
	- The only prerequisite of the selected .c file is that it writes data to files that do not include a "." in their name.
	- As of this version, the `filterDataFiles()` method is intended for use with instrumental learning models similar to the one specified in coreFunc.c...
	  if other models are used, `dataBoxes` may not be filled properly or at all, particularly when the data files have a higher variance in length than 2.
    * Generate custom simulations via simulator settings widget that supplies coreFunc.c with specifications:
	- These specifciation include: # of conditons, simulations, trials, time steps, and optionally a list of initialization values for parameters.
	- If custom values for init params aren't chosen, then the hard coded set of init params are used.
	- The # of simulations, trials, & time steps have initialized values, but the user must specifiy the # of conditions and select the trail functions for each.
    * However data is generated, plot it with an embedded matplotlib canvas:
	- The graphing settings widget mandates that users specify the # of plots prior to running the simulation & the type of plots either prior or after running.
	- After the simulation has been run, users may manipulate the plots via the different user inputs determined by the `styleSelect` QComboBox.

*DETAILS*

GUI:
Once the GUI has been initialized, users may either open an existing .c file or utilize the simulator settings to customize the execution of the coreFunc.c file (via argv[]). In this version, the user must create plots via the graphing settings prior to running the simulation; otherwise, fillDataBoxes() won't have any dataBoxes to fill. If the user has not opened a .c file, they must save before running the simulation to set `self.dirPath`. GUI.py makes use of the subprocess package to execute the selected .c file or coreFunc.c in the command line. During the execution of the `save_average_essentials()` function, data are written to files of the name of the data prepended with `self.dirPath` and appended with `numConditon` (starting with 0). If the user has saved the file, indicating that the simulation is to be custom generated, then all the simulator settings are appended as arguments to the command line execution of coreFunc.c. After running the simulation, all the files in the open/save directory are filtered (excluding files with "." in them) and categorized by length so they may be added to their respective dataBoxes.

GraphParams:
This class is a QWidget that initializes with a single QComboBox called `styleSelect`, populated with three types of graph options: "Trial Plot", "Time Plot", and "Surface Plot". When the user selects one of these, the initOptions() method is called which generates a layout with the respective fields for manipulating plots.

MplGrapher:
This class is a QWidget that embeds MatPlotLib in the GUI. Its `setGraphParams()` method takes arguments from GUI's `plot()` method. The GraphParams instance in question will dictate how it's respective instance of MplGrapher will handle setGraphParams(). Basically, MplGrapher is responsible for deciding whether to render a 3D or 2D plot.

*REQUIRED DEPENDENCIES*
* PySide
* Matplotlib
* NumPy

*TAKE NOTE*

* Change line 195 to be your path to coreFunc.c.
* By convention, data files can't have "." in them.

*ISSUES w/ GUI.py*

* OpenFile() doesn't populate condition information.
* Exception handling isn't exactly tidy yet. Exception/error printing isn't
 uniform either...some print to command line console, others print to GUI
 embedded console (QTextEdit).
* FilterDataFiles() works by creating a list of len(data) & creating two
 variables, dataLength1 & dataLength2, which are the min & max of this list.
 Since the program isn't perfected, the distribution of lengths of data isn't
 uniform (either numTrial length or numTrial * numSteps length), so the dataBox
 for each respective plot (instance of GraphParams) doesn't have all the data
 files added.
* When GUI is updated w/ new layout (as when addGraphOptions() or genFuncBox()
 is called), old layout isn't deleted...the new one is simply superimposed.
 This means that the old layout will still be visible if the new layout takes
 up less space.
* CyclePlot() sometimes doesn't work...just click displayedGraph box to get it
 working again.
* AddGraphOptions() in the case of opening a file doesn't execute properly.
