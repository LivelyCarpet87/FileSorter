import configparser
import argparse
import os
parser = argparse.ArgumentParser(description='Takes in settings for fileSort.py')
parser.add_argument("--rootDir",dest='path',default=os.getcwd(),required=False)
parser.add_argument("--genBinIgnored",nargs='?',dest='genBinIgnored',const=True,default=False,required=False)
args = parser.parse_args()
path=args.path
genBinIgnored=args.genBinIgnored
if not os.path.isdir(path):
    path=os.getcwd()

if not os.path.isdir(path+"/fileSortConfiguration"):
    os.mkdir(path+"/fileSortConfiguration")
f = open("./fileSortConfiguration/globalIgnored.config", "w")

config = configparser.ConfigParser(allow_no_value=True)
config['GlobalSettings'] = {'# Root Directory of bins to be sorted': None,
                            'rootDir': path,
                            '# Enable fileSort? (Global)': None,
                            'rootStatus': 'OFF',
                            '# Name for directory of misplaced files': None,
                            'misplacedDirName': 'Misplaced',
                            '# Remove Misplaced directory when it is empty?': None,
                            'removeMisplacedDir': 'OFF'}

binCount=1
for name in os.listdir(path):
    if os.path.isdir(name) and not os.path.islink(name) and not name=="Misplaced" and not name=="fileSortConfiguration":
        binName="Bin"+str(binCount)
        config.add_section(binName)
        config.set(binName, '# User-given name for this bin')
        config.set(binName,"name",name)
        config.set(binName, '# Enable this bin?')
        config.set(binName,"active","ON")
        config.set(binName, '# Name of folder for this bin')
        config.set(binName,"dirname",name)
        config.set(binName, '# Tag for files in this bin. ')
        config.set(binName, '# File called randchar_MISC_randchar.randtype will be put into MISC bin. ')
        config.set(binName, '# Filename must contain TAG_ in its name to be put into bin')
        config.set(binName,"tag",name[0:4].upper())
        config.set(binName, '# Alternative tag for files in this bin. ')
        config.set(binName,"tagAlternative",name[0:4])
        config.set(binName, '# Ignore misplaced files belonging to this bin in this bin or misplaved folder?')
        config.set(binName,"ignoreMisplaced","OFF")
        if genBinIgnored:
            f = open("./fileSortConfiguration/"+name+"Ignored.config", "w")
        binCount=binCount+1

with open('./fileSortConfiguration/fileSort.config', 'w') as configfile:
    config.write(configfile)
