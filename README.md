Simulator
=========

Package for customizing and analyzing models for simulating cognitive action (instrumental learning)

*OVERVIEW*

GUI:
Once the GUI has been initialized, users may either open an existing .c file or utilize the simulator settings to customize the execution of the coreFunc.c file included (via argv[]). At this time, the user must create plots via the graphing settings prior to running the simulation; otherwise, fillDataBoxes() won't have any dataBoxes to fill. If the user has not opened a .c file, they must save before running the simulation to set dirPath. GUI.py makes use of the subprocess package to execute the selected .c file or coreFunc.c in the command line. If the user has saved the file, then all the simulator settings are appended as arguments for the command line execution of the coreFunc.c file. After running the simulation, all the files in the open/save directory are filtered (excluding files with "." in them) and categorized by length so they may be added to their respective dataBoxes. 

GraphParams:
This class is a QWidget that initializes with a single QComboBox called styleSelect, populated with three types of graph options: "Trial Plot", "Time Plot", and "Surface Plot". When the user selects one of these, the initOptions() method is called which generates a layout with the respective fields for plotting.

MplGrapher:
This class is a QWidget that embeds MatPlotLib in the GUI. Its setGraphParams() method takes arguments from GUI's plot() method. The GraphParams instance in question will dictate how it's respective instance of MplGrapher will handle setGraphParams(). Basically, MplGrapher is responsible for deciding whether to use a 3D or 2D plot, and drawing the plots.

*ISSUES w/ GUI.py*

--- Take note ---
* Change line 195 to be the path to coreFunc.c.
* By convention, data files can't have "." in them.
* FilterDataFiles() works by creating a list of len(data) & creating two
 variables, dataLength1 & dataLength2, which are the min & max of this list.
 Since the program isn't perfected, the distribution of lengths of data isn't
 uniform (either num_trial length or num_trial * num_steps length), so the dataBox
 for each respective plot (instance of GraphParams) doesn't have all the data
 files added.

--- Known solution ---
* OpenFile() doesn't populate condition information.
* Exception handling isn't exactly tidy yet. Exception/error printing isn't
 uniform either...some print to command line console, others print to GUI
 embedded console (QTextEdit).

--- Unknown solution ---
* When GUI is updated w/ new layout (as when addGraphOptions() or genFuncBox()
 is called), old layout isn't deleted...the new one is simply superimposed.
 This means that the old layout will still be visible if the new layout takes
 up less space.
* CyclePlot() sometimes doesn't work...just click displayedGraph box to get it
 working again.
* AddGraphOptions() in the case of opening a file doesn't execute properly.
