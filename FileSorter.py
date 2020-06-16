import sys
import os
import re
import configparser
import argparse

def validTarget(rootDir,name,subdir,filename):
    if filename[0]==".":
        return False

    with open(rootDir+"/fileSortConfiguration/globalIgnored.config", "r") as a_file:
        for line in a_file:
            ignored = line.strip()
            if ignored in subdir:
                return False
    binIgnore=name+"Ignored.config"
    if os.path.exists(binIgnore):
        with open(binIgnore, "r") as a_file:
            for line in a_file:
                ignored = line.strip()
                if ignored in subdir:
                    return False
    return True

def bunchVersions(rootDir,thisBin,groupthreshold):
    projectNames=[]

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
        regexForTag= r"[\S\s]*"+tag+r"_([\S\s]*)V\d[\S\s]*"
        if tagAlternative!= None:
            regexForTagAlt= r"[\S\s]*"+tagAlternative+r"_([\S\s]*)V\d[\S\s]*"
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
        regex_tag = re.compile(regex_tag+r"V\d[\S\s]*"+'$', re.I)

    if dirName != None:
        walkDir=rootDir+os.sep+dirName
    elif absolutedir != None:
        walkDir=absolutedir

    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir,name,subdir,filename):
                    projName=""
                    matched = False
                    try:
                        if re.search(regexTag, filename) and not matched:
                            projName=regexTag.match(filename).group(1)
                            projectNames.append(projName)
                            matched = True
                    except NameError:
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
                        if (projectNames.count(projName) >= groupthreshold) and (projName not in subdir):
                            if not os.path.isdir(subdir+os.sep+projName):
                                os.mkdir(subdir+os.sep+projName)
                            for subdir2, dirs2, files2 in os.walk(walkDir):
                                for filename2 in files2:
                                    filepath2 = subdir2 + os.sep + filename2
                                    if validTarget(rootDir,name,subdir2,filename2) and (re.search(regexTag, filename2) or re.search(regexTagAlt, filename2)) and (projName not in subdir2):
                                        os.rename(filepath2, subdir2+os.sep+projName+os.sep+filename2)
    else:
        sys.exit('Directory for '+name+' not valid.')
def removeMisplaced(rootDir,misplacedDirName,thisBin):
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
    misplacedDirName=thisBin.get('misplacedDirName',"Misplaced")
    if config.has_option(bin,'tag'):
        tag=thisBin.get('tag',bin)
        if config.has_option(bin,'tagAlternative'):
            tagAlternative=thisBin.get('tagAlternative')
        else:
            tagAlternative=""
        regexForTag_F= r"[\S\s]*"+tag+"_"+r"[\S\s]*"
        regexForTag_B= r"[\S\s]*"+"_"+tag+r"[\S\s]*"
        if tagAlternative!= None:
            regexForTagAlt_F= r"[\S\s]*"+tagAlternative+"_"+r"[\S\s]*"
            regexForTagAlt_B= r"[\S\s]*"+"_"+tagAlternative+r"[\S\s]*"
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
            print("Invalid regular expression given for "+name+", skipping ...")

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
                if validTarget(rootDir,name,subdir,filename):
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
                            print(filepath+" is misplaced")
                        else:
                            try:
                                if os.path.isfile(rootDir+os.sep+misplacedDirName+os.sep+filename):
                                    print('Too many duplicates of '+name+"/"+filename+'. Program ignoring this file as a failsafe.')
                                else:
                                    os.rename(filepath, rootDir+os.sep+misplacedDirName+os.sep+filename)
                                    print(filepath+" is misplaced and placed into "+misplacedDirName)
                            except OSError:
                                print('Too many duplicates of '+name+"/"+filename+'. Program ignoring this file as a failsafe. ')


    else:
        sys.exit('Directory for '+name+' not valid.')

def returnMisplaced(rootDir,misplacedDirName,thisBin):
    config.read(path+'/fileSortConfiguration/fileSort.config')
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
        regexForTag_F= r"[\S\s]*"+tag+"_"+r"[\S\s]*"
        regexForTag_B= r"[\S\s]*"+"_"+tag+r"[\S\s]*"
        if tagAlternative!= None:
            regexForTagAlt_F= r"[\S\s]*"+tagAlternative+"_"+r"[\S\s]*"
            regexForTagAlt_B= r"[\S\s]*"+"_"+tagAlternative+r"[\S\s]*"
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
            print("Invalid regular expression given for "+name+", skipping ...")

    walkDir=rootDir+os.sep+misplacedDirName
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir,name,subdir,filename):
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
                            print(filepath+" should be returned")
                        else:
                            try:
                                if dirName != None:
                                    if os.path.isfile(rootDir+os.sep+dirName+os.sep+filename):
                                        print('Too many duplicates of '+name+"/"+filename+'. Program ignoring this file as a failsafe. Return Canceled.')
                                    else:
                                        os.rename(filepath, rootDir+os.sep+dirName+os.sep+filename)
                                        print(filepath+" returned")
                                elif absolutedir != None:
                                    if os.path.isfile(absolutedir+os.sep+filename):
                                        print('Too many duplicates of '+name+"/"+filename+'. Program ignoring this file as a failsafe. Return Canceled.')
                                    else:
                                        os.rename(filepath, absolutedir+os.sep+filename)
                                        print(filepath+" returned")
                                else:
                                    sys.exit('Directory for '+name+' not valid.')
                            except OSError:
                                print('Too many duplicates of '+name+"/"+filename+'. Program ignoring this file as a failsafe. Return Canceled.')

    else:
        sys.exit('Directory for '+name+' not valid.')

#Read Config
config = configparser.ConfigParser()

parser = argparse.ArgumentParser(description='Takes in settings for fileSort.py')
parser.add_argument("--rootDir",dest='path',default=os.getcwd(),required=False)
args = parser.parse_args()
path=args.path
if not os.path.isdir(path):
    path=os.getcwd()

if not os.path.isfile(path+'/fileSortConfiguration/fileSort.config') or not os.path.isfile(path+'/fileSortConfiguration/globalIgnored.config'):
    print(path+'/fileSortConfiguration/fileSort.config')
    sys.exit("ERROR: Configuration files not found")

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
        sys.exit("fileSort.py disabled in configfile")

    if os.path.isdir(rootDir):
        rootDir=rootDir
    else:
        print("Error: Invalid root directory.")

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
            print(thisBin.get('name',bin)+" skipped.")

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
            print(thisBin.get('name',bin)+" skipped.")

misplacedFiles=os.listdir(rootDir+os.sep+misplacedDirName)
if os.path.exists(rootDir+os.sep+misplacedDirName+"/.DS_Store"):
    misplacedFiles.remove('.DS_Store')
if (not misplacedFiles) and removeMisplacedDir and existMisplaced:
    print("Removed " + misplacedDirName + " because uneeded")
    if os.path.exists(rootDir+os.sep+misplacedDirName+"/.DS_Store"):
        os.remove(rootDir+os.sep+misplacedDirName+"/.DS_Store")
    os.rmdir(rootDir+os.sep+misplacedDirName)
elif (not misplacedFiles) and removeMisplacedDir and not existMisplaced:
    if os.path.exists(rootDir+os.sep+misplacedDirName+"/.DS_Store"):
        os.remove(rootDir+os.sep+misplacedDirName+"/.DS_Store")
    os.rmdir(rootDir+os.sep+misplacedDirName)
elif misplacedFiles:
    print("Files have been misplaced. Please return them manually. The program is unable to detirmine the intended bin for these files. ")
else:
    print("Keeping "+misplacedDirName+" in accordance to user settings")
