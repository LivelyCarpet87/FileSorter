import sys
import os
import re
import configparser
import argparse
import logging
import datetime

projectNames = []
blacklistDir = [r"^\/bin\/?.*", r"^/usr/bin\/?.*",
r"^/usr/local/bin\/?.*", r"^/sbin\/?.*",
r"^\/etc\/?.*", r"^\/etc\/rc.d\/?.*", r"^\/usr\/share\/doc\/?.*", r"^\/usr\/man\/?.*", r"^\/dev\/?.*",
r"^\/proc\/?.*", r"^\/sys\/?.*", r"^\/mnt\/?.*", r"^\/media\/?.*", r"^\/var\/?.*", r"^\/var\/log\/?.*",
r"^\/var\/spool\/mail\/?.*", r"^\/lib\/?.*", r"^\/usr\/lib\/?.*", r"\/tmp\/?.*", r"\/boot\/?.*",
"^"+re.escape(r"C:\Program Files")+r".*", "^"+re.escape(r"C:\Program Files (x86)")+r".*",
"^"+re.escape(r"C:\Windows\System32")+r".*", "^"+re.escape(r"C:\pagefile.sys")+r".*",
"^"+re.escape(r"C:\System Volume Information")+r".*", "^"+re.escape(r"C:\Windows\WinSxS")+r".*"]

# Error Codes (Based off BSD Reserved Codes)
# regexErr = 128 + 65
rootDirErr = 128 + 65 + 1
filebinDirErr = 74
cantCreateErr = 73
missingDirErr = 69
invalidSettingErr = 128 + 78
configNotFound = 128 + 66
permissionsErr = 128 + 13

this = sys.modules[__name__]

this.log = logging.getLogger('FileSorter')
this.log.setLevel(logging.DEBUG)

this.globalIgnored = []
this.globalWarned = []


class AdminStateUnknownError(Exception):
    """Cannot determine whether the user is an admin."""
    pass


def isUserAdmin():
    """Return True if user has admin privileges.
    Raises:
        AdminStateUnknownError if user privileges cannot be determined.
    """
    try:
        return os.getuid() == 0
    except AttributeError:
        pass
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1
    except AttributeError:
        raise AdminStateUnknownError


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
    this.log.debug('Trying to move ' + currentDir + os.sep + filename + ' to ' + targetDir + os.sep + filename)
    if not os.path.isfile(targetDir + os.sep + filename):
        os.rename(currentDir + os.sep + filename, targetDir + os.sep + filename)
        this.log.debug('Moved and renamed ' + str(currentDir + os.sep + filename) + ' to ' + str(targetDir + os.sep + filename) + ' with os.rename()')
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
        this.log.error('Too many duplicates of ' + targetDir + os.sep + filename + '. File has no extention. Program ignoring this file as a failsafe.')
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
        this.log.debug('attemptCounter=' + str(attemptCounter) + ' newFilename=' + newFilename)

        if os.path.isfile(targetDir + os.sep + newFilename):
            attemptCounter = attemptCounter + 1
            this.log.debug(targetDir + os.sep + newFilename + ' already exists. Trying again. ')
        elif attemptCounter > 11:
            this.log.error('Too many duplicates of ' + targetDir + os.sep + filename + ' found. Possible error. Program ignoring this file as a failsafe.')
        else:
            break
    os.rename(currentDir + os.sep + filename, targetDir + os.sep + newFilename)
    this.log.debug('Moved and renamed ' + str(currentDir + os.sep + filename) + ' to ' + str(targetDir + os.sep + newFilename) + ' with os.rename()')
    return None


# this function detirmines if the file passed to it should be ignored
def validTarget(name, subdir, filename, walkDir):
    # this.log.debug( 'Testing if '+subdir + os.sep + filename+' should be ignored.')  # Creates excessive this.debug messages, uncomment when needed
    if filename[0] == ".":
        return False
    if not os.path.isfile(this.rootDir + os.sep + "fileSortConfiguration" + os.sep + "globalIgnored.config"):
        this.log.critical(this.rootDir + os.sep + "fileSortConfiguration" + os.sep + "globalIgnored.config not found. ")
        sys.exit(configNotFound)
    try:
        with open(this.rootDir + os.sep + "fileSortConfiguration" + os.sep + "globalIgnored.config", "r") as file:
            del file
    except PermissionError:
        this.log.critical(" Unable to open " + this.rootDir + os.sep + "fileSortConfiguration" + os.sep + "globalIgnored.config")
        sys.exit(permissionsErr)

    with open(this.rootDir + os.sep + "fileSortConfiguration" + os.sep + "globalIgnored.config", "r") as a_file:  # read the global ignore file
        for line in a_file:
            ignored = line.strip()  # parse each line as a regex pattern
            try:  # try to match the file to the patterns
                ignoreCondition = re.compile(ignored)
                filenameMatches = len(re.findall(ignoreCondition, filename))
                subdirMatches = len(re.findall(ignoreCondition, subdir))
                walkDirMatches = len(re.findall(ignoreCondition, walkDir))
                for pattern in blacklistDir:
                    #this.log.debug("matching pattern: " + pattern)  # Creates excessive this.debug messages, uncomment when needed
                    if re.match(pattern, subdir) is not None and not this.includeSysFiles:
                        this.log.error(subdir + os.sep + filename + " is presumed to be a system file and will not be moved for saftey reasons. It has matched the pattern: " + pattern + " If you believe this is mistaken, please open an issue. This decision can be overridden with the --this.includeSysFiles flag. " + str(re.match(r"/Users/.*", subdir)))
                        return False
                    elif re.match(pattern, subdir) is not None and this.includeSysFiles:
                        this.log.warning(subdir + os.sep + filename + " is presumed to be a system file and is not recommended to be sorted. This decision to ignore it was overriden by the USER with the --this.includeSysFiles flag. It has matched the pattern: " + pattern + " If you believe this is mistaken, please open an issue. ")
                        return False
                # check if it matches in the directory relative to the absolute directory of the file
                if (subdirMatches + filenameMatches) > walkDirMatches and walkDir in subdir:
                    if (subdir + os.sep + filename) not in this.globalIgnored:  # this.globalIgnored is an array with absolute this.path of all ignored files.
                        # if the file has not been mentioned, tell user.
                        this.log.debug(filename + ' matched ' + ignored)
                        this.log.info(subdir + os.sep + filename + " ignored according to Global configuration file. ")
                        this.globalIgnored.append(subdir + os.sep + filename)
                        this.log.debug(str(subdir + os.sep + filename) + ' added to this.globalIgnored.')
                        if (this.rootDir + os.sep + this.misplacedDirName) in subdir:
                            # warning the user that the file is in the misplaced folder and is ignored.
                            this.log.warning(subdir + os.sep + filename + " is in the misplaced folder. ")
                    return False
            except re.error:
                if ignored not in this.globalWarned:
                    # re.error is raised for invalid regex expression, causes the line in ignore file to be skipped
                    this.log.error("Invalid regular expression given: "+ignored)
                    this.globalWarned.append(ignored)
                    this.log.debug(ignored+' added to this.globalWarned.')
    filebinIgnore = this.rootDir + os.sep + "fileSortConfiguration" + os.sep + name + "Ignored.config"  # read the local ignored file (not applied globally)
    if os.path.isfile(filebinIgnore):
        # this.log.debug('Ignore file found for '+name) #Creates excessive this.debug messages, uncomment when needed
        try:
            with open(filebinIgnore, "r") as file:
                del file
        except PermissionError:
            this.log.critical(" Unable to open " + filebinIgnore)
            sys.exit(permissionsErr)
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
                        this.log.debug('Filename: ' + subdir + os.sep + filename + ' matched in filename ' + filenameMatches + ' times, matched in subdir ' + subdirMatches + 'times, and matched in walkDir' + walkDirMatches + ' times. ')
                        this.log.info(subdir + os.sep + filename + " ignored according to local configuration file for " + name + ". ")
                        if (this.rootDir + os.sep + this.misplacedDirName) in subdir:
                            # warning the user that the file is in the misplaced folder and is ignored.
                            this.log.warning(subdir + os.sep + filename + " is in the misplaced folder. ")
                        return False
                except re.error:
                    # skip invalid expressions
                    this.log.error("Invalid regular expression given: " + ignored)
    # else: #Creates excessive this.debug messages, uncomment when needed
        # this.log.debug('Local ignoredConfig not found for ' + filebinIgnore) #Creates excessive this.debug messages, uncomment when needed
    return True


# put different versions of the same file together. Files named as TAG_filenameV1.0,
# TAG_filenameV2.1,TAG_filenameV3.0 will be put into folder called filename
def groupVersions():
    global projectNames
    this.config.read(this.rootDir + os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config')
    this.log.debug('Read config file for groupVersions() function')
    tag_separator = this.config.get('GlobalSettings', 'tag_separator')
    name = this.currentFilebin.get('name', this.filebin)
    this.log.debug('testing if versions can be bunched for ' + name)
    if this.config.has_option(this.filebin, 'dirName'):
        dirName = this.currentFilebin.get('dirName', this.filebin)
        this.log.debug('dirName: ' + dirName)
        absolutedir = None
    elif this.config.has_option(this.filebin, 'absolutedir'):
        dirName = None
        absolutedir = this.currentFilebin.get('absolutedir', this.filebin)
        this.log.debug('absolutedir: ' + absolutedir)
    else:
        this.log.critical('Directory for ' + name + ' is missing.')
        sys.exit(missingDirErr)

    if this.config.has_option(this.filebin, 'tag'):
        if this.currentFilebin.get('tag', this.filebin) != '':
            tag = this.currentFilebin.get('tag', this.filebin)
        else:
            tag = None
        if this.config.has_option(this.filebin, 'tagAlternative'):
            if this.currentFilebin.get('tagAlternative') != '':
                tagAlternative = this.currentFilebin.get('tagAlternative')
            else:
                tagAlternative = None
        else:
            tagAlternative = ""
        if tag is not None:
            regexForTag = r"^[\S\s]*" + re.escape(tag) + re.escape(tag_separator) + r"([\S\s]*)V\d[\S\s]*$"
        else:
            regexForTagAlt = None
        this.log.debug('groupVersions -> regexForTag: ' + regexForTag)
        if tagAlternative is not None:
            regexForTagAlt = r"^[\S\s]*" + re.escape(tagAlternative) + re.escape(tag_separator) + r"([\S\s]*)V\d[\S\s]*$"
            this.log.debug('groupVersions -> regexForTagAlt: ' + regexForTagAlt)
        else:
            regexForTagAlt = None
    else:
        regexForTag = None
        regexForTagAlt = None

    if this.config.has_option(this.filebin, 'regex_tag'):
        if this.currentFilebin.get('regex_tag') != '':
            regex_tag = this.currentFilebin.get('regex_tag')
            regex_tag = '^' + regex_tag + r"([\S\s]*)V\d[\S\s]*$"
            this.log.debug('groupVersions -> regex_tag: ' + regex_tag)
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
        walkDir = this.rootDir + os.sep + dirName
    elif absolutedir is not None:
        walkDir = absolutedir
    this.log.debug('groupVersions -> Directory set to ' + walkDir)
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(name, subdir, filename, walkDir):
                    projName = matchVersionFormat(regexTag, regexTagAlt, regex_tag, filename)
                    if projName is not None:
                        this.log.debug('Found potential project: ' + projName + ' with count: ' + str(projectNames.count(projName)) + ' and project threshold met: ' + str(projectNames.count(projName) >= this.groupthreshold) + ' and subdirectory: ' + subdir)
                        if (projectNames.count(projName) >= this.groupthreshold) and (projName not in subdir):  # if there are numerous versions AND it is not in a folder with the project name:

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

                                    if validTarget(name, subdir2, filename2, walkDir) and matchProject and (projName not in subdir2):
                                        duplicateFileWorkaround(subdir2, subdir2 + os.sep + projName, filename2)  # move files into this directory.
                                        this.log.debug('groupVersions -> Multiple versions of filename2 found and moved into ' + subdir2 + os.sep + projName)

    else:
        this.log.critical('Directory for ' + name + ' not valid.')  # quit if the given directory for the folder to sort is invalid, see topmost if condition.
        sys.exit(filebinDirErr)


# remove misplaced files and move to misplaced folder.
def removeMisplaced():
    name = this.currentFilebin.get('name', this.filebin)
    this.log.debug('Removing misplaced files in ' + name)
    this.config.read(this.rootDir + os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config')
    tag_separator = this.config.get('GlobalSettings', 'tag_separator')
    if this.config.has_option(this.filebin, 'dirName') and this.config.has_option(this.filebin, 'absolutedir'):
        this.log.critical('Two directories given for ' + name + ' Aborting due to possible conflict. Please remove 1 of the 2 directories. ')
        sys.exit(filebinDirErr)
    elif this.config.has_option(this.filebin, 'dirName'):
        dirName = this.currentFilebin.get('dirName', this.filebin)
        absolutedir = None
    elif this.config.has_option(this.filebin, 'absolutedir'):
        dirName = None
        absolutedir = this.currentFilebin.get('absolutedir', this.filebin)
    else:
        this.log.critical('Directory for ' + name + ' is missing.')
        sys.exit(missingDirErr)
    ignoreMisplaced = this.config.getboolean(this.filebin, 'ignoreMisplaced')
    this.misplacedDirName = this.currentFilebin.get('misplacedDirName', "Misplaced")
    if this.config.has_option(this.filebin, 'tag'):
        if this.currentFilebin.get('tag', this.filebin) != '':
            tag = this.currentFilebin.get('tag', this.filebin)
        else:
            tag = None
        if this.config.has_option(this.filebin, 'tagAlternative'):
            if this.currentFilebin.get('tagAlternative') != '':
                tagAlternative = this.currentFilebin.get('tagAlternative')
            else:
                tagAlternative = None
        else:
            tagAlternative = None
        if tag is not None:
            regexForTag_F = r"[\S\s]*"+re.escape(tag)+re.escape(tag_separator)+r"[\S\s]*"
            this.log.debug(name + ' -> removeMisplaced -> regexForTag_F: ' + regexForTag_F)
            regexForTag_B = r"[\S\s]*" + re.escape(tag_separator) + re.escape(tag) + r"[\S\s]*"
            this.log.debug(name + ' -> removeMisplaced -> regexForTag_B: ' + regexForTag_B)
        else:
            regexForTag_F = None
            regexForTag_B = None
        if tagAlternative is not None:
            regexForTagAlt_F = r"[\S\s]*" + re.escape(tagAlternative) + re.escape(tag_separator) + r"[\S\s]*"
            this.log.debug(name + ' -> removeMisplaced -> regexForTagAlt_F: ' + regexForTagAlt_F)
            regexForTagAlt_B = r"[\S\s]*" + re.escape(tag_separator) + re.escape(tagAlternative) + r"[\S\s]*"
            this.log.debug(name + ' -> removeMisplaced -> regexForTagAlt_B: ' + regexForTagAlt_B)
        else:
            regexForTagAlt_F = None
            regexForTagAlt_B = None
    else:
        regexForTag_F = None
        regexForTagAlt_F = None
    if this.config.has_option(this.filebin, 'regex_tag'):
        if this.currentFilebin.get('regex_tag') != '':
            regex_tag = this.currentFilebin.get('regex_tag')
            this.log.debug(name + ' -> removeMisplaced -> regex_tag: ' + regex_tag)
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
            this.log.warning("Invalid regular expression" + regex_tag + " given for " + name + "Ignore file, skipping ...")
    this.log.debug(name + ' -> removeMisplaced -> Compiled all regex tags.')
    if dirName is not None:
        walkDir = this.rootDir + os.sep + dirName
    elif absolutedir is not None:
        walkDir = absolutedir
    this.log.debug(name + ' -> removeMisplaced -> walkDir: ' + walkDir)
    if not os.path.isdir(this.rootDir + os.sep + this.misplacedDirName):
        os.mkdir(this.rootDir + os.sep + this.misplacedDirName)
        this.log.debug(name + ' -> removeMisplaced -> Created Misplaced Folder b/c it may be needed later')
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(name, subdir, filename, walkDir):
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
                            this.log.info(filepath + " is misplaced")
                        else:
                            duplicateFileWorkaround(subdir, this.rootDir + os.sep + this.misplacedDirName, filename)
                            this.log.info(filepath + " is misplaced and placed into " + this.misplacedDirName)
    else:
        this.log.critical('Directory for ' + name + ' not valid.')
        sys.exit(filebinDirErr)


# return the misplaced files to the directories they belong in if they have the corresponding tags.
def returnMisplaced():
    this.config.read(this.rootDir + os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config')
    tag_separator = this.config.get('GlobalSettings', 'tag_separator')
    name = this.currentFilebin.get('name', this.filebin)
    this.log.debug('Returning misplaced files for ' + name)
    if this.config.has_option(this.filebin, 'dirName') and this.config.has_option(this.filebin, 'absolutedir'):
        this.log.critical('Two directories given for ' + name + ' Aborting due to possible conflict. Please remove 1 of the 2 directories. ')
        sys.exit(filebinDirErr)
    elif this.config.has_option(this.filebin, 'dirName'):
        dirName = this.currentFilebin.get('dirName', this.filebin)
        absolutedir = None
    elif this.config.has_option(this.filebin, 'absolutedir'):
        dirName = None
        absolutedir = this.currentFilebin.get('absolutedir', this.filebin)
    else:
        this.log.critical('Directory for ' + name + ' is missing.')
        sys.exit(missingDirErr)
    ignoreMisplaced = this.config.getboolean(this.filebin, 'ignoreMisplaced')
    if this.config.has_option(this.filebin, 'tag'):
        if this.currentFilebin.get('tag', this.filebin) is not None:
            tag = this.currentFilebin.get('tag', this.filebin)
        else:
            tag = None
        if this.config.has_option(this.filebin, 'tagAlternative'):
            if this.currentFilebin.get('tagAlternative') != '':
                tagAlternative = this.currentFilebin.get('tagAlternative')
            else:
                tagAlternative = None
        else:
            tagAlternative = None
        if tag is not None:
            regexForTag_F = r"[\S\s]*" + re.escape(tag) + re.escape(tag_separator) + r"[\S\s]*"
            this.log.debug(name + ' -> returnMisplaced -> regexForTag_F: ' + regexForTag_F)
            regexForTag_B = r"[\S\s]*" + re.escape(tag_separator) + re.escape(tag) + r"[\S\s]*"
            this.log.debug(name + ' -> returnMisplaced -> regexForTag_B: ' + regexForTag_B)
        else:
            regexForTag_F = None
        if tagAlternative is not None:
            regexForTagAlt_F = r"[\S\s]*" + re.escape(tagAlternative) + re.escape(tag_separator) + r"[\S\s]*"
            this.log.debug(name + ' -> returnMisplaced -> regexForTagAlt_F: ' + regexForTagAlt_F)
            regexForTagAlt_B = r"[\S\s]*" + re.escape(tag_separator) + re.escape(tagAlternative) + r"[\S\s]*"
            this.log.debug(name + ' -> returnMisplaced -> regexForTagAlt_B: ' + regexForTagAlt_B)
        else:
            regexForTagAlt_F = None
    else:
        regexForTag_F = None
        regexForTagAlt_F = None

    if this.config.has_option(this.filebin, 'regex_tag'):
        if this.currentFilebin.get('regex_tag') != '':
            regex_tag = this.currentFilebin.get('regex_tag')
            this.log.debug(name + ' -> returnMisplaced -> regex_tag: ' + regex_tag)
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
            this.log.error("Invalid regular expression given for " + name + ", skipping ...")

    walkDir = this.rootDir + os.sep + this.misplacedDirName
    this.log.debug(name + ' -> returnMisplaced -> walkDir: ' + walkDir)
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(name, subdir, filename, walkDir):
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
                            this.log.info(filepath + " should be returned")
                        else:
                            if dirName is not None:
                                # ignore if duplicate files exist.
                                duplicateFileWorkaround(subdir, this.rootDir + os.sep + dirName, filename)
                                this.log.info(filepath + " returned")
                            elif absolutedir is not None:
                                duplicateFileWorkaround(subdir, absolutedir, filename)
                                this.log.info(filepath + " returned")
                            else:
                                this.log.critical('Directory for ' + name + ' not valid.')
                                sys.exit(filebinDirErr)
    else:
        log.critical('Directory for ' + name + ' not valid.')
        sys.exit(filebinDirErr)


def parseArgs():
    parser = argparse.ArgumentParser(description='Generates settings for fileSort.py')
    ifCreateLog = parser.add_mutually_exclusive_group(required=False)
    ifCreateLog.add_argument("--logDir", dest='logDir', default='', required=False)
    ifCreateLog.add_argument("--noLog", action='store_true', default=False, required=False)
    verbosityLevel = parser.add_mutually_exclusive_group(required=False)
    verbosityLevel.add_argument('--debug', action='store_const',const=2, default=0)  # this.debug
    verbosityLevel.add_argument('--verbose', '-v', action='count', default=0)  # warning, info, this.debug
    verbosityLevel.add_argument('--quiet', '-q', action='count', default=0)  # critical, error/exception, warning
    parser.add_argument("--rootDir", dest='path', default=os.getcwd(), required=False)
    parser.add_argument("--includeSysFiles", action='store_true', default=False, required=False)
    args = parser.parse_args()
    this.logDir = args.logDir
    this.verbose = args.verbose
    this.quiet = args.quiet
    this.path = args.path
    this.noLog = args.noLog
    this.debug = args.debug
    this.includeSysFiles = args.includeSysFiles


def inputArgs(logDir, verbose, quiet, noLog, debug, includeSysFiles, path):
    this.logDir = logDir
    this.verbose = verbose
    this.quiet = quiet
    this.path = path
    this.noLog = noLog
    this.debug = debug
    this.includeSysFiles = includeSysFiles


def main():
    verbosityLevel = this.verbose - this.quiet + this.debug
    if not os.path.isdir(this.path):
        this.path = os.getcwd()
    if not this.noLog:
        if this.logDir == '':
            this.logDir = os.getcwd() + os.sep + 'Logs'
        if not os.path.isdir(this.logDir):
            try:
                os.mkdir(this.logDir)
            except FileNotFoundError:
                if verbosityLevel != -3:
                    print('ERROR: Unable to use "Logs" directory (defaults under working directory). Consider specifying a directory for log file with "--this.logDir" or pass "--this.noLog" option. ')
                sys.exit(cantCreateErr)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if not this.noLog:
        fh = logging.FileHandler(this.logDir + os.sep + 'fileSorter.log')
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        this.log.addHandler(fh)

    if not this.noLog:
        fhW = logging.FileHandler(this.logDir + os.sep + 'fileSorterwarning.log')
        fhW.setLevel(logging.WARNING)
        fhW.setFormatter(formatter)
        this.log.addHandler(fhW)

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
            ch.setLevel(logging.this.debug)
        else:
            print("ERROR: Invalid verbosity level setting given. Use max -vv or -qqq, or --this.verbose, --this.quiet, --this.debug")
            sys.exit(invalidSettingErr)
        this.log.addHandler(ch)

    this.log.debug('this.logDir = '+str(this.logDir)+', this.verbose = '+str(this.verbose)+', this.quiet = '+str(this.quiet)+', this.path = '+str(this.path))

    if isUserAdmin():
        this.log.warning("Please do not run this script as root if possible to prevent accidental breaking of system components. \n Please ensure that the configuration files are all protected with the neccessary permissions to prevent abuse. ")

    # Read Config
    this.config = configparser.ConfigParser()
    if not os.path.isfile(this.path + os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config') or not os.path.isfile(this.path + os.sep + 'fileSortConfiguration' + os.sep + 'globalIgnored.config'):
        this.log.critical("Configuration files not found at "+this.path + os.sep + 'fileSortConfiguration. Expected fileSort.config and globalIgnored.config')
        sys.exit(configNotFound)

    try:
        this.config.read(this.path + os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config')
    except PermissionError:
        this.log.critical("Unable to open configuration file because of permissions error")
        sys.exit(permissionsErr)

    if ('GlobalSettings' in this.config):
        GlobalSettings = this.config['GlobalSettings']
        this.rootDir = GlobalSettings.get('rootDir')
        this.misplacedDirName = GlobalSettings.get('misplacedDirName', "Misplaced")
        rootStatus = this.config.getboolean('GlobalSettings', 'rootStatus')
        removeMisplacedDir = this.config.getboolean('GlobalSettings', 'removeMisplacedDir')
        groupversions = this.config.getboolean('GlobalSettings', 'groupversions')
        this.groupthreshold = this.config.getint('GlobalSettings', 'groupthreshold')

        this.log.debug('rootDir = ' + str(this.rootDir) + ', misplacedDirName = ' + str(this.misplacedDirName) + ', rootStatus = ' + str(rootStatus) + ', removeMisplacedDir = ' + str(removeMisplacedDir) + ', groupversions = ' + str(groupversions) + ', groupthreshold = ' + str(this.groupthreshold))
        if not rootStatus:
            this.log.warning("fileSort.py disabled in configfile")
            sys.exit(0)

        if os.path.isdir(this.rootDir):
            this.rootDir = this.rootDir
        else:
            this.log.critical("Invalid root directory given." + this.rootDir)
            sys.exit(rootDirErr)
    else:
        this.log.critical("Global Configuration not found in fileSort.config configuration file. ")
        sys.exit(invalidSettingErr)

    existMisplaced = os.path.isdir(this.rootDir + os.sep + this.misplacedDirName)
    Sections = this.config.sections()
    filebinCount = len(Sections)

    for i in range(1, filebinCount+1):
        this.filebin = "Bin" + str(i)
        if this.config.has_section(this.filebin):
            this.currentFilebin = this.config[this.filebin]
            active = this.config.getboolean(this.filebin, 'active')
            if active:
                removeMisplaced()
            else:
                this.log.info(this.currentFilebin.get('name', this.filebin) + " skipped.")

    for i in range(1, filebinCount+1):
        this.this.log.debug("Testing if Bin "+str(i)+" found.")
        this.filebin = "Bin" + str(i)
        if not this.config.has_section(this.filebin):
            this.log.debug("Bin "+str(i)+" not found.")
        else:
            this.log.debug("Bin "+str(i)+" found.")
            this.currentFilebin = this.config[this.filebin]
            active = this.config.getboolean(this.filebin, 'active')
            if active:
                returnMisplaced()
                if groupversions:
                    groupVersions()
            else:
                this.log.info(this.currentFilebin.get('name',this.filebin)+" skipped.")

    misplacedFiles = os.listdir(this.rootDir + os.sep + this.misplacedDirName)
    if os.path.exists(this.rootDir + os.sep + this.misplacedDirName + os.sep + ".DS_Store"):
        misplacedFiles.remove('.DS_Store')
    if (not misplacedFiles) and removeMisplacedDir and existMisplaced:
        this.log.info("Removed " + this.misplacedDirName + " because uneeded")
        if os.path.exists(this.rootDir + os.sep + this.misplacedDirNameos.sep+".DS_Store"):
            os.remove(this.rootDir + os.sep + this.misplacedDirName + os.sep + ".DS_Store")
        os.rmdir(this.rootDir + os.sep + this.misplacedDirName)
    elif (not misplacedFiles) and removeMisplacedDir and not existMisplaced:
        if os.path.exists(this.rootDir + os.sep + this.misplacedDirName + os.sep + ".DS_Store"):
            os.remove(this.rootDir + os.sep + this.misplacedDirName + os.sep + ".DS_Store")
        os.rmdir(this.rootDir + os.sep + this.misplacedDirName)
    elif misplacedFiles:
        this.log.warning("Files have been misplaced. Please return them manually. The program is unable to detirmine the intended filebin for these files. ")
    else:
        this.log.info("Keeping "+this.misplacedDirName+" folder empty.")


if __name__ == '__main__':
    parseArgs()
    main()
