import os
import configparser
import fileRename
import FileSorter
import initFileSorter
import logging
import sys
scriptDir = os.getcwd()


def sortFiles():
    print("Are you certain you wish to sort this directory?")
    if input("Press Y to continue: ") not in ['y','Y']:
        return None
    if not os.path.isfile(os.getcwd()+ os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config'):
        print("The directory you gave is not set up. Configuration file not found. Please first set it up. ")
        print(os.getcwd()+ os.sep + 'fileSortConfiguration' + os.sep + 'fileSort.config not found.' )
        input("Press any key to continue: ")
        return None
    FileSorter.inputArgs("", 1, 0, True, 0, False, os.getcwd())
    FileSorter.main()
    print("\n\n\nThe above output will BE CLEARED once you continue. Please INSPECT the output text, especially the warnings and errors. \
    When automated, the above data would be saved in the logs. ")
    input("Press any key to continue: ")
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
    input("Press any key to continue: ")
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
        pass
    elif userChoice == 6:
        fileRename.changeWorkingDir()
    elif userChoice == 7:
        exit()
    else:
        print("Invalid choice option.")


if __name__ == '__main__':
    while True:
        os.system('clear')
        main()
