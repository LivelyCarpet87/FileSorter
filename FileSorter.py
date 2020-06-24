import sys
import os
import re
import configparser
import argparse
import logging
import datetime

projectNames = []

# Error Codes (Based off BSD Reserved Codes)
# regexErr = 128 + 65
rootDirErr = 128 + 65 + 1
filebinDirErr = 74
cantCreateErr = 73
missingDirErr = 69
invalidSettingErr = 128 + 78
configNotFound = 128 + 66

def matchVersionFormat(regexTag, regexTagAlt, regex_tag, filename):
    global projectNames
    if regexTag is not None:
        if regexTag.search(filename):
            projName = regexTag.match(filename).group(1)
            projectNames.append(projName)
            return projName
    if regexTagAlt is not None:
        if regexTagAlt.search(filename):
            projName = regexTagAlt.match(filename).group(1)
            projectNames.append(projName)
            return projName
    if regex_tag is not None:
        if regex_tag.search(filename):
            projName = regex_tag.match(filename).group(1)
            projectNames.append(projName)
            return projName
    return None


def duplicateFileWorkaround(currentDir, targetDir, filename):
    log.debug('Trying to move ' + currentDir + os.sep + filename + ' to ' + targetDir + os.sep + filename)
    if not os.path.isfile(targetDir + os.sep + filename):
        os.rename(currentDir + os.sep + filename, targetDir + os.sep + filename)
        log.debug('Moved and renamed ' + str(currentDir + os.sep + filename) + ' to ' + str(targetDir + os.sep + filename) + ' with os.rename()')
        return None
    copyUnderscore2 = re.compile(r"^([\S\s]*)_copy_?(\d)\.([\S\s]*)$")
    copySpace2 = re.compile(r"^([\S\s]*) copy ?(\d)\.([\S\s]*)$")
    copyUnderscore = re.compile(r"^([\S\s]*)_copy\.([\S\s]*)$")
    copySpace = re.compile(r"^([\S\s]*) copy\.([\S\s]*)$")
    noCopy = re.compile(r"^([\S\s]*)\.([\S\s]*)$")

    if copyUnderscore2.search(filename):
        attemptCounter = 1 + int(copyUnderscore2.match(filename).group(2))
        underscore = True
        filenameBase = copyUnderscore2.match(filename).group(1)
        fileExtension = copyUnderscore2.match(filename).group(3)
    elif copySpace2.search(filename):
        attemptCounter = 1 + int(copySpace2.match(filename).group(2))
        underscore = False
        filenameBase = copySpace2.match(filename).group(1)
        fileExtension = copySpace2.match(filename).group(3)
    elif copyUnderscore.search(filename):
        attemptCounter = 2
        underscore = True
        filenameBase = copyUnderscore.match(filename).group(1)
        fileExtension = copyUnderscore.match(filename).group(2)
    elif copySpace.search(filename):
        attemptCounter = 2
        underscore = False
        filenameBase = copySpace.match(filename).group(1)
        fileExtension = copySpace.match(filename).group(2)
    elif noCopy.search(filename):
        attemptCounter = 1
        underscore = False
        filenameBase = noCopy.match(filename).group(1)
        fileExtension = noCopy.match(filename).group(2)
    else:
        log.error('Too many duplicates of ' + targetDir + os.sep + filename + '. File has no extention. Program ignoring this file as a failsafe.')
        return None

    while True:
        if attemptCounter == 1:
            newFilename = filenameBase + '.' + fileExtension
        if attemptCounter == 2 and underscore is True:
            newFilename = filenameBase + '_copy.' + fileExtension
        if attemptCounter == 2 and underscore is False:
            newFilename = filenameBase + ' copy.' + fileExtension
        if attemptCounter > 2 and underscore is True:
            newFilename = filenameBase + '_copy ' + str(attemptCounter-1) + '.' + fileExtension
        if attemptCounter > 2 and underscore is False:
            newFilename = filenameBase + ' copy ' + str(attemptCounter-1) + '.' + fileExtension
        log.debug('attemptCounter=' + str(attemptCounter) + ' newFilename=' + newFilename)

        if os.path.isfile(targetDir + os.sep + newFilename):
            attemptCounter = attemptCounter + 1
            log.debug(targetDir + os.sep + newFilename + ' already exists. Trying again. ')
        elif attemptCounter > 11:
            log.error('Too many duplicates of ' + targetDir + os.sep + filename + ' found. Possible error. Program ignoring this file as a failsafe.')
        else:
            break
    os.rename(currentDir + os.sep + filename, targetDir + os.sep + newFilename)
    print(os.path.isfile(targetDir + os.sep + newFilename))
    log.debug('Moved and renamed ' + str(currentDir + os.sep + filename) + ' to ' + str(targetDir + os.sep + newFilename) + ' with os.rename()')
    return None


# this function detirmines if the file passed to it should be ignored
def validTarget(rootDir, name, subdir, filename, walkDir, misplacedDirName):
    # log.debug( 'Testing if '+subdir + os.sep + filename+' should be ignored.') # Creates excessive debug messages, uncomment when needed
    global globalIgnored
    global globalWarned
    if filename[0] == ".":
        return False
    with open(rootDir + os.sep + "fileSortConfiguration" + os.sep + "globalIgnored.config", "r") as a_file:  # read the global ignore file
        for line in a_file:
            ignored = line.strip()  # parse each line as a regex pattern
            try:  # try to match the file to the patterns
                ignoreCondition = re.compile(ignored)
                filenameMatches = len(re.findall(ignoreCondition, filename))
                subdirMatches = len(re.findall(ignoreCondition, subdir))
                walkDirMatches = len(re.findall(ignoreCondition, walkDir))
                # check if it matches in the directory relative to the absolute directory of the file
                if (subdirMatches + filenameMatches) > walkDirMatches:
                    # Check if the user has been notified that the file is ignored
                    if (subdir + os.sep + filename) not in globalIgnored:  # globalIgnored is an array with absolute path of all ignored files.
                        # if the file has not been mentioned, tell user.
                        log.debug(filename + ' matched ' + ignored)
                        log.info(subdir + os.sep + filename + " ignored according to Global configuration file. ")
                        globalIgnored.append(subdir + os.sep + filename)
                        log.debug(str(subdir + os.sep + filename) + ' added to globalIgnored.')
                        if (rootDir + os.sep + misplacedDirName) in subdir:
                            # warning the user that the file is in the misplaced folder and is ignored.
                            log.warning(subdir + os.sep + filename + " is in the misplaced folder. ")
                    return False
            except re.error:
                if ignored not in globalWarned:
                    # re.error is raised for invalid regex expression, causes the line in ignore file to be skipped
                    log.error("Invalid regular expression given: "+ignored)
                    globalWarned.append(ignored)
                    log.debug(ignored+' added to globalWarned.')
    filebinIgnore = rootDir + os.sep + "fileSortConfiguration" + os.sep + name + "Ignored.config"  # read the local ignored file (not applied globally)
    if os.path.exists(filebinIgnore):
        # log.debug('Ignore file found for '+name) #Creates excessive debug messages, uncomment when needed
        with open(filebinIgnore, "r") as a_file:
            for line in a_file:
                ignored = line.strip()
                try:
                    ignoreCondition = re.compile(ignored)
                    filenameMatches = len(re.findall(ignoreCondition, filename))
                    subdirMatches = len(re.findall(ignoreCondition, subdir))
                    walkDirMatches = len(re.findall(ignoreCondition, walkDir))
                    if subdirMatches > walkDirMatches:
                        # notify user that file has been ignored.
                        log.debug('Filename: ' + subdir + os.sep + filename + ' matched in filename ' + filenameMatches + ' times, matched in subdir ' + subdirMatches + 'times, and matched in walkDir' + walkDirMatches + ' times. ')
                        log.info(subdir + os.sep + filename + " ignored according to local configuration file for " + name + ". ")
                        if (rootDir + os.sep + misplacedDirName) in subdir:
                            # warning the user that the file is in the misplaced folder and is ignored.
                            log.warning(subdir + os.sep + filename + " is in the misplaced folder. ")
                        return False
                except re.error:
                    # skip invalid expressions
                    log.error("Invalid regular expression given: " + ignored)
    # else: #Creates excessive debug messages, uncomment when needed
        # log.debug('Local ignoredConfig not found for ' + filebinIgnore) #Creates excessive debug messages, uncomment when needed
    return True


# put different versions of the same file together. Files named as TAG_filenameV1.0,
# TAG_filenameV2.1,TAG_filenameV3.0 will be put into folder called filename
def groupVersions(rootDir, thisFilebin, groupthreshold):
    global projectNames
    config.read(rootDir + os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config')
    log.debug('Read config file for groupVersions() function')
    tag_separator = config.get('GlobalSettings', 'tag_separator')
    name = thisFilebin.get('name', filebin)
    log.debug('testing if versions can be bunched for ' + name)
    if config.has_option(filebin, 'dirName'):
        dirName = thisFilebin.get('dirName', filebin)
        log.debug('dirName: ' + dirName)
        absolutedir = None
    elif config.has_option(filebin, 'absolutedir'):
        dirName = None
        absolutedir = thisFilebin.get('absolutedir', filebin)
        log.debug('absolutedir: ' + absolutedir)
    else:
        log.critical('Directory for ' + name + ' is missing.')
        sys.exit(missingDirErr)

    if config.has_option(filebin, 'tag'):
        if thisFilebin.get('tag', filebin) != '':
            tag = thisFilebin.get('tag', filebin)
        else:
            tag = None
        if config.has_option(filebin, 'tagAlternative'):
            if thisFilebin.get('tagAlternative') != '':
                tagAlternative = thisFilebin.get('tagAlternative')
            else:
                tagAlternative = None
        else:
            tagAlternative = ""
        if tag is not None:
            regexForTag = r"^[\S\s]*" + re.escape(tag) + re.escape(tag_separator) + r"([\S\s]*)V\d[\S\s]*$"
        else:
            regexForTagAlt = None
        log.debug('groupVersions -> regexForTag: ' + regexForTag)
        if tagAlternative is not None:
            regexForTagAlt = r"^[\S\s]*" + re.escape(tagAlternative) + re.escape(tag_separator) + r"([\S\s]*)V\d[\S\s]*$"
            log.debug('groupVersions -> regexForTagAlt: ' + regexForTagAlt)
        else:
            regexForTagAlt = None
    else:
        regexForTag = None
        regexForTagAlt = None

    if config.has_option(filebin, 'regex_tag'):
        if thisFilebin.get('regex_tag') != '':
            regex_tag = thisFilebin.get('regex_tag')
            regex_tag = '^' + regex_tag + r"([\S\s]*)V\d[\S\s]*$"
            log.debug('groupVersions -> regex_tag: ' + regex_tag)
        else:
            regex_tag = None
    else:
        regex_tag = None

    if regexForTag is not None:
        regexTag = re.compile(regexForTag+'$', re.I)
    else:
        regexTag = None
    if regexForTagAlt is not None:
        regexTagAlt = re.compile(regexForTagAlt+'$', re.I)
    else:
        regexTagAlt = None
    if regex_tag is not None:
        regex_tag = re.compile('(' + regex_tag + ')' + r"V\d[\S\s]*" + '$')
    else:
        regex_tag = None

    if dirName is not None:
        walkDir = rootDir + os.sep + dirName
    elif absolutedir is not None:
        walkDir = absolutedir
    log.debug('groupVersions -> Directory set to ' + walkDir)
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir, name, subdir, filename, walkDir, misplacedDirName):
                    projName = matchVersionFormat(regexTag, regexTagAlt, regex_tag, filename)
                    if projName is not None:
                        log.debug('Found potential project: ' + projName + ' with count: ' + str(projectNames.count(projName)) + ' and project threshold met: ' + str(projectNames.count(projName) >= groupthreshold) + ' and subdirectory: ' + subdir)
                        if (projectNames.count(projName) >= groupthreshold) and (projName not in subdir):  # if there are numerous versions AND it is not in a folder with the project name:

                            if not os.path.isdir(subdir + os.sep + projName):  # make a directory if it does not exist
                                os.mkdir(subdir + os.sep + projName)
                            for subdir2, dirs2, files2 in os.walk(walkDir):
                                for filename2 in files2:
                                    filepath2 = subdir2 + os.sep + filename2
                                    matchProject = False
                                    if regexTag is not None:
                                        if re.search(regexTag, filename2):
                                            if projName == regexTag.match(filename2).group(1):
                                                matchProject = True
                                    if regexTagAlt is not None:
                                        if re.search(regexTagAlt, filename2):
                                            if projName == regexTag.match(filename2).group(1):
                                                matchProject = True
                                    if regex_tag is not None:
                                        if re.search(regex_tag, filename2):
                                            if projName == regexTag.match(filename2).group(1):
                                                matchProject = True

                                    if validTarget(rootDir, name, subdir2, filename2, walkDir, misplacedDirName) and matchProject and (projName not in subdir2):
                                        duplicateFileWorkaround(subdir2, subdir2 + os.sep + projName, filename2)  # move files into this directory.
                                        log.debug('groupVersions -> Multiple versions of filename2 found and moved into ' + subdir2 + os.sep + projName)

    else:
        log.critical('Directory for ' + name + ' not valid.')  # quit if the given directory for the folder to sort is invalid, see topmost if condition.
        sys.exit(filebinDirErr)


# remove misplaced files and move to misplaced folder.
def removeMisplaced(rootDir, misplacedDirName, thisFilebin):
    name = thisFilebin.get('name', filebin)
    log.debug('Removing misplaced files in ' + name)
    config.read(rootDir + os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config')
    tag_separator = config.get('GlobalSettings', 'tag_separator')
    if config.has_option(filebin, 'dirName') and config.has_option(filebin, 'absolutedir'):
        log.critical('Two directories given for ' + name + ' Aborting due to possible conflict. Please remove 1 of the 2 directories. ')
        sys.exit(filebinDirErr)
    elif config.has_option(filebin, 'dirName'):
        dirName = thisFilebin.get('dirName', filebin)
        absolutedir = None
    elif config.has_option(filebin, 'absolutedir'):
        dirName = None
        absolutedir = thisFilebin.get('absolutedir', filebin)
    else:
        log.critical('Directory for ' + name + ' is missing.')
        sys.exit(missingDirErr)
    ignoreMisplaced = config.getboolean(filebin, 'ignoreMisplaced')
    misplacedDirName = thisFilebin.get('misplacedDirName', "Misplaced")
    if config.has_option(filebin, 'tag'):
        if thisFilebin.get('tag', filebin) != '':
            tag = thisFilebin.get('tag', filebin)
        else:
            tag = None
        if config.has_option(filebin, 'tagAlternative'):
            if thisFilebin.get('tagAlternative') != '':
                tagAlternative = thisFilebin.get('tagAlternative')
            else:
                tagAlternative = None
        else:
            tagAlternative = None
        if tag is not None:
            regexForTag_F = r"[\S\s]*"+re.escape(tag)+re.escape(tag_separator)+r"[\S\s]*"
            log.debug(name + ' -> removeMisplaced -> regexForTag_F: ' + regexForTag_F)
            regexForTag_B = r"[\S\s]*" + re.escape(tag_separator) + re.escape(tag) + r"[\S\s]*"
            log.debug(name + ' -> removeMisplaced -> regexForTag_B: ' + regexForTag_B)
        else:
            regexForTag_F = None
            regexForTag_B = None
        if tagAlternative is not None:
            regexForTagAlt_F = r"[\S\s]*" + re.escape(tagAlternative) + re.escape(tag_separator) + r"[\S\s]*"
            log.debug(name + ' -> removeMisplaced -> regexForTagAlt_F: ' + regexForTagAlt_F)
            regexForTagAlt_B = r"[\S\s]*" + re.escape(tag_separator) + re.escape(tagAlternative) + r"[\S\s]*"
            log.debug(name + ' -> removeMisplaced -> regexForTagAlt_B: ' + regexForTagAlt_B)
        else:
            regexForTagAlt_F = None
            regexForTagAlt_B = None
    else:
        regexForTag_F = None
        regexForTagAlt_F = None
    if config.has_option(filebin, 'regex_tag'):
        if thisFilebin.get('regex_tag') != '':
            regex_tag = thisFilebin.get('regex_tag')
            log.debug(name + ' -> removeMisplaced -> regex_tag: ' + regex_tag)
        else:
            regex_tag = None
    else:
        regex_tag = None

    if regexForTag_F is not None:
        regexTag_F = re.compile(regexForTag_F+'$', re.I)
        regexTag_B = re.compile(regexForTag_B+'$', re.I)
    if regexForTagAlt_F is not None:
        regexTagAlt_F = re.compile(regexForTagAlt_F+'$', re.I)
        regexTagAlt_B = re.compile(regexForTagAlt_B+'$', re.I)
    if regex_tag is not None:
        try:
            regex_tag = re.compile(regex_tag)
        except re.error:
            log.warning("Invalid regular expression" + regex_tag + " given for " + name + "Ignore file, skipping ...")
    log.debug(name + ' -> removeMisplaced -> Compiled all regex tags.')
    if dirName is not None:
        walkDir = rootDir + os.sep + dirName
    elif absolutedir is not None:
        walkDir = absolutedir
    log.debug(name + ' -> removeMisplaced -> walkDir: ' + walkDir)
    if not os.path.isdir(rootDir + os.sep + misplacedDirName):
        os.mkdir(rootDir + os.sep + misplacedDirName)
        log.debug(name + ' -> removeMisplaced -> Created Misplaced Folder b/c it may be needed later')
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir, name, subdir, filename, walkDir, misplacedDirName):
                    try:
                        rTag = regexTag_F.search(filename) or regexTag_B.search(filename)
                    except NameError:
                        rTag = False
                    except AttributeError:
                        rTag = False
                    try:
                        rAltTag = regexTagAlt_F.search(filename) or regexTagAlt_B.search(filename)
                    except NameError:
                        rAltTag = False
                    except AttributeError:
                        rAltTag = False
                    try:
                        rTagGiven = regex_tag.search(filename)
                    except NameError:
                        rTagGiven = False
                    except AttributeError:
                        rTagGiven = False
                    if rTag or rAltTag or rTagGiven:
                        continue
                    else:
                        if ignoreMisplaced:
                            log.info(filepath + " is misplaced")
                        else:
                            duplicateFileWorkaround(subdir, rootDir + os.sep + misplacedDirName, filename)
                            log.info(filepath + " is misplaced and placed into " + misplacedDirName)
    else:
        log.critical('Directory for ' + name + ' not valid.')
        sys.exit(filebinDirErr)


# return the misplaced files to the directories they belong in if they have the corresponding tags.
def returnMisplaced(rootDir, misplacedDirName, thisFilebin):
    config.read(rootDir + os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config')
    tag_separator = config.get('GlobalSettings', 'tag_separator')
    name = thisFilebin.get('name', filebin)
    log.debug('Returning misplaced files for ' + name)
    if config.has_option(filebin, 'dirName') and config.has_option(filebin, 'absolutedir'):
        log.critical('Two directories given for ' + name + ' Aborting due to possible conflict. Please remove 1 of the 2 directories. ')
        sys.exit(filebinDirErr)
    elif config.has_option(filebin, 'dirName'):
        dirName = thisFilebin.get('dirName', filebin)
        absolutedir = None
    elif config.has_option(filebin, 'absolutedir'):
        dirName = None
        absolutedir = thisFilebin.get('absolutedir', filebin)
    else:
        log.critical('Directory for ' + name + ' is missing.')
        sys.exit(missingDirErr)
    ignoreMisplaced = config.getboolean(filebin, 'ignoreMisplaced')
    if config.has_option(filebin, 'tag'):
        if thisFilebin.get('tag', filebin) is not None:
            tag = thisFilebin.get('tag', filebin)
        else:
            tag = None
        if config.has_option(filebin, 'tagAlternative'):
            if thisFilebin.get('tagAlternative') != '':
                tagAlternative = thisFilebin.get('tagAlternative')
            else:
                tagAlternative = None
        else:
            tagAlternative = None
        if tag is not None:
            regexForTag_F = r"[\S\s]*" + re.escape(tag) + re.escape(tag_separator) + r"[\S\s]*"
            log.debug(name + ' -> returnMisplaced -> regexForTag_F: ' + regexForTag_F)
            regexForTag_B = r"[\S\s]*" + re.escape(tag_separator) + re.escape(tag) + r"[\S\s]*"
            log.debug(name + ' -> returnMisplaced -> regexForTag_B: ' + regexForTag_B)
        else:
            regexForTag_F = None
        if tagAlternative is not None:
            regexForTagAlt_F = r"[\S\s]*" + re.escape(tagAlternative) + re.escape(tag_separator) + r"[\S\s]*"
            log.debug(name + ' -> returnMisplaced -> regexForTagAlt_F: ' + regexForTagAlt_F)
            regexForTagAlt_B = r"[\S\s]*" + re.escape(tag_separator) + re.escape(tagAlternative) + r"[\S\s]*"
            log.debug(name + ' -> returnMisplaced -> regexForTagAlt_B: ' + regexForTagAlt_B)
        else:
            regexForTagAlt_F = None
    else:
        regexForTag_F = None
        regexForTagAlt_F = None

    if config.has_option(filebin, 'regex_tag'):
        if thisFilebin.get('regex_tag') != '':
            regex_tag = thisFilebin.get('regex_tag')
            log.debug(name + ' -> returnMisplaced -> regex_tag: ' + regex_tag)
        else:
            regex_tag = None
    else:
        regex_tag = None

    if regexForTag_F is not None:
        regexTag_F = re.compile(regexForTag_F+'$', re.I)
        regexTag_B = re.compile(regexForTag_B+'$', re.I)
    if regexForTagAlt_F is not None:
        regexTagAlt_F = re.compile(regexForTagAlt_F+'$', re.I)
        regexTagAlt_B = re.compile(regexForTagAlt_B+'$', re.I)
    if regex_tag is not None:
        try:
            regex_tag = re.compile(regex_tag, re.I)
        except re.error:
            log.error("Invalid regular expression given for " + name + ", skipping ...")

    walkDir = rootDir + os.sep + misplacedDirName
    log.debug(name + ' -> returnMisplaced -> walkDir: ' + walkDir)
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir, name, subdir, filename, walkDir, misplacedDirName):
                    try:
                        rTag = regexTag_F.search(filename) or regexTag_B.search(filename)
                    except NameError:
                        rTag = False
                    except AttributeError:
                        rTag = False
                    try:
                        rAltTag = regexTagAlt_F.search(filename) or regexTagAlt_B.search(filename)
                    except NameError:
                        rAltTag = False
                    except AttributeError:
                        rAltTag = False
                    try:
                        rTagGiven = regex_tag.search(filename)
                    except NameError:
                        rTagGiven = False
                    except AttributeError:
                        rTagGiven = False
                    if rTag or rAltTag or rTagGiven:
                        if ignoreMisplaced:
                            log.info(filepath + " should be returned")
                        else:
                            if dirName is not None:
                                # ignore if duplicate files exist.
                                duplicateFileWorkaround(subdir, rootDir + os.sep + dirName, filename)
                                log.info(filepath + " returned")
                            elif absolutedir is not None:
                                duplicateFileWorkaround(subdir, absolutedir, filename)
                                log.info(filepath + " returned")
                            else:
                                log.critical('Directory for ' + name + ' not valid.')
                                sys.exit(filebinDirErr)
    else:
        log.critical('Directory for ' + name + ' not valid.')
        sys.exit(filebinDirErr)

globalIgnored = []
globalWarned = []

parser = argparse.ArgumentParser(description='Generates settings for fileSort.py')
ifCreateLog = parser.add_mutually_exclusive_group(required=False)
ifCreateLog.add_argument("--logDir", dest='logDir', default='', required=False)
ifCreateLog.add_argument("--noLog", action='store_true', default=False, required=False)
verbosityLevel = parser.add_mutually_exclusive_group(required=False)
verbosityLevel.add_argument('--debug', action='store_const',const=2, default=0)  # debug
verbosityLevel.add_argument('--verbose', '-v', action='count', default=0)  # warning, info, debug
verbosityLevel.add_argument('--quiet', '-q', action='count', default=0)  # critical, error/exception, warning
parser.add_argument("--rootDir", dest='path', default=os.getcwd(), required=False)
args = parser.parse_args()
logDir = args.logDir
verbose = args.verbose
quiet = args.quiet
path = args.path
noLog = args.noLog
debug = args.debug
verbosityLevel = verbose - quiet + debug
if not os.path.isdir(path):
    path = os.getcwd()
if not noLog:
    if logDir == '':
        logDir = os.getcwd() + os.sep + 'Logs'
    if not os.path.isdir(logDir):
        try:
            os.mkdir(logDir)
        except FileNotFoundError:
            if verbosityLevel != -3:
                print('ERROR: Unable to use "Logs" directory (defaults under working directory). Consider specifying a directory for log file with "--logDir" or pass "--noLog" option. ')
            sys.exit(cantCreateErr)

log = logging.getLogger('FileSorter')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if not noLog:
    fh = logging.FileHandler(logDir + os.sep + 'fileSorter.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    log.addHandler(fh)

if not noLog:
    fhW = logging.FileHandler(logDir + os.sep + 'fileSorterwarning.log')
    fhW.setLevel(logging.WARNING)
    fhW.setFormatter(formatter)
    log.addHandler(fhW)

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
if verbosityLevel != -3:
    if verbosityLevel == -2:
        ch.setLevel(logging.CRITICAL)
    elif verbosityLevel == -1:
        ch.setLevel(logging.ERROR)
    elif verbosityLevel == 0:
        ch.setLevel(logging.WARNING)
    elif verbosityLevel == 1:
        ch.setLevel(logging.INFO)
    elif verbosityLevel == 2:
        ch.setLevel(logging.DEBUG)
    else:
        print("ERROR: Invalid verbosity level setting given. Max -vv or -qqq")
        sys.exit(invalidSettingErr)
    log.addHandler(ch)

log.debug('logDir = '+str(logDir)+', verbose = '+str(verbose)+', quiet = '+str(quiet)+', path = '+str(path))
# Read Config
config = configparser.ConfigParser()
if not os.path.isfile(path + os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config') or not os.path.isfile(path + os.sep + 'fileSortConfiguration' + os.sep + 'globalIgnored.config'):
    log.critical("Configuration files not found at "+path + os.sep + 'fileSortConfiguration. Expected fileSort.config and globalIgnored.config')
    sys.exit(configNotFound)

config.read(path + os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config')
if ('GlobalSettings' in config):
    GlobalSettings = config['GlobalSettings']
    rootDir = GlobalSettings.get('rootDir')
    misplacedDirName = GlobalSettings.get('misplacedDirName', "Misplaced")
    rootStatus = config.getboolean('GlobalSettings', 'rootStatus')
    removeMisplacedDir = config.getboolean('GlobalSettings', 'removeMisplacedDir')
    groupversions = config.getboolean('GlobalSettings', 'groupversions')
    groupthreshold = config.getint('GlobalSettings', 'groupthreshold')

    log.debug('rootDir = ' + str(rootDir) + ', misplacedDirName = ' + str(misplacedDirName) + ', rootStatus = ' + str(rootStatus) + ', removeMisplacedDir = ' + str(removeMisplacedDir) + ', groupversions = ' + str(groupversions) + ', groupthreshold = ' + str(groupthreshold))
    if not rootStatus:
        log.warning("fileSort.py disabled in configfile")
        sys.exit(0)

    if os.path.isdir(rootDir):
        rootDir = rootDir
    else:
        log.critical("Invalid root directory given.")
        sys.exit(rootDirErr)
else:
    log.critical("Global Configuration not found in fileSort.config configuration file. ")
    sys.exit(invalidSettingErr)

existMisplaced = os.path.isdir(rootDir + os.sep + misplacedDirName)
Sections = config.sections()
filebinCount = len(Sections)

for i in range(1, filebinCount+1):
    filebin = "Filebin"+str(i)
    if config.has_section(filebin):
        thisFilebin = config[filebin]
        active = config.getboolean(filebin, 'active')
        if active:
            removeMisplaced(rootDir, misplacedDirName, thisFilebin)
        else:
            log.info(thisFilebin.get('name', filebin) + " skipped.")

for i in range(1, filebinCount+1):
    filebin = "Filebin" + str(i)
    if config.has_section(filebin):
        thisFilebin = config[filebin]
        active = config.getboolean(filebin, 'active')
        if active:
            returnMisplaced(rootDir, misplacedDirName, thisFilebin)
            if groupversions:
                groupVersions(rootDir, thisFilebin, groupthreshold)
        else:
            log.info(thisFilebin.get('name',filebin)+" skipped.")

misplacedFiles = os.listdir(rootDir + os.sep + misplacedDirName)
if os.path.exists(rootDir + os.sep + misplacedDirName + os.sep + ".DS_Store"):
    misplacedFiles.remove('.DS_Store')
if (not misplacedFiles) and removeMisplacedDir and existMisplaced:
    log.info("Removed " + misplacedDirName + " because uneeded")
    if os.path.exists(rootDir + os.sep + misplacedDirNameos.sep+".DS_Store"):
        os.remove(rootDir + os.sep + misplacedDirName + os.sep + ".DS_Store")
    os.rmdir(rootDir + os.sep + misplacedDirName)
elif (not misplacedFiles) and removeMisplacedDir and not existMisplaced:
    if os.path.exists(rootDir + os.sep + misplacedDirName + os.sep + ".DS_Store"):
        os.remove(rootDir + os.sep + misplacedDirName + os.sep + ".DS_Store")
    os.rmdir(rootDir + os.sep + misplacedDirName)
elif misplacedFiles:
    log.warning("Files have been misplaced. Please return them manually. The program is unable to detirmine the intended filebin for these files. ")
else:
    log.info("Keeping "+misplacedDirName+" folder empty.")
log.info("Finished")
