import os
import re
import time

def main():
    print("Current working directory (folder location): " + os.getcwd())
    print("Options:\n\
    1. Rename files to include tag in current folder\n\
    2. Rename files to include tag in current folder and all subfolders\n\
    3. Rename files to remove tag in current folder\n\
    4. Rename files to remove tag in current folder and all subfolders\n\
    5. Change current working directory (the folder you are in)\n\
    6. Exit\n\
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
    elif userChoice == 5:
        changeWorkingDir()
    elif userChoice == 6:
        exit()
    else:
        print("Invalid choice option.")

def changeWorkingDir():
    print("Current working directory is " + str(os.getcwd()))
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
        else:
            print("Invalid input. Please give a valid path.")

    os.chdir(newDir)


def renamingOptions():
    print("Verify the renaming of all files manually (or rename automatically)? [Y]/n")
    while True:
        choice = input("> ")
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
    print("Please input the tag to be included into the filenames. ")
    print('For example, "APPL" will cause the file named "myfile.txt"')
    print('to be renamed into "APPL_myfile.txt" ')
    while True:
        tag = input("TAG: ")
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
    print("Please input the tag to be removed from the filenames. ")
    print('For example, "APPL" will cause the file named "APPL_myfile.txt" to be renamed into "myfile.txt" ')
    print('The program will exit this mode if no files with the tag are found. ')
    while True:
        tag = input("TAG: ")
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
    interateThrough = renamingOptions()
    tag = renamingTag() + '_'
    for name in os.listdir(os.getcwd()):
        if os.path.isfile('.' + os.sep + name) and not os.path.isfile('.' + os.sep + tag + name) and tag not in name and name[0] != '.':
            if interateThrough:
                while True:
                    choice = input("Rename " + str(name) +" > ")
                    if type(choice) == str:
                        if choice in ["Y","y","Yes","yes","YES"]:
                            os.rename('.' + os.sep + name, '.' + os.sep + tag + name)
                            break
                        else:
                            print("\nSkipped "+ name +" per user choice. ")
                            break
            else:
                os.rename('.' + os.sep + name, '.' + os.sep + tag + name)
        elif os.path.isfile('.' + os.sep + tag + name):
            print("\nSkipped "+name+" because "+tag + name+ " exists already.")
        elif tag in name:
            print("\nSkipped " + name + " because it already contains the tag.")


def renameFolderAndSub():
    interateThrough = renamingOptions()
    tag = renamingTag() + '_'
    for path, folders, names in os.walk(".", topdown=False):
        for name in names:
            nameFull = os.path.join(path, name)
            if os.path.isfile(nameFull) and not os.path.isfile(path + os.sep + tag + name) and tag not in name and name[0] != '.':
                if interateThrough:
                    while True:
                        choice = input("Rename " + str(nameFull) +" > ")
                        if type(choice) == str:
                            if choice in ["Y","y","Yes","yes","YES"]:
                                os.rename(path + os.sep + name, path + os.sep + tag + name)
                                break
                            else:
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
    interateThrough = renamingOptions()
    tag = undoRenamingTag() + '_'
    for name in os.listdir(os.getcwd()):
        if undoRename(tag,name) is not None:
            newName = undoRename(tag,name)
            if os.path.isfile('.' + os.sep + name) and not os.path.isfile('.' + os.sep + newName) and tag not in newName and name[0] != '.':
                if interateThrough:
                    while True:
                        choice = input("Rename " + str(name) +" > ")
                        if type(choice) == str:
                            if choice in ["Y","y","Yes","yes","YES"]:
                                os.rename('.' + os.sep + name, '.' + os.sep + newName)
                                break
                            else:
                                print("\nSkipped "+ name +" per user choice. ")
                                break
                else:
                    os.rename('.' + os.sep + name, '.' + os.sep + newName)
            elif os.path.isfile('.' + os.sep + newName):
                print("\nSkipped "+name+" because "+newName+ " exists already.")
            elif tag in newName:
                print("\nSkipped " + name + " because the program is uncertain how to remove the tag from the name.")


def undoRenameFolderAndSub():
    interateThrough = renamingOptions()
    tag = undoRenamingTag() + '_'
    for path, folders, names in os.walk(".", topdown=False):
        for name in names:
            if undoRename(tag,name) is not None:
                newName = undoRename(tag,name)
                nameFull = os.path.join(path, name)
                if os.path.isfile(nameFull) and not os.path.isfile(path + os.sep + newName) and tag not in newName and name[0] != '.':
                    if interateThrough:
                        while True:
                            choice = input("Rename " + str(nameFull) + " to " + newName +"? > ")
                            if type(choice) == str:
                                if choice in ["Y","y","Yes","yes","YES"]:
                                    os.rename(path + os.sep + name, path + os.sep + newName)
                                    break
                                else:
                                    print("Skipped "+ nameFull +" per user choice.\n")
                                    break
                    else:
                        os.rename(path + os.sep + name, path + os.sep + newName)
                elif os.path.isfile(path + os.sep + newName):
                    print("\nSkipped "+path + os.sep + name+" because "+path + os.sep + tag + name+ " exists already.")
                elif tag in newName:
                    print("\nSkipped " + path + os.sep + name+" because the program is uncertain how to remove the tag from the name.")


while True:
    main()
