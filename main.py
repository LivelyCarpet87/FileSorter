import os
import configparser
import fileRename
import FileSorter
import initFileSorter
import logging
import sys
import threading
import time
import atexit
import json
import ast

scriptDir = os.path.dirname(os.path.realpath(__file__))
jobs = []

class threadedSorter():
    def __init__(self, runInterval, rootDir):
        self.enabled = True
        self.runInterval = runInterval
        self.verbosity = -3
        self.rootDir = rootDir
        self.includeSysFiles = False
        self.thisSorter = None


    def targetDir(self):
        self.rootDir = os.getcwd()


    def thread_func(self):
        while self.enabled:
            for index in range(self.runInterval*60):
                if self.enabled:
                    time.sleep(1)
                else:
                    print("Thread Killed")
                    break
            if self.enabled:
                FileSorter.inputArgs("Logs",self.verbosity,0,False,0,self.includeSysFiles,self.rootDir)


def launch(threadedSorter):
    threadedSorter.thisSorter = threading.Thread(target=threadedSorter.thread_func, args=())
    threadedSorter.thisSorter.start()


def kill(threadedSorter):
    threadedSorter.enabled = False


def loadJobs():
    if os.path.isfile("./jobs.json"):
        f = open("./jobs.json", "r")
        jobsSnapshot = json.loads(f.read())
        for jobSave in jobsSnapshot:
            jobSave = jobsSnapshot[jobSave]
            runInterval = jobSave['runInterval']
            rootDir = jobSave['rootDir']
            newJob = threadedSorter(runInterval,rootDir)
            launch(newJob)
            jobs.append(newJob)


def scheduleNewSorter():
    print("Are you certain you wish to sort this directory?")
    if input("Press Y to continue: ") not in ['y','Y']:
        return None
    if not os.path.isfile(os.getcwd()+ os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config'):
        print("The directory you gave is not set up. Configuration file not found. Please first set it up. ")
        print(os.getcwd()+ os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config not found.' )
        input("Press enter to continue: ")
        return None
    print("Please enter the interval you wish to run the file sorter at, as an \
integer number of minutes. Please note that this app must be open for it to run. ")
    while True:
        interval = input("Interval(Min): ")
        try:
            interval = int(interval)
            break
        except ValueError:
            print("Please enter a valid integer. ")
    newJob = threadedSorter(interval,os.getcwd())
    launch(newJob)
    jobs.append(newJob)


def removeScheduledSorter():
    print("Are you certain you wish to NOT sort this directory?")
    if input("Press Y to continue: ") not in ['y','Y']:
        return None
    if not os.path.isfile(os.getcwd()+ os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config'):
        print("The directory you gave is not set up. Configuration file not found.")
        input("Press enter to continue: ")
        return None
    for sorter in jobs:
        if sorter.rootDir == os.getcwd():
            kill(sorter)
            time.sleep(10)
            jobs.remove(sorter)
    input("Press enter to continue: ")


def scheduler():
    if jobs is not []:
        print("Scheduled:")
        for job in jobs:
            print(job.rootDir)
    print("Choices:\n\
    1. Schedule another sorter for target folder\n\
    2. UNschedule an existing sorter\n\
    3. Back")
    while True:
        userChoice = input("Choice Num > ")
        try:
            userChoice = int(userChoice)
        except ValueError:
            pass
        if userChoice in range(1,3+1):
            break
        else:
            print("Invalid input. Please enter a corresponding integer. ")

    if userChoice == 1:
        scheduleNewSorter()
    elif userChoice == 2:
        removeScheduledSorter()
    elif userChoice == 3:
        return None
    else:
        print("Invalid choice option.")


def sortFiles():
    print("Are you certain you wish to sort this directory?")
    if input("Press Y to continue: ") not in ['y','Y']:
        return None
    if not os.path.isfile(os.getcwd()+ os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config'):
        print("The directory you gave is not set up. Configuration file not found. Please first set it up. ")
        print(os.getcwd()+ os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config not found.' )
        input("Press enter to continue: ")
        return None
    FileSorter.inputArgs("", 1, 0, True, 0, False, os.getcwd())
    FileSorter.main()
    print("\n\n\nThe above output will BE CLEARED once you continue. Please INSPECT the output text, especially the warnings and errors. \
    When automated, the above data would be saved in the logs. ")
    input("Press enter to continue: ")
    return None


def setupSorter(advanced):
    if advanced:
        print("Would you like to also sort any other folder that is not a subdirectory of the target folder?")
        while True:
            choice = input("y/[N] > ")
            if choice in ["y","Y","yes","Yes","YES"]:
                includeDir = []
                while True:
                    print("Please enter the FULL path of another folder to sort. Enter" + '"!skip" to skip.')
                    while True:
                        userEntry = input("Dir:")
                        if os.path.isdir(userEntry):
                            includeDir.append(userEntry)
                            break
                        elif userEntry == '!skip':
                            break
                        else:
                            print("Invalid Directory. ")
                    print("Would you like to add another folder? ")
                    choice = None
                    while choice not in ["y","Y","yes","Yes","YES","n","N","no","No","NO",""]:
                        choice = input("y/[N] > ")
                    if choice in ["y","Y","yes","Yes","YES"]:
                        pass
                    elif choice in ["n","N","no","No","NO",""]:
                        break
                if includeDir == []:
                    includeDir = None
                break
            elif choice in ["n","N","no","No","NO",""]:
                includeDir = None
                break
        initFileSorter.setArgs(os.getcwd(), True, includeDir)
        initFileSorter.interactiveMain(advanced)
    else:
        initFileSorter.setArgs(os.getcwd(), True, None)
        initFileSorter.interactiveMain(advanced)
    input("Press enter to continue: ")


def main():
    print("Target Folder:")
    print(os.getcwd()+"\n")
    print("Main Menu:\n\
    1. Rename files\n\
    2. Setup the file sorter\n\
    3. Setup the file sorter [Advanced Setup]\n\
    4. Sort the files\n\
    5. Schedule the file sorter\n\
    6. Change target folder\n\
    7. Exit\n\
    ")
    while True:
        userChoice = input("Choice Num > ")
        try:
            userChoice = int(userChoice)
        except ValueError:
            pass
        if userChoice in range(1,7+1):
            break
        else:
            print("Invalid input. Please enter a corresponding integer. ")

    if userChoice == 1:
        os.system('clear')
        fileRename.main()
    elif userChoice == 2:
        setupSorter(False)
    elif userChoice == 3:
        setupSorter(True)
    elif userChoice == 4:
        sortFiles()
    elif userChoice == 5:
        scheduler()
    elif userChoice == 6:
        fileRename.changeWorkingDir()
    elif userChoice == 7:
        saveJobs()
        killJobs()
        sys.exit()
    else:
        print("Invalid choice option.")


def saveJobs():
    print("Saving Jobs to "+scriptDir + os.sep +"jobs.json")
    jobsSnapshot = {}
    counter=1
    for job in jobs:
        jobsSnapshot["Job"+str(counter)] = { 'enabled' : job.enabled,
        'runInterval':job.runInterval,
        'verbosity':job.verbosity,
        'rootDir':job.rootDir,
        'includeSysFiles':job.includeSysFiles}
        counter = counter +1
    output = json.dumps(jobsSnapshot)
    if os.path.isfile(scriptDir + os.sep +"jobs.json"):
        os.remove(scriptDir + os.sep +"jobs.json")
    with open(scriptDir + os.sep +"jobs.json", "w") as outfile:
        outfile.write(output)


def killJobs():
    print("Killing Jobs")
    jobsSnapshot = {}
    counter=1
    for job in jobs:
        kill(job)


if __name__ == '__main__':
    try:
        loadJobs()
        while True:
            os.system('clear')
            main()
    except KeyboardInterrupt:
        saveJobs()
        killJobs()
        sys.exit()
