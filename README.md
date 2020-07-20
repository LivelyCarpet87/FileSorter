# Function/Purpose

This is a file sorter written in python3. It sorts all the files in a given directory according to rules listed by the user. It sorts files into folders according to a tag written into file names. For example, if `ROB` has been defined as the tag for the `Robotics` folder, files with names containing `ROB_` such as `ROB_pushbot.java` will be sorted into the `Robotics` folder. It also has the ability to ignore files according to certain strings in filenames or file-paths according to a specific and a global Ignored.config file when sorting files in folders. 

# OS Compatibility

It has been tested on MacOS Mojave and should be compatible with all MacOS. It has not been tested on other Operating Systems but I presume it may work because of the design of the Python3 OS package. Please open an issue on GitHub to let me know if it works or doesn't work on any specific OS. 

# Install

## 1. macOS

### Install FileSorter Application

Follow this link to the [releases page]() and select the application version of the macOS .pkg files. Once downloaded, double click the pkg file to open and a guided install should begin. Upon opening the installed app, a terminal window should apppear with the interface. 

### Install FileSorter Command Line Version

Follow this link to the [releases page]() and select the CLI version of the macOS .pkg files. Once downloaded, double click the pkg file to open and a guided install should begin. Once installation is complete, open Terminal (Tip: Spotlight search Terminal to launch it) and type `FileSorter` and hit enter. The main menu should appear. 

## 2. Windows

Follow this link to the [releases page]() and download the .exe file. Save it to a location you prefer and open it by double clicking. A command prompt should appear with the main window. 

## 3. Ubuntu

Follow this link to the [releases page]() and download the Ubuntu binary file. Save it to a loaction you prefer with the name FileSorter. Opening it via a terminal session or running it should show the main menu. 

## 4. Python Scripts (For command line users only)
### Prerequisites
Git: [Download git here](https://git-scm.com/)

Python3: To install python3 on MacOS using Homebrew, run `brew install python3`

(To get Homebrew, paste `/bin/bash -c &quot;$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)&quot;` into terminal and hit enter. The program will guide you through the steps)

### Steps of Installation

1. `git clone https://github.com/LivelyCarpet87/FileSorter`

2. `cd FileSorter`

3. `pip3 install -r requirements.txt`

# Usage

Here this guide really diverges:

1. [Guide for absolute beginners]()
2. [Guide for beginners]() (User can: copy, paste, and modify terminal commands when guided)
3. [Guide for budding programmers]() (User can: understand working directories and use basic terminal commands)
4. [Guide for programmers]() (User can: work with configuration files, command line arguments, and advanced commands)

# Common Errors
## macOS
1. User can't find the installed app:
	Please verify that you have installed the application version and not the CLI version. The CLI version has "CLI" in its name. If this does not solve your issue, please open an new issue [here](). 
2. Command not found:
	Please make sure you installed the CLI version and not the application version. Also, please make sure your `$PATH` vairable contains `/usr/local/bin`. If this does not solve your issue, please open an new issue [here]().

# Issues?

If some function does not work as expected, or if you have any questions, feel free to open an issue. When reporting on a potential bug, please increase verbosity with `-vv` flag to enter debug level of STDOUT logging. 

# To-Do

- [x] Add an interactive config setup script

- [x] Add a script to automatically rename files

- [x] Wrap into an application for automation. 

- [x] Add logging

- [x] Add verbosity control

- [ ] Compile into a suite of terminal commands for better automation

- [ ] Improve the automation capabilites of the apps

- [ ] Optimize code