import configparser
import argparse
import os
import re
def duplicateFileWorkaround(currentDir,targetDir,filename):
    copyUnderscore2 = re.compile(r"^([\S\s]*)_copy_?(\d)\.([\S\s]*)$")
    copySpace2 = re.compile(r"^([\S\s]*) copy ?(\d)\.([\S\s]*)$")
    copyUnderscore = re.compile(r"^([\S\s]*)_copy\.([\S\s]*)$")
    copySpace = re.compile(r"^([\S\s]*) copy\.([\S\s]*)$")
    noCopy = re.compile(r"^([\S\s]*)\.([\S\s]*)$")

    if copyUnderscore2.search(filename):
        attemptCounter=1 + int(copyUnderscore2.match(filename).group(2))
        underscore=True
        filenameBase=copyUnderscore2.match(filename).group(1)
        fileExtension=copyUnderscore2.match(filename).group(3)
    elif copySpace2.search(filename):
        attemptCounter=1 + int(copySpace2.match(filename).group(2))
        underscore=False
        filenameBase=copySpace2.match(filename).group(1)
        fileExtension=copySpace2.match(filename).group(3)
    elif copyUnderscore.search(filename):
        attemptCounter = 2
        underscore=True
        filenameBase=copyUnderscore.match(filename).group(1)
        fileExtension=copyUnderscore.match(filename).group(2)
    elif copySpace.search(filename):
        attemptCounter = 2
        underscore=False
        filenameBase=copySpace.match(filename).group(1)
        fileExtension=copySpace.match(filename).group(2)
    elif noCopy.search(filename):
        attemptCounter=1
        underscore=False
        filenameBase=noCopy.match(filename).group(1)
        fileExtension=noCopy.match(filename).group(2)
    else:
        print('ERROR: Too many duplicates of '+targetDir+os.sep+filename+'. File has no extention. Program ignoring this file as a failsafe.')
        return None

    while True:
        if attemptCounter == 1:
            newFilename=filenameBase+'.'+fileExtension+'.backup'
        if attemptCounter == 2 and underscore == True:
            newFilename=filenameBase+'_copy.'+fileExtension+'.backup'
        if attemptCounter == 2 and underscore == False:
            newFilename=filenameBase+' copy.'+fileExtension+'.backup'
        if attemptCounter > 2 and underscore == True:
            newFilename=filenameBase+'_copy '+str(attemptCounter-1)+'.'+fileExtension+'.backup'
        if attemptCounter > 2 and underscore == False:
            newFilename=filenameBase+' copy '+str(attemptCounter-1)+'.'+fileExtension+'.backup'

        if os.path.isfile(targetDir+os.sep+newFilename):
            attemptCounter=attemptCounter+1
        elif attemptCounter > 11:
            print('ERROR: Too many duplicates of '+targetDir+os.sep+filename+'.backup'+' found. Possible error. Program ignoring this file as a failsafe.')
        else:
            break
    os.rename(currentDir+os.sep+filename, targetDir+os.sep+newFilename)
    return None

def isDir(possiblePath):
    if os.path.isdir(possiblePath):
        return possiblePath
    else:
        msg = possiblePath+" is not a valid directory. "
        raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser(description='Takes in settings for fileSort.py')
parser.add_argument("--rootDir",dest='path',default=os.getcwd(),required=False)
parser.add_argument("--genBinIgnored",nargs='?',dest='genBinIgnored',const=True,default=False,required=False)
parser.add_argument("--includeDir",nargs='+',type=isDir,required=False)
args = parser.parse_args()
path=args.path
genBinIgnored=args.genBinIgnored
includeDir=args.includeDir
if not os.path.isdir(path):
    path=os.getcwd()

if not os.path.isdir(path+os.sep+"fileSortConfiguration"):
    os.mkdir(path+os.sep+"fileSortConfiguration")

if os.path.isfile("."+os.sep+"fileSortConfiguration"+os.sep+"fileSort.config"):
    duplicateFileWorkaround("."+os.sep+"fileSortConfiguration","."+os.sep+"fileSortConfiguration","fileSort.config")

if not os.path.isfile("."+os.sep+"fileSortConfiguration"+os.sep+"globalIgnored.config"):
    f = open("."+os.sep+"fileSortConfiguration"+os.sep+"globalIgnored.config", "w")

config = configparser.ConfigParser(allow_no_value=True)
config['GlobalSettings'] = {'# Root Directory of bins to be sorted': None,
                            'rootDir': path,
                            '# Enable fileSort? (Global)': None,
                            'rootStatus': 'OFF',
                            '# Name for directory of misplaced files': None,
                            'misplacedDirName': 'Misplaced',
                            '# Remove Misplaced directory when it is empty?': None,
                            'removeMisplacedDir': 'OFF',
                            '# Group versions?': None,
                            'groupversions' : 'ON',
                            '# Any file with this number of versions or more will be grouped.': None,
                            'groupthreshold': 3,
                            '# The seperator between the tag and the filename.': None,
                            'tag_separator': '_'}

binCount=1
if includeDir is not None:
    for dir in includeDir:
        binName="Bin"+str(binCount)
        name = os.path.basename(dir)
        config.add_section(binName)
        config.set(binName, '# User-given name for this bin')
        config.set(binName,"name",name)
        config.set(binName, '# Enable this bin?')
        config.set(binName,"active","ON")
        config.set(binName, '# AbsoluteDirectory of the folder')
        config.set(binName,"absolutedir",dir)
        config.set(binName, '# Tag for files in this bin. ')
        config.set(binName, '# File called randchar_MISC_randchar.randtype will be put into MISC bin. ')
        config.set(binName, '# Filename must contain TAG_ in its name to be put into bin')
        config.set(binName,"tag",name[0:4].upper())
        config.set(binName, '# Alternative tag for files in this bin. ')
        config.set(binName,"tagAlternative",name[0:4])
        config.set(binName, '# Alternative regular expression tag')
        config.set(binName,"regex_tag",'')
        config.set(binName, '# Ignore misplaced files belonging to this bin in this bin or misplaved folder?')
        config.set(binName,"ignoreMisplaced","OFF")
        if genBinIgnored:
            f = open("."+os.sep+"fileSortConfiguration"+os.sep+name+"Ignored.config", "w")
        binCount=binCount+1

for name in os.listdir(path):
    if os.path.isdir(name) and not os.path.islink(name) and not name=="Misplaced" and not name=="fileSortConfiguration" and not name=="Logs":
        binName="Bin"+str(binCount)
        config.add_section(binName)
        config.set(binName, '# User-given name for this bin')
        config.set(binName,"name",name)
        config.set(binName, '# Enable this bin?')
        config.set(binName,"active","ON")
        config.set(binName, '# Name of folder directly under the root directory')
        config.set(binName,"dirname",name)
        config.set(binName, '# Tag for files in this bin. ')
        config.set(binName, '# File called randchar_MISC_randchar.randtype will be put into MISC bin. ')
        config.set(binName, '# Filename must contain TAG_ in its name to be put into bin')
        config.set(binName,"tag",name[0:4].upper())
        config.set(binName, '# Alternative tag for files in this bin. ')
        config.set(binName,"tagAlternative",'')
        config.set(binName, '# Alternative regular expression tag')
        config.set(binName,"regex_tag",'')
        config.set(binName, '# Ignore misplaced files belonging to this bin in this bin or misplaved folder?')
        config.set(binName,"ignoreMisplaced","OFF")
        if genBinIgnored:
            if not os.path.isfile("."+os.sep+"fileSortConfiguration"+os.sep+name+"Ignored.config"):
                f = open("."+os.sep+"fileSortConfiguration"+os.sep+name+"Ignored.config", "w")
        binCount=binCount+1

with open('.'+os.sep+'fileSortConfiguration'+os.sep+'fileSort.config', 'w') as configfile:
    config.write(configfile)
