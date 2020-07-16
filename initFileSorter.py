import configparser
import argparse
import os
import re
import sys

this = sys.modules[__name__]


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


def parseArgs():
    parser = argparse.ArgumentParser(description='Takes in settings for fileSort.py')
    parser.add_argument("--rootDir",dest='path',default=os.getcwd(),required=False)
    parser.add_argument("--genBinIgnored",nargs='?',dest='genBinIgnored',const=True,default=False,required=False)
    parser.add_argument("--includeDir",nargs='+',type=isDir,required=False)
    args = parser.parse_args()
    this.path=args.path
    this.genBinIgnored=args.genBinIgnored
    this.includeDir=args.includeDir
    if not os.path.isdir(this.path):
        this.path=os.getcwd()


def setArgs(path, genBinIgnored, includeDir):
    this.path=path
    this.genBinIgnored=genBinIgnored
    this.includeDir=includeDir
    if not os.path.isdir(this.path):
        raise FileNotFoundError


def checkConfigFile():
    if not os.path.isdir(this.path+os.sep+"fileSortConfiguration"):
        os.mkdir(this.path+os.sep+"fileSortConfiguration")

    if os.path.isfile("."+os.sep+"fileSortConfiguration"+os.sep+"fileSort.config"):
        duplicateFileWorkaround("."+os.sep+"fileSortConfiguration","."+os.sep+"fileSortConfiguration","fileSort.config")


def interactiveMain(advanced):
    checkConfigFile()
    if not os.path.isfile("."+os.sep+"fileSortConfiguration"+os.sep+"globalIgnored.config"):
        f = open("."+os.sep+"fileSortConfiguration"+os.sep+"globalIgnored.config", "w")

    config = configparser.ConfigParser(allow_no_value=True)
    config['GlobalSettings'] = {'# Root Directory of bins to be sorted': None,
                                'rootDir': this.path,
                                '# Enable fileSort? (Global)': None,
                                'rootStatus': 'ON',
                                '# Name for directory of misplaced files': None,
                                'misplacedDirName': 'Misplaced',
                                '# Remove Misplaced directory when it is empty?': None,
                                'removeMisplacedDir': 'OFF',
                                '# Group versions?': None,
                                'groupversions' : 'OFF',
                                '# Any file with this number of versions or more will be grouped.': None,
                                'groupthreshold': 3,
                                '# The seperator between the tag and the filename.': None,
                                'tag_separator': '_'}

    if advanced:
        print('Would you like to group different versions of the same files, \
denoted by the syntax "TAG_FilenameV1.txt", into a single folder with \
the name "Filename", when the file sorter runs?')
        while True:
            userChoice = input("y/n > ")
            if userChoice in ['y','Y','yes','Yes','YES']:
                config['GlobalSettings']['groupversions'] = 'ON'
                break
            elif userChoice in ['n','N','no','No','NO']:
                break
    binCount=1
    if this.includeDir is not None:
        for dir in this.includeDir:
            binName="Bin"+str(binCount)
            name = os.path.basename(dir)
            config.add_section(binName)
            config.set(binName, '# User-given name for this bin')
            print("Filebin "+ dir +" has been named "+name+" in the config files. \
Enter a new name or enter nothing to use current name. ")
            userInput = ""
            while True:
                userInput = input("Name: ")
                if userInput == "":
                    break
                elif len(userInput) <= 2:
                    print("Name too short")
                else:
                    name = userInput
                    break
            del userInput
            config.set(binName,"name",name)
            config.set(binName, '# Enable this bin?')
            print("Would you like to enable the file sorter of " + name +"?")
            while True:
                userInput = input(" [Y]/n > ")
                if userInput in ['y', 'Y', 'yes', 'Yes', 'YES', '']:
                    config.set(binName,"active","ON")
                    break
                elif userInput in ['n', 'N', 'no', 'No', 'NO']:
                    config.set(binName,"active","OFF")
                    break
            config.set(binName, '# AbsoluteDirectory of the folder')
            config.set(binName,"absolutedir",dir)
            config.set(binName, '# Tag for files in this bin. ')
            config.set(binName, '# File called randchar_MISC_randchar.randtype will be put into MISC bin. ')
            config.set(binName, '# Filename must contain TAG_ in its name to be put into bin')
            tag = name[0:4].upper()
            print("Filebin "+ dir +" has the tag "+tag+" in the config files. \
Enter a new tag or enter nothing to use current tag. ")
            userInput = ""
            while True:
                userInput = input("Tag: ")
                if len(userInput) >= 2 and '_' not in userInput and ' ' not in userInput and os.sep not in userInput:
                    tag = userInput
                    break
                elif userInput == "":
                    break
                elif len(userInput) <= 2:
                    print("Invalid tag, please ensure tag is at least 2 letters. ")
                elif '_' in userInput or ' ' in userInput or os.sep in userInput:
                    print("Please do not put underscores or whitespaces or " + os.sep +" in the tag. A trailing underscore is not needed. ")
            del userInput
            config.set(binName,"tag",tag)
            config.set(binName, '# Alternative tag for files in this bin. ')
            tag = name[0:4]
            print("Filebin "+ dir +" has the alternative tag "+tag+" in the config files. \
Enter a new tag or enter nothing to not use any alternative tag. ")
            userInput = ""
            while True:
                userInput = input("Alt Tag: ")
                if len(userInput) >= 2 and '_' not in userInput and ' ' not in userInput and os.sep not in userInput:
                    tag = userInput
                    break
                elif userInput == "":
                    break
                elif len(userInput) <= 2:
                    print("Invalid tag, please ensure tag is at least 2 letters. ")
                elif '_' in userInput or ' ' in userInput or os.sep in userInput:
                    print("Please do not put underscores or whitespaces or " + os.sep +" in the tag. A trailing underscore is not needed. ")
            del userInput
            config.set(binName,"tagAlternative",tag)
            config.set(binName, '# Alternative regular expression tag')
            tag = ''
            if advanced == True:
                print("Filebin "+ dir +" has no default regular expression tag in the config files. \
Enter a new regex tag or enter nothing to disable this feature. Disable this if you do not know regular expressions. ")
                userInput = ""
                userInput = input("Regex Tag: ")
                tag = userInput
                del userInput
            config.set(binName,"regex_tag",tag)
            config.set(binName, '# Ignore misplaced files belonging to this bin in this bin or misplaved folder?')
            config.set(binName,"ignoreMisplaced","OFF")
            if this.genBinIgnored:
                f = open("."+os.sep+"fileSortConfiguration"+os.sep+name+"Ignored.config", "w")
                if advanced == True:
                    with open('.'+os.sep+'fileSortConfiguration'+os.sep+name+"Ignored.config", 'a+') as ignoreConfig:
                        print("Enter regular expressions (regex) that match any files that you wish the sorter to ignore. \
Enter the folder name or filenames if you do not know regex very well. Please be certain \
only files you wish to be ignored match the regex. ")
                        print('Enter "!NEXT" to move on. ')
                        while True:
                            userInput = input("Regex: ")
                            if userInput == "" or userInput == '!NEXT':
                                break
                            else:
                                ignoreConfig.write(userInput)
            binCount=binCount+1

    for name in os.listdir(this.path):
        if os.path.isdir(name) and not os.path.islink(name) and not name=="Misplaced" and not name=="fileSortConfiguration" and not name=="Logs":
            binName="Bin"+str(binCount)
            config.add_section(binName)
            config.set(binName, '# User-given name for this bin')
            print("Filebin ."+os.sep+ name +" has been named "+name+" in the config files. \
Enter a new name or enter nothing to use current name. ")
            userInput = ""
            while True:
                userInput = input("Name: ")
                if userInput == "":
                    break
                elif len(userInput) <= 2:
                    print("Name too short")
                else:
                    name = userInput
                    break
            del userInput
            config.set(binName,"name",name)
            config.set(binName, '# Enable this bin?')
            print("Would you like to enable the file sorter of " + name +"?")
            while True:
                userInput = input(" [Y]/n > ")
                if userInput in ['y', 'Y', 'yes', 'Yes', 'YES', '']:
                    config.set(binName,"active","ON")
                    break
                elif userInput in ['n', 'N', 'no', 'No', 'NO']:
                    config.set(binName,"active","OFF")
                    break
            config.set(binName, '# Name of folder directly under the root directory')
            config.set(binName,"dirname",name)
            config.set(binName, '# Tag for files in this bin. ')
            config.set(binName, '# File called randchar_MISC_randchar.randtype will be put into MISC bin. ')
            config.set(binName, '# Filename must contain TAG_ in its name to be put into bin')
            tag = name[0:4].upper()
            print("Filebin "+ name +" has the tag "+tag+" in the config files. \
Enter a new tag or enter nothing to use current tag. ")
            userInput = ""
            while True:
                userInput = input("Tag: ")
                if len(userInput) >= 2 and '_' not in userInput and ' ' not in userInput and os.sep not in userInput:
                    tag = userInput
                    break
                elif userInput == "":
                    break
                elif len(userInput) <= 2:
                    print("Invalid tag, please ensure tag is at least 2 letters. ")
                elif '_' in userInput or ' ' in userInput or os.sep in userInput:
                    print("Please do not put underscores or whitespaces or " + os.sep +" in the tag. A trailing underscore is not needed. ")
            del userInput
            config.set(binName,"tag",tag)
            config.set(binName, '# Alternative tag for files in this bin. ')
            tag = name[0:4]
            print("Filebin "+ name +" has the alternative tag "+tag+" in the config files. \
Enter a new tag or enter nothing to not use any alternative tag. ")
            userInput = ""
            while True:
                userInput = input("Alt Tag: ")
                if len(userInput) >= 2 and '_' not in userInput and ' ' not in userInput and os.sep not in userInput:
                    tag = userInput
                    break
                elif userInput == "":
                    break
                elif len(userInput) <= 2:
                    print("Invalid tag, please ensure tag is at least 2 letters. ")
                elif '_' in userInput or ' ' in userInput or os.sep in userInput:
                    print("Please do not put underscores or whitespaces or " + os.sep +" in the tag. A trailing underscore is not needed. ")
            del userInput
            config.set(binName,"tagAlternative",tag)
            config.set(binName, '# Alternative regular expression tag')
            tag = ''
            if advanced == True:
                print("Filebin "+ name +" has no default regular expression tag in the config files. \
Enter a new regex tag or enter nothing to disable this feature. Disable this if you do not know regular expressions. ")
                userInput = ""
                userInput = input("Regex Tag: ")
                tag = userInput
                del userInput
            config.set(binName,"regex_tag",tag)
            config.set(binName, '# Ignore misplaced files belonging to this bin in this bin or misplaved folder?')
            config.set(binName,"ignoreMisplaced","OFF")
            if this.genBinIgnored:
                f = open("."+os.sep+"fileSortConfiguration"+os.sep+name+"Ignored.config", "w")
                if advanced == True:
                    with open('.'+os.sep+'fileSortConfiguration'+os.sep+name+"Ignored.config", 'a+') as ignoreConfig:
                        print("Enter regular expressions (regex) that match any files that you wish the sorter to ignore. \
Enter the folder name or filenames if you do not know regex very well. Please be certain \
only files you wish to be ignored match the regex. ")
                        print('Enter "!NEXT" to move on. ')
                        while True:
                            userInput = input("Regex: ")
                            if userInput == "" or userInput == '!NEXT':
                                break
                            else:
                                ignoreConfig.write(userInput)
            binCount=binCount+1
    print("Your choices above have been written to the respective configuration \
files. To explore more settings, please read the self-documented configuration files. ")
    with open('.'+os.sep+'fileSortConfiguration'+os.sep+'fileSort.config', 'w') as configfile:
        config.write(configfile)


def main():
    checkConfigFile()
    if not os.path.isfile("."+os.sep+"fileSortConfiguration"+os.sep+"globalIgnored.config"):
        f = open("."+os.sep+"fileSortConfiguration"+os.sep+"globalIgnored.config", "w")

    config = configparser.ConfigParser(allow_no_value=True)
    config['GlobalSettings'] = {'# Root Directory of bins to be sorted': None,
                                'rootDir': this.path,
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
    if this.includeDir is not None:
        for dir in this.includeDir:
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
            if this.genBinIgnored:
                f = open("."+os.sep+"fileSortConfiguration"+os.sep+name+"Ignored.config", "w")
            binCount=binCount+1

    for name in os.listdir(this.path):
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
            if this.genBinIgnored:
                if not os.path.isfile("."+os.sep+"fileSortConfiguration"+os.sep+name+"Ignored.config"):
                    f = open("."+os.sep+"fileSortConfiguration"+os.sep+name+"Ignored.config", "w")
            binCount=binCount+1

    with open('.'+os.sep+'fileSortConfiguration'+os.sep+'fileSort.config', 'w') as configfile:
        config.write(configfile)

if __name__ == '__main__':
    parseArgs()
    main()
