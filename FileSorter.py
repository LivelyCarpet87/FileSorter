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
    regexForTag_F= ".*"+tag+"_"+r"[\S\s]*"
    regexForTag_B= ".*"+"_"+tag+r"[\S\s]*"
    regexForTagAlt_F= ".*"+tagAlternative+"_"+r"[\S\s]*"
    regexForTagAlt_B= ".*"+"_"+tagAlternative+r"[\S\s]*"
    regexTag = re.compile(r'('+regexForTag+')$', re.I)
    if tagAlternative!="":
        regexTagAlt_F = re.compile(r'\.('+tagAlternative_F+')$', re.I)
        regexTagAlt_B = re.compile(r'\.('+tagAlternative_B+')$', re.I)
    else:
        regexTagAlt_F= regexTag_F
        regexTagAlt_B= regexTag_B
    walkDir=rootDir+"/"+dirName
    if not os.path.isdir(rootDir+"/"+misplacedDirName):
        os.mkdir(rootDir+"/"+misplacedDirName)
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
                            os.rename(filepath, rootDir+"/"+misplacedDirName+"/"+filename)

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
    regexTag = re.compile(r'('+regexForTag+')$', re.I)
    if tagAlternative!="":
        regexTagAlt_F = re.compile(r'\.('+tagAlternative_F+')$', re.I)
        regexTagAlt_B = re.compile(r'\.('+tagAlternative_B+')$', re.I)
    else:
        regexTagAlt_F= regexTag_F
        regexTagAlt_B= regexTag_B

    walkDir=rootDir+"/"+misplacedDirName
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
                            os.rename(filepath, rootDir+"/"+dirName+"/"+filename)


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
        else:
            print(thisBin.get('name',bin)+" skipped.")


misplacedFiles=os.listdir(rootDir+"/"+misplacedDirName)
if os.path.exists(rootDir+"/"+misplacedDirName+"/.DS_Store"):
    misplacedFiles.remove('.DS_Store')
if (not misplacedFiles) and removeMisplacedDir:
    print("Removed " + misplacedDirName + " because uneeded")
    if os.path.exists(rootDir+"/"+misplacedDirName+"/.DS_Store"):
        os.remove(rootDir+"/"+misplacedDirName+"/.DS_Store")
    os.rmdir(rootDir+"/"+misplacedDirName)
else:
    print("Keeping "+misplacedDirName+" in accordance to user settings")
