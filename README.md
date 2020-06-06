# Function/Purpose

This is a file sorter written in python3. It sorts all the files in a given root directory according rules in a configuration file and some Ignored.config files. It sorts files into folders according to a tag written into file names. For example, if `ROB` has been defined as the tag for the `Robotics` folder, files with names containing `ROB_` such as `ROB_pushbot.java` will be sorted into the `Robotics` folder. It also has the ability to ignore files according to certain strings in filenames or file-paths according to a specific and a global Ignored.config file when sorting files in folders. 

# OS Compatibility

It has been tested on MacOS Mojave and should be compatible with all MacOS. It has not been tested on other OS but I presume it may work. Please open an Issue to let me know if it works or doesn't work on other OS. 

# Install

## Prerequisites

Git: [Download git here](https://git-scm.com/)

Python3: To install python3 on MacOS using Homebrew, run `brew install python3`

(To get Homebrew, paste `/bin/bash -c &quot;$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)&quot;` into terminal and hit enter. The script will guide you through the steps)

## Steps of Installation

To install the required packages, run `pip3 install -r requirements.txt`

1. `git clone https://github.com/LivelyCarpet87/FileSorter`

2. `cd FileSorter`

3. `pip3 install -r requirements.txt`

# Usage

## Set Up

1. `python3 initFileSorter.py --rootDir /Path/To/Root/Of/Folders/To/Sort`
   
   This generates the config files for you. If the --rootDir is not given, the script will assume the working directory of the terminal session to be the rootDir. If --genBinIgnored is included, it will generate a folder-specific Ignored.config file for each folder.
   
   **Quick Tip: Drag the rootDir folder into your terminal window to avoid typing it.**

2. Edit the generated configuration files in the /fileSortConfiguration folder in your /Path/To/Root/Of/Folders/To/Sort`
   
   Remember to change the value of `rootstatus` to `ON` and to keep the `[Bin#]` sequential. `alternativeTag` can be deleted in the config file. 

## Execution

Run `python3 FileSorter.py --rootDir /Path/To/Root/Of/Folders/To/Sort`

1. Files without the tag required for a folder and not ignored by any of the Ignored.config files will be moved into the Misplaced folder (you can rename this in the Config). If the Misplaced folder does not exist, it will be created. 

2. Files in the Misplaced folder with the right tag and not ignored by any of the Ignored.config files will be moved into the right folder. 

3. If the Misplaced folder is empty, it will be removed by default. 

# Config File Explained

## Example Config File

> [GlobalSettings]
> 
> \# root directory of bins to be sorted
> 
> rootdir = /Users/livelycarpet87/Google Drive/2020-2021 Semester 1
> 
> \# enable filesort? (global)
> 
> rootstatus = OFF
> 
> \# name for directory of misplaced files
> 
> misplaceddirname = Misplaced
> 
> \# remove misplaced directory when it is empty?
> 
> removemisplaceddir = ON
> 
> [Bin1]
> 
> \# user-given name for this bin
> 
> name = Misc
> 
> \# enable this bin?
> 
> active = ON
> 
> \# name of folder for this bin
> 
> dirname = Misc
> 
> \# tag for files in this bin.
> 
> \# file called randchar_misc_randchar.randtype will be put into misc bin.
> 
> \# filename must contain tag_ in its name to be put into bin
> 
> tag = MISC
> 
> \# alternative tag for files in this bin.
> 
> tagalternative = Misc
> 
> \# ignore misplaced files belonging to this bin in this bin or misplaved folder?
> 
> ignoremisplaced = OFF

## Explanation

### [Global Settings]

This section contains all the settings used for each bin and the program overall. 

### rootdir

RootDir is the folder where all the folders (referred to as bins from now on for simplicity) are. The bins should all be sub-directories to this root directory. 

### rootstatus

RootStatus is the Boolean value that enables the script. It defaults to false to prevent the user from executing without checking the config. If it is false, the script exits without making changes. 

### misplaceddirname

MisplacedDirName is the name for the folder where all the files that don't belong in each bin are moved to. Files belonging to bins will be placed back to their respective bins from this folder. This folder is removed once it is empty by default. 

### removemisplaceddir

RemoveMisplacedDir removes the folder for misplaced files when it is empty. It is on by default. 

---

### [Bin1]

This section contains settings specific to Bin1. Bins must be named in sequential numerical order for the program to parse properly. 

### name

This is a value for the user to set to recognize this bin, since the format Bin# is easier to parse but harder to remember which. It defaults to name of the folder when generated. 

### active

If this is false, any processing for this bin is skipped. This defaults to True. 

### dirname

DirName is the name the bin. Its value defaults to the name of the folder. 

### tag

Tag is the tag for the bin. All file belonging to this bin have `TAG_`  (or the alternative tag) in their name, such as containing `MISC_` in the filename for the Misc folder. It defaults to the uppercase first 4 letters of the name of the bin. 

### tagalternative

TagAlternative is the alternative tag for the bin. All file belonging to this bin have `ALTTAG_` (or the primary tag, see above) in their name, such as containing `Misc_` in the filename for the Misc folder. It defaults to the first 4 letters of the name of the bin and is not uppercased automatically. This attribute can be deleted without effects. 

### ignoremisplaced

IgnoreMisplaced will cause misplaced files to be mentioned but not moved when enabled. It is OFF by default.  

---

### [Bin2]

This is the beginning of the next bin. The number must be +1 of the previous bin. 

---

## About the Ignored.config Files

The globalIgnored.config file is applied globally. The nameIgnored.config file is applied to the specific bin with the corresponding name. For example, globalIgnored.config applies to the Misc and the Robotics bins, but MiscIgnored.config only applies to the Misc bin. 



In the file is a set of strings separated by newlines. Each line is a string. If any file's name or absolute path contains this string, it will be ignored. It is not needed to add files beginning with '.' because they are ignored by default. Needless to say, any string contained in the rootDir would cause all the files to match and be ignored. 

# Issues?

If some function does not work as expected, or if you have any questions, feel free to open an issue. 
