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
    dirName=thisBin.get('dirName',bin)
    tag=thisBin.get('tag',bin)
    if config.has_option(bin,'tagAlternative'):
        tagAlternative=thisBin.get('tagAlternative')
    else:
        tagAlternative=""
    regexForTag= r"[\S\s]*"+tag+r"_([\S\s]*)V\d[\S\s]*"
    if tagAlternative!="":
        regexForTagAlt= r"[\S\s]*"+tagAlternative+r"_([\S\s]*)V\d[\S\s]*"
    else:
        regexForTagAlt=regexForTag
    regexTag = re.compile(regexForTag+'$', re.I)
    regexTagAlt = re.compile(regexForTagAlt+'$', re.I)

    walkDir=rootDir+os.sep+dirName
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir,name,subdir,filename):
                    projName=""
                    if re.search(regexTag, filename):
                        projName=regexTag.match(filename).group(1)
                        projectNames.append(projName)
                        print(projName)
                    elif re.search(regexTagAlt, filename):
                        projName=regexTagAlt.match(filename).group(1)
                        projectNames.append(projName)
                        print(projName)
                    if projName!="":
                        if (projectNames.count(projName) >= groupthreshold) and (projName not in subdir):
                            if not os.path.isdir(subdir+os.sep+projName):
                                os.mkdir(subdir+os.sep+projName)
                            for subdir2, dirs2, files2 in os.walk(walkDir):
                                for filename2 in files2:
                                    filepath2 = subdir2 + os.sep + filename2
                                    if validTarget(rootDir,name,subdir2,filename2) and (re.search(regexTag, filename2) or re.search(regexTagAlt, filename2)) and (projName not in subdir2):
                                        os.rename(filepath2, subdir2+os.sep+projName+os.sep+filename2)

def removeMisplaced(rootDir,misplacedDirName,thisBin):
    name=thisBin.get('name',bin)
    dirName=thisBin.get('dirName',bin)
    tag=thisBin.get('tag',bin)
    if config.has_option(bin,'tagAlternative'):
        tagAlternative=thisBin.get('tagAlternative')
    else:
        tagAlternative=""
    ignoreMisplaced=config.getboolean(bin, 'ignoreMisplaced')
    misplacedDirName=thisBin.get('misplacedDirName',"Misplaced")
    regexForTag_F= r"[\S\s]*"+tag+"_"+r"[\S\s]*"
    regexForTag_B= r"[\S\s]*"+"_"+tag+r"[\S\s]*"
    regexForTagAlt_F= r"[\S\s]*"+tagAlternative+"_"+r"[\S\s]*"
    regexForTagAlt_B= r"[\S\s]*"+"_"+tagAlternative+r"[\S\s]*"
    regexTag_F = re.compile(r'('+regexForTag_F+')$', re.I)
    regexTag_B = re.compile(r'('+regexForTag_B+')$', re.I)
    if tagAlternative!="":
        regexTagAlt_F = re.compile(r'\.('+regexForTagAlt_F+')$', re.I)
        regexTagAlt_B = re.compile(r'\.('+regexForTagAlt_B+')$', re.I)
    else:
        regexTagAlt_F= regexTag_F
        regexTagAlt_B= regexTag_B
    walkDir=rootDir+os.sep+dirName
    if not os.path.isdir(rootDir+os.sep+misplacedDirName):
        os.mkdir(rootDir+os.sep+misplacedDirName)
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir,name,subdir,filename):
                    if (regexTag_F.search(filename) or regexTag_B.search(filename)) or (regexTagAlt_F.search(filename) or regexTagAlt_B.search(filename)):
                        continue
                    else:
                        if ignoreMisplaced:
                            print(filepath+" is misplaced")
                        else:
                            print(filepath+" is misplaced and placed into "+misplacedDirName)
                            os.rename(filepath, rootDir+os.sep+misplacedDirName+os.sep+filename)

def returnMisplaced(rootDir,misplacedDirName,thisBin):
    config.read(path+'/fileSortConfiguration/fileSort.config')
    name=thisBin.get('name',bin)
    dirName=thisBin.get('dirName',bin)
    ignoreMisplaced=config.getboolean(bin, 'ignoreMisplaced')
    tag=thisBin.get('tag',thisBin)
    if config.has_option(bin,'tagAlternative'):
        tagAlternative=thisBin.get('tagAlternative')
    else:
        tagAlternative=""
    regexForTag_F= ".*"+tag+"_"+r"[\S\s]*"
    regexForTag_B= ".*"+"_"+tag+r"[\S\s]*"
    regexForTagAlt_F= ".*"+tagAlternative+"_"+r"[\S\s]*"
    regexForTagAlt_B= ".*"+"_"+tagAlternative+r"[\S\s]*"
    regexTag_F = re.compile(r'('+regexForTag_F+')$', re.I)
    regexTag_B = re.compile(r'('+regexForTag_B+')$', re.I)
    if tagAlternative!="":
        regexTagAlt_F = re.compile(r'\.('+regexForTagAlt_F+')$', re.I)
        regexTagAlt_B = re.compile(r'\.('+regexForTagAlt_B+')$', re.I)
    else:
        regexTagAlt_F= regexTag_F
        regexTagAlt_B= regexTag_B

    walkDir=rootDir+os.sep+misplacedDirName
    if os.path.isdir(walkDir):
        for subdir, dirs, files in os.walk(walkDir):
            for filename in files:
                filepath = subdir + os.sep + filename
                if validTarget(rootDir,name,subdir,filename):
                    if (regexTag_F.search(filename) or regexTag_B.search(filename)) or (regexTagAlt_F.search(filename) or regexTagAlt_B.search(filename)):
                        if ignoreMisplaced:
                            print(filepath+" should be returned")
                        else:
                            print(filepath+" returned")
                            os.rename(filepath, rootDir+os.sep+dirName+os.sep+filename)


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
if (not misplacedFiles) and removeMisplacedDir:
    print("Removed " + misplacedDirName + " because uneeded")
    if os.path.exists(rootDir+os.sep+misplacedDirName+"/.DS_Store"):
        os.remove(rootDir+os.sep+misplacedDirName+"/.DS_Store")
    os.rmdir(rootDir+os.sep+misplacedDirName)
else:
    print("Keeping "+misplacedDirName+" in accordance to user settings")
