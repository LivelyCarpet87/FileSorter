import os
import re
import time

def main():
    print("Current target folder: " + os.getcwd())
    if __name__ == '__main__':
        print("Options:\n\
    1. Add tag to files in target folder\n\
    2. Add tag to files in target folder AND ALL subfolders\n\
    3. Remove tag from files in target folder\n\
    4. Rename tag from files in target folder AND ALL subfolders\n\
    5. Change target folder\n\
    6. Exit\n\
    ")
    else:
        print("Options:\n\
    1. Add tag to files in target folder\n\
    2. Add tag to files in target folder AND ALL subfolders\n\
    3. Remove tag from files in target folder\n\
    4. Rename tag from files in target folder AND ALL subfolders\n\
    6. Back\n\
    ")
    while True:
        userChoice = input("Choice Num > ")
        try:
            userChoice = int(userChoice)
        except ValueError:
            pass
        if userChoice in range(1,6+1):
            break
        else:
            print("Invalid input. Please enter a corresponding integer. ")
    if userChoice == 1:
        renameFolder()
    elif userChoice == 2:
        renameFolderAndSub()
    elif userChoice == 3:
        undoRenameFolder()
    elif userChoice == 4:
        undoRenameFolderAndSub()
    elif userChoice == 5 and __name__ == '__main__':
        changeWorkingDir()
    elif userChoice == 6:
        if __name__ == '__main__':
            exit()
        else:
            os.system('clear')
            return None
    else:
        print("Invalid choice option.")

def changeWorkingDir():
    print("Current target folder is " + str(os.getcwd()))
    time.sleep(1)
    print("Current subfolders:")
    subfolders = [ f.name for f in os.scandir(os.getcwd()) if f.is_dir() ]
    for name in subfolders:
        if name[0] is not '.':
            time.sleep(0.1)
            print(name)
    while True:
        newDir = input("Change to: ")
        if os.path.isdir(newDir):
            break
        elif newDir == "!back":
            return None
        else:
            print("Invalid input. Please give a valid folder path. To go back, enter" + '"!back"')

    os.chdir(newDir)


def renamingOptions():
    print("Verify the renaming of all files manually (or rename automatically)? [Y]/n")
    print("To go back, enter" + '"!back"')
    while True:
        choice = input("> ")
        if choice == "!back":
            return None
        if choice is "":
            choice = "y"
        if type(choice) == str:
            if choice in ["Y","y","Yes","yes","YES"]:
                return True
            elif choice in ["N","n","No","no","NO"]:
                print("Are you sure? This could be difficult to fix if done wrong. ")
                confirm = input("Press enter to confirm. Press any other key to cancel: ")
                if confirm == "":
                    return False
                else:
                    return True


def renamingTag():
    print('Please input the tag to be included into the filenames. \
For example, "APPL" will cause the file named "myfile.txt" \
to be renamed into "APPL_myfile.txt" ')
    print("To go back, enter" + '"!back"')
    while True:
        tag = input("TAG: ")
        if tag == "!back":
            return ""
        if type(tag) == str:
            if len(tag) >= 2 and '_' not in tag and ' ' not in tag and os.sep not in tag and tag[0] != '.':
                return tag
            elif tag[0] == '.':
                print("Invalid tag, tag cannot begin with a period because filenames begining with a period will cause file to be hidden. ")
            elif len(tag) <= 2:
                print("Invalid tag, please ensure tag is at least 2 letters. ")
            elif '_' in tag or ' ' in tag or os.sep in tag:
                print("Please do not put underscores or whitespaces or " + os.sep +" in the tag. A trailing underscore is not needed. ")
        else:
            print("Invalid tag, please enter a valid string. ")


def undoRenamingTag():
    print('Please input the tag to be removed from the filenames. \
For example, "APPL" will cause the file named "APPL_myfile.txt" to be renamed into "myfile.txt" \
The program will exit this mode if no files with the tag are found. ')
    print("To go back, enter" + '"!back"')
    while True:
        tag = input("Remove TAG: ")
        if tag == "!back":
            return ""
        if type(tag) == str:
            if len(tag) >= 2 and '_' not in tag and ' ' not in tag and os.sep not in tag and tag[0] != '.':
                return tag
            elif tag[0] == '.':
                print("Invalid tag, tags must not start with a period. ")
            elif len(tag) <= 2:
                print("Invalid tag, tag must be at least 2 letters. ")
            elif '_' in tag or ' ' in tag or os.sep in tag:
                print("Tag cannot contain underscores, spaces or "+os.sep)
        else:
            print("Invalid tag, please enter a valid string. ")


def renameFolder():
    iterateThrough = renamingOptions()
    if iterateThrough is None:
        return None
    tag = renamingTag() + '_'
    if tag == '_':
        return None
    for name in os.listdir(os.getcwd()):
        if os.path.isfile('.' + os.sep + name) and not os.path.isfile('.' + os.sep + tag + name) and tag not in name and name[0] != '.':
            if iterateThrough:
                while True:
                    choice = input("Rename " + str(name) +" y/n> ")
                    if type(choice) == str:
                        if choice in ["Y","y","Yes","yes","YES"]:
                            os.rename('.' + os.sep + name, '.' + os.sep + tag + name)
                            break
                        elif choice in ["N","n","No","no","NO"]:
                            print("\nSkipped "+ name +" per user choice. ")
                            break
            else:
                os.rename('.' + os.sep + name, '.' + os.sep + tag + name)
        elif os.path.isfile('.' + os.sep + tag + name):
            print("\nSkipped "+name+" because "+tag + name+ " exists already.")
        elif tag in name:
            print("\nSkipped " + name + " because it already contains the tag.")


def renameFolderAndSub():
    iterateThrough = renamingOptions()
    if iterateThrough is None:
        return None
    tag = renamingTag() + '_'
    if tag == '_':
        return None
    for path, folders, names in os.walk(".", topdown=False):
        for name in names:
            nameFull = os.path.join(path, name)
            if os.path.isfile(nameFull) and not os.path.isfile(path + os.sep + tag + name) and tag not in name and name[0] != '.':
                if iterateThrough:
                    while True:
                        choice = input("Rename " + str(nameFull) +" > ")
                        if type(choice) == str:
                            if choice in ["Y","y","Yes","yes","YES"]:
                                os.rename(path + os.sep + name, path + os.sep + tag + name)
                                break
                            elif choice in ["N","n","No","no","NO"]:
                                print("Skipped "+ nameFull +" per user choice.\n")
                                break
                else:
                    os.rename(path + os.sep + name, path + os.sep + tag + name)
            elif os.path.isfile(path + os.sep + tag + name):
                print("\nSkipped "+path + os.sep + name+" because "+path + os.sep + tag + name+ " exists already.")
            elif tag in name:
                print("\nSkipped " + path + os.sep + name+" because it already contains the tag.")

def undoRename(tag,filename):
    excludeTag = re.compile(r'^(.*)'+ re.escape(tag) +r'(.*)$')
    if re.search(excludeTag,filename) == None:
        return None
    else:
        return re.fullmatch(excludeTag,filename).group(1) + re.fullmatch(excludeTag,filename).group(2)


def undoRenameFolder():
    iterateThrough = renamingOptions()
    if iterateThrough is None:
        return None
    tag = undoRenamingTag() + '_'
    if tag == '_':
        return None
    for name in os.listdir(os.getcwd()):
        if undoRename(tag,name) is not None:
            newName = undoRename(tag,name)
            if os.path.isfile('.' + os.sep + name) and not os.path.isfile('.' + os.sep + newName) and tag not in newName and name[0] != '.':
                if iterateThrough:
                    while True:
                        choice = input("Rename " + str(name) +" > ")
                        if type(choice) == str:
                            if choice in ["Y","y","Yes","yes","YES"]:
                                os.rename('.' + os.sep + name, '.' + os.sep + newName)
                                break
                            elif choice in ["N","n","No","no","NO"]:
                                print("\nSkipped "+ name +" per user choice. ")
                                break
                else:
                    os.rename('.' + os.sep + name, '.' + os.sep + newName)
            elif os.path.isfile('.' + os.sep + newName):
                print("\nSkipped "+name+" because "+newName+ " exists already.")
            elif tag in newName:
                print("\nSkipped " + name + " because the program is uncertain how to remove the tag from the name.")


def undoRenameFolderAndSub():
    iterateThrough = renamingOptions()
    if iterateThrough is None:
        return None
    tag = undoRenamingTag() + '_'
    if tag == '_':
        return None
    for path, folders, names in os.walk(".", topdown=False):
        for name in names:
            if undoRename(tag,name) is not None:
                newName = undoRename(tag,name)
                nameFull = os.path.join(path, name)
                if os.path.isfile(nameFull) and not os.path.isfile(path + os.sep + newName) and tag not in newName and name[0] != '.':
                    if iterateThrough:
                        while True:
                            choice = input("Rename " + str(nameFull) + " to " + newName +"? > ")
                            if type(choice) == str:
                                if choice in ["Y","y","Yes","yes","YES"]:
                                    os.rename(path + os.sep + name, path + os.sep + newName)
                                    break
                                elif choice in ["N","n","No","no","NO"]:
                                    print("Skipped "+ nameFull +" per user choice.\n")
                                    break
                    else:
                        os.rename(path + os.sep + name, path + os.sep + newName)
                elif os.path.isfile(path + os.sep + newName):
                    print("\nSkipped "+path + os.sep + name+" because "+path + os.sep + tag + name+ " exists already.")
                elif tag in newName:
                    print("\nSkipped " + path + os.sep + name+" because the program is uncertain how to remove the tag from the name.")

if __name__ == '__main__':
    while True:
        main()
