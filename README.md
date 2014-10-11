Simulator(R) Version 1.1 10/10/14
================================

*OVERVIEW*

This package provides a GUI for customizing and analyzing models for simulating cognitive action (instrumental learning).
* Open & run .c files:
    - The only prerequisite of the selected .c file is that it writes data to files that do not include a "." in their name.
    - As of this version, the `filterDataFiles()` method is intended for use with instrumental learning models similar to the one specified in coreFunc.c (having trials and time steps per trial)...
      if other models are used, the proper graphing parameters may not be instantiated properly or at all, particularly when the data files have a higher variance in length than 2.
* Generate custom simulations via simulator settings widget that supplies coreFunc.c with specifications:
    - These specifciation include: number of conditons, simulations, trials, time steps, and optionally a list of initialization values for parameters.
    - If custom values for init params aren't chosen, then the hard coded set of init params are used.
    - The number of simulations, trials, & time steps have initialized values, but the user must specifiy the number of conditions and select the trail functions for each.
* However data is supplied, plot it with an embedded matplotlib canvas:
    - The graphing settings widget allows the user to add figures with the push of a button. If the user selects "2D Plot" or "3D Plot" from the graphing settings toolbar prior to adding a figure, then that figure will only support that type of plot.
    - Once the figure has been added, the user then supplies the dimensions for the embedded subplots: (1,1), (2,2), (3,1), etc.
    - Once this parameter has been supplied and the user pressed `enter`, the appropriate number of databoxes will be generated and filled with all the data files (or only time step data if `3D Plot` is selected prior to figure creation). 
    - If the user chooses to plot in 2D, then after selecting the data file to plot, different graphing parameters will become available to the user based on the length of that data file. Time step data will include extra parameters for viewing specific trials of the simulation, and for specifying a custom range for the x-axis (i.e. you want to plot 2 trials consecutively).

*DETAILS*

GUI:
* Once the GUI has been initialized, users may either open an existing .c file or utilize the simulator settings to customize the execution of the coreFunc.c file (via argv[]). If the user has not opened a .c file, they must save before running the simulation to set `self.dirPath`. GUI.py makes use of the subprocess package to execute the selected .c file or coreFunc.c. During the execution of the `save_average_essentials()` function, data are written to files of the name of the data prepended with `self.dirPath` and appended with `numConditon` (starting with 0). If the user has saved the file, indicating that the simulation is to be custom generated, then all the simulator settings are appended as arguments to the command line execution of coreFunc.c. After running the simulation, all the files in the open/save directory are filtered (excluding files with "." in them) and categorized by length so they may be added to their respective dataBoxes depending on the type of plot the user chooses to graph.

GraphParams:
* This class is a QWidget that initializes graphing parameters for the instanse of MplGrapher that it is paired with. When the user selects a data file from a databox, the initOptions() method is called which generates a layout with the respective fields for manipulating plots.

MplGrapher:
* This class is a QWidget that embeds MatPlotLib in the GUI. Its `setGraphParams()` method takes arguments from GUI's `plot()` method. The GraphParams instance that it is paired with will dictate how this instance MplGrapher will handle setGraphParams(). Basically, MplGrapher is responsible for deciding whether to render a 3D or 2D plot. It is also responsible for adjusting embedded subplots.

*REQUIRED DEPENDENCIES*
* PySide
* Matplotlib
* NumPy

*TAKE NOTE*

* Change lines in GUI.py's run() function so that the first item in the list `cmd` is your path to the coreFunc.c files.
* By convention, data files can't have "." in them.

*ISSUES w/ GUI.py*

* `openFile()` doesn't populate condition information. Similarly `saveFile()` doesn't work yet. It doesn't make sense to fully implement these until the project is in its final stages.
* Exception handling isn't exactly tidy yet. Exception/error printing isn't
 uniform either...some print to command line console, others print to GUI
 embedded console (QTextEdit).
* When GUI is updated w/ new layout (as when addGraphOptions() or genFuncBox()
 is called), old layout isn't deleted...the new one is simply superimposed.
 This means that the old layout will still be visible if the new layout takes
 up less space. Deleting the figures that have been generated will eliminate this issue.
* `cyclePlot()` sometimes doesn't work...just click displayedGraph box to get it
 working again.

