# Basics

This section targets people who have a more limited understanding of the command line. All commands, `in this format`, are presumed to be run in terminal. Terminal can be found on MacOS by typing "terminal" in Spotlight. 

A **directory** is a location or a folder. It has a path, which is the list of folders leading to the last folder.

# Function/Purpose

This is a file sorter written in python3. It sorts all the files in a given directory according rules listed by the user. It sorts files into folders according to a tag written into file names. For example, if `ROB` has been defined as the tag for the `Robotics` folder, files with names containing `ROB_` such as `ROB_pushbot.java` will be sorted into the `Robotics` folder. It also has the ability to ignore files according to certain strings in filenames or file-paths according to a specific and a global Ignored.config file when sorting files in folders. 

# OS Compatibility

It has been tested on MacOS Mojave and should be compatible with all MacOS. It has not been tested on other OS but I presume it may work. Please open an issue on GitHub to let me know if it works or doesn't work on other OS. 

# Install

## Prerequisites

Git: [Download git here](https://git-scm.com/)

Python3: To install python3 on MacOS using Homebrew, run `brew install python3`

(To get Homebrew, paste `/bin/bash -c &quot;$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)&quot;` into terminal and hit enter. The program will guide you through the steps)

## Steps of Installation

To install the required packages, run `pip3 install -r requirements.txt`

1. `git clone https://github.com/LivelyCarpet87/FileSorter`

2. `cd FileSorter`

3. `pip3 install -r requirements.txt`

# Usage

## Set Up

1. `python3 initFileSorter.py --rootDir /Absolute/Path/To/Root/Of/Folders/To/Sort`
   
   This generates the config files for you. If the --rootDir is not given, the program will assume the working directory of the terminal session to be the rootDir. If --genBinIgnored is included, it will generate a folder-specific Ignored.config file for each folder.
   
   **Quick Tip: Drag the folder into your terminal window instead of typing it.**

2. Edit the generated configuration files in the /fileSortConfiguration folder in your /Path/To/Root/Of/Folders/To/Sort`
   
   Remember to change the value of `rootstatus` to `ON` and to keep the `[Bin#]` sequential. `alternativeTag` can be deleted in the config file. 

## Execution

Run `python3 FileSorter.py --rootDir /Absolute/Path/To/Root/Of/Folders/To/Sort`

1. Files without the tag required for a folder and not ignored by any of the Ignored.config files will be moved into the Misplaced folder (you can rename this in the Config). If the Misplaced folder does not exist, it will be created. 

2. Files in the Misplaced folder with the right tag and not ignored by any of the Ignored.config files will be moved into the right folder. 

3. If the Misplaced folder is empty, it will be removed by default. 

## Behavior

- Files that can't be sorted into any bin will remain in the Misplaced folder. 

- Files should be named as `Tag_name.type` for sorting. Acceptable alternative naming scheme is `name_Tag.type`. Note the use of the underscore is necessary. 

- Files (other than the .DS\_Store in the Misplaced folder) will not be deleted unless a bug occurs.

# Config File

The following is an example of an auto-generated file, the bolded parts can be edited by the user. 

> [GlobalSettings]
> 
> \# root directory of bins to be sorted
> 
> rootdir = **/Users/livelycarpet87/Google Drive/2020-2021 Semester 1**
> 
> \# enable filesort? (global)
> 
> rootstatus = **OFF**
> 
> \# name for directory of misplaced files
> 
> misplaceddirname = **Misplaced**
> 
> \# remove misplaced directory when it is empty?
> 
> removemisplaceddir = **ON**
> 
> **[Bin1]**
> 
> \# user-given name for this bin
> 
> name = **Misc**
> 
> \# enable this bin?
> 
> active = **ON**
> 
> \# name of folder for this bin
> 
> dirname = **Misc**
> 
> \# tag for files in this bin.
> 
> \# file called MISC\_filename.filetype will be put into misc bin.
> 
> \# filename must contain tag_ in its name to be put into bin
> 
> tag = **MISC**
> 
> \# alternative tag for files in this bin. 
> 
> tagalternative = **Misc**
> 
> \# ignore misplaced files belonging to this bin in this bin or misplaced folder?
> 
> ignoremisplaced = **OFF**
> 
> \# Group versions?
> 
> groupversions = **ON**
> 
> \# Any file with this number of versions or more will be grouped.
> 
> groupthreshold = **3**

### Things User May Want To Change

1. rootsort: Set to ON to enable the sorting

2. groupVersions: The file-sorter will combine the files with different version numbers in the same bin together. For example, `ROB_myCodeV1.0.java`, `ROB_myCodev1.2.java`, and  `ROB_myCodeV2.0.java`  will be all grouped to a folder called `myCode` in the same directory when this is enabled. 

3. groupthreshold: This is the minimal number of versions that need to exist before the files are grouped together. 

4. active: This sets whether the bin has files sorted in/out. Once off, the bin is skipped. 

5. name: The names for each file bin can be changed to be different from the folder's name. 

6. tag: The user can edit the tag if they feel like it. It can be more or less than 4 characters. Just remember to name the files as `TAG_Filename.filetype`

7. tagalternative: It is just like tag. Delete it if you do not want it. 

8. ignoremisplaced: Set this to on for a dry run. 

## About the Ignored.config Files

The globalIgnored.config file is applied globally. The nameIgnored.config file is applied to the specific bin with the corresponding name. For example, globalIgnored.config applies to the Misc and the Robotics bins, but MiscIgnored.config only applies to the Misc bin. 

In the file is a set of strings separated by newlines. Each line is a string. If any file's name or absolute path contains this string, it will be ignored. It is not needed to add files beginning with '.' because they are ignored by default. Needless to say, any string contained in the rootDir would cause all the files to match and be ignored. 

# Issues?

If some function does not work as expected, or if you have any questions, feel free to open an issue. 
