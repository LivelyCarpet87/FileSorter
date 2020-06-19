import sys
import os
import re
import configparser
import argparse
import logging

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
        log.warn('Too many duplicates of '+targetDir+"/"+filename+'. File has no extention. Program ignoring this file as a failsafe.')
        return None

    while True:
        if attemptCounter == 1:
            newFilename=filenameBase+'.'+fileExtension
        if attemptCounter == 2 and underscore == True:
            newFilename=filenameBase+'_copy.'+fileExtension
        if attemptCounter == 2 and underscore == False:
            newFilename=filenameBase+' copy.'+fileExtension
        if attemptCounter > 2 and underscore == True:
            newFilename=filenameBase+'_copy '+str(attemptCounter-1)+'.'+fileExtension
        if attemptCounter > 2 and underscore == False:
            newFilename=filenameBase+' copy '+str(attemptCounter-1)+'.'+fileExtension

        if os.path.isfile(targetDir+os.sep+newFilename):
            attemptCounter=attemptCounter+1
        elif attemptCounter > 11:
            log.warn('Too many duplicates of '+targetDir+"/"+filename+' found. Possible error. Program ignoring this file as a failsafe.')
        else:
            break
    os.rename(currentDir+os.sep+filename, targetDir+os.sep+newFilename)
    return None



#this function detirmines if the file passed to it should be ignored
def validTarget(rootDir,name,subdir,filename,walkDir,misplacedDirName):
    global globalIgnored
    if filename[0]==".":
        return False

    with open(rootDir+os.sep+"fileSortConfiguration"+os.sep+"globalIgnored.config", "r") as a_file: #read the global ignore file
        for line in a_file:
            ignored = line.strip() #parse each line as a regex pattern
            try: #try to match the file to the patterns
                ignoreCondition=re.compile(ignored)
                filenameMatches=subdirMatches=len(re.findall(ignoreCondition, filename))
                subdirMatches=len(re.findall(ignoreCondition, subdir))
                walkDirMatches=len(re.findall(ignoreCondition, walkDir))
                #check if it matches in the directory relative to the absolute directory of the file
                if (subdirMatches + filenameMatches) > walkDirMatches:
                    #Check if the user has been notified that the file is ignored
                    if (subdir+os.sep+ filename) not in globalIgnored:#globalIgnored is an array with absolute path of all ignored files.
                        #if the file has not been mentioned, tell user.
                        log.info("\n"+subdir+os.sep+ filename + " ignored according to Global configuration file. ")
                        globalIgnored.append(subdir+os.sep+ filename)
                        if (rootDir + os.sep + misplacedDirName) in subdir:
                            #warn the user that the file is in the misplaced folder and is ignored.
                            log.warn(subdir+os.sep+ filename + " is in the misplaced folder. ")
                    return False
            except SyntaxError:
                #SyntaxError is raised for invalid regex expression, causes the line in ignore file to be skipped
                log.warn("\n Invalid regular expression given: "+ignored)

    binIgnore=rootDir+os.sep+"fileSortConfiguration"+os.sep+name+"Ignored.config" #read the local ignored file (not applied globally)
    if os.path.exists(binIgnore):
        with open(binIgnore, "r") as a_file:
            for line in a_file:
                ignored = line.strip()
                try:
                    ignoreCondition=re.compile(ignored)
                    filenameMatches=subdirMatches=len(re.findall(ignoreCondition, filename))
                    subdirMatches=len(re.findall(ignoreCondition, subdir))
                    walkDirMatches=len(re.findall(ignoreCondition, walkDir))
                    if subdirMatches > walkDirMatches:
                        #notify user that file has been ignored.
                        log.info("\n"+subdir+os.sep+ filename + " ignored according to local configuration file for "+name+". ")
                        if (rootDir + os.sep + misplacedDirName) in subdir:
                            #warn the user that the file is in the misplaced folder and is ignored.
                            log.warn(subdir+os.sep+ filename + " is in the misplaced folder. ")
                        return False
                except SyntaxError:
                    #skip invalid expressions
                    log.warn("\n Invalid regular expression given: "+ignored)
    return True

#put different versions of the same file together. Files named as TAG_filenameV1.0,
#TAG_filenameV2.1,TAG_filenameV3.0 will be put into folder called filename
def bunchVersions(rootDir,thisBin,groupthreshold):
    projectNames=[]
    config.read(rootDir+'/fileSortConfiguration/fileSort.config')
    tag_separator=config.get('GlobalSettings','tag_separator')
    name=thisBin.get('name',bin)
    if config.has_option(bin,'dirName'):
        dirName=thisBin.get('dirName',bin)
        absolutedir=None
    elif config.has_option(bin,'absolutedir'):
        dirName=None
        absolutedir=thisBin.get('absolutedir',bin)
    else:
        sys.exit('Directory for '+name+' not given.')
    if config.has_option(bin,'tag'):
        tag=thisBin.get('tag',bin)
        if config.has_option(bin,'tagAlternative'):
            tagAlternative=thisBin.get('tagAlternative')
        else:
            tagAlternative=""
        regexForTag= r"[\S\s]*"+re.escape(tag)+re.escape(tag_separator)+r"([\S\s]*)V\d[\S\s]*"
        if tagAlternative!= None:
            regexForTagAlt= r"[\S\s]*"+re.escape(tagAlternative)+re.escape(tag_separator)+r"([\S\s]*)V\d[\S\s]*"
    else:
        regexForTag=None
        regexForTagAlt=None

    if config.has_option(bin,'regex_tag'):
        regex_tag=thisBin.get('regex_tag')
    else:
        regex_tag=None

    if regexForTag != None:
        regexTag = re.compile(regexForTag+'$', re.I)
    if regexForTagAlt != None:
        regexTagAlt = re.compile(regexForTagAlt+'$', re.I)
    if regex_tag != None:
        regex_tag = re.compile('('+regex_tag+')'+r"V\d[\S\s]*"+'$')

    if dirName != None:
        walkDir=rootDir+os.sep+dirName
    elif absolutedir != None:
        walkDir=absolutedir

    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir,name,subdir,filename,walkDir,misplacedDirName):
                    projName=""
                    matched = False
                    try:
                        if re.search(regexTag, filename) and not matched:
                            projName=regexTag.match(filename).group(1) #try to see if file matches required format.
                            projectNames.append(projName)#add to list of found project names
                            matched = True
                    except NameError:#ignore if the regex pattern does not exist or being invalid
                        continue
                    except AttributeError:
                        continue

                    try:
                        if regexTagAlt != None and not matched:
                            if re.search(regexTagAlt, filename):
                                projName=regexTagAlt.match(filename).group(1)
                                projectNames.append(projName)
                                matched = True
                    except NameError:
                        continue
                    except AttributeError:
                        continue
                    try:
                        if regex_tag != None and not matched:
                            if re.search(regex_tag, filename):
                                projName=regex_tag.match(filename).group(1)
                                projectNames.append(projName)
                                matched = True
                    except NameError:
                        continue
                    except AttributeError:
                        continue

                    if projName!="":
                        if (projectNames.count(projName) >= groupthreshold) and (projName not in subdir):#if there are numerous versions AND it is not in a folder with the project name:
                            if not os.path.isdir(subdir+os.sep+projName):#make a directory if it does not exist
                                os.mkdir(subdir+os.sep+projName)
                            for subdir2, dirs2, files2 in os.walk(walkDir):
                                for filename2 in files2:
                                    filepath2 = subdir2 + os.sep + filename2
                                    if validTarget(rootDir,name,subdir2,filename2,walkDir,misplacedDirName) and (re.search(regexTag, filename2) or re.search(regexTagAlt, filename2)) and (projName not in subdir2):
                                        duplicateFileWorkaround(subdir2,subdir2+os.sep+projName,filename2)#move files into this directory.

    else:
        sys.exit('Directory for '+name+' not valid.')# quit if the given directory for the folder to sort is invalid, see topmost if condition.

#remove misplaced files and move to misplaced folder.
def removeMisplaced(rootDir,misplacedDirName,thisBin):
    name=thisBin.get('name',bin)
    config.read(rootDir+'/fileSortConfiguration/fileSort.config')
    tag_separator=config.get('GlobalSettings','tag_separator')
    if config.has_option(bin,'dirName'):
        dirName=thisBin.get('dirName',bin)
        absolutedir=None
    elif config.has_option(bin,'absolutedir'):
        dirName=None
        absolutedir=thisBin.get('absolutedir',bin)
    else:
        sys.exit('Directory for '+name+' not given.')
    ignoreMisplaced=config.getboolean(bin, 'ignoreMisplaced')
    misplacedDirName=thisBin.get('misplacedDirName',"Misplaced")
    if config.has_option(bin,'tag'):
        tag=thisBin.get('tag',bin)
        if config.has_option(bin,'tagAlternative'):
            tagAlternative=thisBin.get('tagAlternative')
        else:
            tagAlternative=""
        regexForTag_F= r"[\S\s]*"+re.escape(tag)+re.escape(tag_separator)+r"[\S\s]*"
        regexForTag_B= r"[\S\s]*"+re.escape(tag_separator)+re.escape(tag)+r"[\S\s]*"
        if tagAlternative!= None:
            regexForTagAlt_F= r"[\S\s]*"+re.escape(tagAlternative)+re.escape(tag_separator)+r"[\S\s]*"
            regexForTagAlt_B= r"[\S\s]*"+re.escape(tag_separator)+re.escape(tagAlternative)+r"[\S\s]*"
    else:
        regexForTag_F=None
        regexForTagAlt_F=None
    if config.has_option(bin,'regex_tag'):
        regex_tag=thisBin.get('regex_tag')
    else:
        regex_tag=None

    if regexForTag_F != None:
        regexTag_F = re.compile(regexForTag_F+'$', re.I)
        regexTag_B = re.compile(regexForTag_B+'$', re.I)
    if regexForTagAlt_F != None:
        regexTagAlt_F = re.compile(regexForTagAlt_F+'$', re.I)
        regexTagAlt_B = re.compile(regexForTagAlt_B+'$', re.I)
    if regex_tag != None:
        try:
            regex_tag = re.compile(regex_tag)
        except re.error:
            log.warn("Invalid regular expression"+regex_tag+" given for "+name+"Ignore file, skipping ...")

    if dirName != None:
        walkDir=rootDir+os.sep+dirName
    elif absolutedir != None:
        walkDir=absolutedir

    if not os.path.isdir(rootDir+os.sep+misplacedDirName):
        os.mkdir(rootDir+os.sep+misplacedDirName)
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir,name,subdir,filename,walkDir,misplacedDirName):
                    try:
                        rTag=regexTag_F.search(filename) or regexTag_B.search(filename)
                    except NameError:
                        rTag = False
                    except AttributeError:
                        rTag = False
                    try:
                        rAltTag=regexTagAlt_F.search(filename) or regexTagAlt_B.search(filename)
                    except NameError:
                        rAltTag = False
                    except AttributeError:
                        rAltTag = False
                    try:
                        rTagGiven=regex_tag.search(filename)
                    except NameError:
                        rTagGiven = False
                    except AttributeError:
                        rTagGiven = False
                    if rTag or rAltTag or rTagGiven:
                        continue
                    else:
                        if ignoreMisplaced:
                            log.info(filepath+" is misplaced")
                        else:
                            duplicateFileWorkaround(subdir,rootDir+os.sep+misplacedDirName,filename)
                            log.info(filepath+" is misplaced and placed into "+misplacedDirName)



    else:
        sys.exit('Directory for '+name+' not valid.')

#return the misplaced files to the directories they belong in if they have the corresponding tags.
def returnMisplaced(rootDir,misplacedDirName,thisBin):
    config.read(rootDir+'/fileSortConfiguration/fileSort.config')
    tag_separator=config.get('GlobalSettings','tag_separator')
    name=thisBin.get('name',bin)
    if config.has_option(bin,'dirName'):
        dirName=thisBin.get('dirName',bin)
        absolutedir=None
    elif config.has_option(bin,'absolutedir'):
        dirName=None
        absolutedir=thisBin.get('absolutedir',bin)
    else:
        sys.exit('Directory for '+name+' not given.')
    ignoreMisplaced=config.getboolean(bin, 'ignoreMisplaced')
    if config.has_option(bin,'tag'):
        tag=thisBin.get('tag',bin)
        if config.has_option(bin,'tagAlternative'):
            tagAlternative=thisBin.get('tagAlternative')
        else:
            tagAlternative=""
        regexForTag_F= r"[\S\s]*"+re.escape(tag)+re.escape(tag_separator)+r"[\S\s]*"
        regexForTag_B= r"[\S\s]*"+re.escape(tag_separator)+re.escape(tag)+r"[\S\s]*"
        if tagAlternative!= None:
            regexForTagAlt_F= r"[\S\s]*"+re.escape(tagAlternative)+re.escape(tag_separator)+r"[\S\s]*"
            regexForTagAlt_B= r"[\S\s]*"+re.escape(tag_separator)+re.escape(tagAlternative)+r"[\S\s]*"
    else:
        regexForTag_F=None
        regexForTagAlt_F=None

    if config.has_option(bin,'regex_tag'):
        regex_tag=thisBin.get('regex_tag')
    else:
        regex_tag=None

    if regexForTag_F != None:
        regexTag_F = re.compile(regexForTag_F+'$', re.I)
        regexTag_B = re.compile(regexForTag_B+'$', re.I)
    if regexForTagAlt_F != None:
        regexTagAlt_F = re.compile(regexForTagAlt_F+'$', re.I)
        regexTagAlt_B = re.compile(regexForTagAlt_B+'$', re.I)
    if regex_tag != None:
        try:
            regex_tag = re.compile(regex_tag, re.I)
        except re.error:
            log.warn("Invalid regular expression given for "+name+", skipping ...")

    walkDir=rootDir+os.sep+misplacedDirName
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir,name,subdir,filename,walkDir,misplacedDirName):
                    try:
                        rTag=regexTag_F.search(filename) or regexTag_B.search(filename)
                    except NameError:
                        rTag = False
                    except AttributeError:
                        rTag = False
                    try:
                        rAltTag=regexTagAlt_F.search(filename) or regexTagAlt_B.search(filename)
                    except NameError:
                        rAltTag = False
                    except AttributeError:
                        rAltTag = False
                    try:
                        rTagGiven=regex_tag.search(filename)
                    except NameError:
                        rTagGiven = False
                    except AttributeError:
                        rTagGiven = False
                    if rTag or rAltTag or rTagGiven:
                        if ignoreMisplaced:
                            log.info(filepath+" should be returned")
                        else:
                            if dirName != None:
                                #ignore if duplicate files exist.
                                duplicateFileWorkaround(subdir,rootDir+os.sep+dirName,filename)
                                log.info(filepath+" returned")
                            elif absolutedir != None:
                                duplicateFileWorkaround(subdir,absolutedir,filename)
                                log.info(filepath+" returned")
                            else:
                                sys.exit('Directory for '+name+' not valid.')


    else:
        sys.exit('Directory for '+name+' not valid.')

globalIgnored=[]

parser = argparse.ArgumentParser(description='Generates settings for fileSort.py')
parser.add_argument("--logDir",dest='logDir',default=os.getcwd(),required=False)
verbosityLevel=parser.add_mutually_exclusive_group(required=False)
verbosityLevel.add_argument('--verbose', '-v', action='count', default=0) #warning/warn, info, debug
verbosityLevel.add_argument('--quiet', '-q', action='count', default=0)#critical, error/exception, warning/warn
parser.add_argument("--rootDir",dest='path',default=os.getcwd(),required=False)
args = parser.parse_args()
logDir=args.logDir
verbose=args.verbose
quiet=args.quiet
path=args.path
if not os.path.isdir(path):
    path=os.getcwd()

verbosityLevel=verbose-quiet

log = logging.getLogger('FileSorter')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('fileSorter.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
log.addHandler(fh)

fhW = logging.FileHandler('fileSorterWarn.log')
fhW.setLevel(logging.WARN)
fhW.setFormatter(formatter)
log.addHandler(fhW)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)

if verbosityLevel == -3:
    del ch
elif verbosityLevel == -2:
    ch.setLevel(logging.CRITICAL)
elif verbosityLevel == -1:
    ch.setLevel(logging.ERROR)
elif verbosityLevel == 0:
    ch.setLevel(logging.WARN)
elif verbosityLevel == 1:
    ch.setLevel(logging.INFO)
elif verbosityLevel == 2:
    ch.setLevel(logging.DEBUG)
else:
    sys.exit("ERROR: Invalid verbosity level setting given. Max -vv or -qqq")
if verbosityLevel != -3:
    log.addHandler(ch)

log.info("Running")
#Read Config
config = configparser.ConfigParser()
if not os.path.isfile(path+os.sep+'fileSortConfiguration'+os.sep+'fileSort.config') or not os.path.isfile(path+os.sep+'fileSortConfiguration'+os.sep+'globalIgnored.config'):
    log.critical("Configuration files not found at "+path+os.sep+'fileSortConfiguration. Expected fileSort.config and globalIgnored.config')
    sys.exit("ERROR: Configuration files not found. See log for details. ")

config.read(path+'/fileSortConfiguration/fileSort.config')
if ('GlobalSettings' in config):
    GlobalSettings = config['GlobalSettings']
    misplacedDirName=GlobalSettings.get('misplacedDirName',"Misplaced")
    rootDir=GlobalSettings.get('rootDir')
    rootStatus=config.getboolean('GlobalSettings','rootStatus')
    removeMisplacedDir=config.getboolean('GlobalSettings','removeMisplacedDir')
    groupversions=config.getboolean('GlobalSettings','groupversions')
    groupthreshold=config.getint('GlobalSettings','groupthreshold')

    if not rootStatus:
        log.warn("fileSort.py disabled in configfile")
        sys.exit("fileSort.py disabled in configfile")

    if os.path.isdir(rootDir):
        rootDir=rootDir
    else:
        log.critical("Invalid root directory given.")
        sys.exit("Error: Invalid root directory given.")
else:
    log.critical("Global Configuration not found in fileSort.config configuration file. ")
    sys.exit("Error: Global Configuration not found in configuration file. ")

existMisplaced=os.path.isdir(rootDir+os.sep+misplacedDirName)
Sections=config.sections()
binCount=len(Sections)

for i in range(1,binCount+1):
    bin="Bin"+str(i)
    if config.has_section(bin):
        thisBin=config[bin]
        active=config.getboolean(bin, 'active')
        if active:
            removeMisplaced(rootDir,misplacedDirName,thisBin)
        else:
            log.info(thisBin.get('name',bin)+" skipped.")

for i in range(1,binCount+1):
    bin="Bin"+str(i)
    if config.has_section(bin):
        thisBin=config[bin]
        active=config.getboolean(bin, 'active')
        if active:
            returnMisplaced(rootDir,misplacedDirName,thisBin)
            if groupversions:
                bunchVersions(rootDir,thisBin,groupthreshold)
        else:
            log.info(thisBin.get('name',bin)+" skipped.")

misplacedFiles=os.listdir(rootDir+os.sep+misplacedDirName)
if os.path.exists(rootDir+os.sep+misplacedDirName+"/.DS_Store"):
    misplacedFiles.remove('.DS_Store')
if (not misplacedFiles) and removeMisplacedDir and existMisplaced:
    log.info("Removed " + misplacedDirName + " because uneeded")
    if os.path.exists(rootDir+os.sep+misplacedDirName+"/.DS_Store"):
        os.remove(rootDir+os.sep+misplacedDirName+"/.DS_Store")
    os.rmdir(rootDir+os.sep+misplacedDirName)
elif (not misplacedFiles) and removeMisplacedDir and not existMisplaced:
    if os.path.exists(rootDir+os.sep+misplacedDirName+"/.DS_Store"):
        os.remove(rootDir+os.sep+misplacedDirName+"/.DS_Store")
    os.rmdir(rootDir+os.sep+misplacedDirName)
elif misplacedFiles:
    log.warn("Files have been misplaced. Please return them manually. The program is unable to detirmine the intended bin for these files. ")
else:
    log.info("Keeping "+misplacedDirName+" in accordance to user settings")
log.info("Done")
