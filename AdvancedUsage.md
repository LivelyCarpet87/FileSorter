
## Set Up

1. `python3 initFileSorter.py --rootDir /Absolute/Path/To/Root/Of/Folders/To/Sort`
   
   This generates the config files for you. If the --rootDir is not given, the program will assume the working directory of the terminal session to be the rootDir. If --genBinIgnored is included, it will generate a folder-specific Ignored.config file for each folder.
   
   **Quick Tip: Drag the folder into your terminal window instead of typing it.**

2. Edit the generated configuration files in the /fileSortConfiguration folder in your /Path/To/Root/Of/Folders/To/Sort`
   
   Remember to change the value of `rootstatus` to `ON` and to keep the `[Bin#]` sequential. `alternativeTag` can be deleted in the config file. 
   
3. If you have any directories with files already existing, use `python3 fileRename.py` to interactively rename all files with the tags you wish. 

## Execution

Run `python3 FileSorter.py --rootDir /Absolute/Path/To/Root/Of/Folders/To/Sort`

1. Files without the tag required for a folder and not ignored by any of the Ignored.config files will be moved into the Misplaced folder (you can rename this in the Config). If the Misplaced folder does not exist, it will be created. 

2. Files in the Misplaced folder with the right tag and not ignored by any of the Ignored.config files will be moved into the right folder. 

3. If the Misplaced folder is empty, it will be removed by default. 

## Behavior

- Files that can't be sorted into any bin will remain in the Misplaced folder. 

- Files should be named as `Tag_name.type` for sorting. Acceptable alternative naming scheme is `name_Tag.type`. Note the use of the underscore is necessary. 

- Files (other than the .DS\_Store in the Misplaced folder) will not be deleted.

- Files may be renamed to prevent duplicate files having the same name in the same folder, and the renaming process will be logged under INFO. It will also be displayed in STDOUT when the `-v` or `-vv` tags are enabled. 

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

1. rootstatus: Set to ON to enable the sorting

2. groupVersions: The file-sorter will combine the files with different version numbers in the same bin together. For example, `ROB_myCodeV1.0.java`, `ROB_myCodev1.2.java`, and  `ROB_myCodeV2.0.java`  will be all grouped to a folder called `myCode` in the same directory when this is enabled. 

3. groupthreshold: This is the minimal number of versions that need to exist before the files are grouped together. 

4. active: This sets whether the bin has files sorted in/out. Once off, the bin is skipped. 

5. name: The names for each file bin can be changed to be different from the folder's name. 

6. tag: The user can edit the tag if they feel like it. It can be more or less than 4 characters. Just remember to name the files as `TAG_Filename.filetype`

7. tagalternative: It is just like tag. Delete it if you do not want it. 

8. ignoremisplaced: Set this to on for a dry run. 

## About the Ignored.config Files

The globalIgnored.config file is applied globally. The nameIgnored.config file is applied to the specific bin with the corresponding name. For example, globalIgnored.config applies to the Misc and the Robotics bins, but MiscIgnored.config only applies to the bin named Misc. 

In the file is a set of regular expression patterns separated by newlines. Each line is read as a pattern. If any file's filename or relative path to the file bin matches the pattern, it will be ignored. It is not needed to add files beginning with '.' because they are ignored by default. 

# fileSorter.py Flags

1. `--logDir`
   
   By default, the fileSorter script generates `Logs` folder in the current working directory if none exists. Then it would place all log files in that `Logs` folder. When this flag is passed, it takes the input as an absolute path to the directory to store log files. All generated log files would be stored there.

2. `--rootDir`
   
   This flag specifies the root directory for fileSorter.py to traverse. It overrides the default assumption that the current working directory as the root directory for sorting.

3. `--debug`
   
   This flag increases the verbosity (the amount of information printed to STDOUT) to debug level. It is only useful for troubleshooting. For basic information, it is recommended to read the log files **INSTEAD OF** enabling this flag. 

# initFileSorter.py Flags

`--rootDir`

This flag specifies the root directory for initFileSorter.py to store the config files and to create config files for. It overrides the default assumption that the current working directory as the root directory for initialization.

# Further Customization & Usage

What was given above should be enough for basic usage of this script. To increase potential for automation and customization, further features were added and documented [here](https://github.com/LivelyCarpet87/FileSorter/blob/master/More%20Complex%20Usage.md#more-complex-usage) to prevent information overload. 