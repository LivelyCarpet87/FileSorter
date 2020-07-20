# Guide For Absolute Beginners

## Terminology

Target Folder: This is the folder the app is targeting. You can change the targeted folder as explained [later](#usage). All the actions of the application will be made to the targeted folder (and possibly subfolders).

Subfolder: The folder in a certain folder is the subfolder of the folder. If folder A is a subfolder of folder B, folder A is IN folder B. 

TAG: This is a combination of letters placed at the start of a file's name, followed by an underscore, to mark where a certain file belongs. 

Filebin: For the sake of this tutorial, we will refer to all the folders where files are to be sorted into as filebins. They are folders with a pre-designated tag. 

## How It Works (Overview)

The file sorter sorts files in filebins according to a few rules. If a file does not have the tag of a filebin, but is placed inside a filebin, it is deemed as misplaced and moved to a folder called Misplaced. If a file has a tag of a filebin and is in the folder Misplaced, it will be moved to the filebin with the matching tag. Files that do not match any tag will remain in the Misplaced folder. 

## Usage

### Basics

The program interacts with the user via a terminal window or command prompt. Users can choose menu items by entering the corresponding integer and hitting enter. Default choices are usually outlined in square brackets such as `[Y]/n`. By hitting enter without any input, the default value is taken. The program will alert you of invalid inputs and reasons why should such a scenario occur. 

### Step 1: Changing the Target Folder

On the main menu, select option 6 to change target mode. Then type out the full path you wish to change the target folder to and hit enter. A easier way is to simply drag the folder into the terminal window or command prompt. If you entered this mode by accident, enter `!back` to go back. 

### Step 2: Setting Up the Sorter For a Folder

On the main menu, select the option 2 to set up a folder. The file sorter will be set up to sort all the subfolders of the folder you set up, also now known as filebins. Follow the prompts for the setup to give each filebin a name and tags. 

### Step 2.5-ish: Renaming Files To Include the Right Tag

To rename files according to your setup, please first change the target folder with **Step 1** to the folder whose files you wish to rename. Then select option 1 on the main menu to rename files. Then select option 2 to rename ALL files in the folder. Follow the defaullt choice (Yes) when asked if you wish to manually verify the renaming. Then please enter the tag you wish to add to the start of file names. The choose as the program asks you if you wish to rename certain files. Simply enter y/n to confirm or deny. 

### Step 3: Running the Sorter

Follow **Step 1** to change the target folder to the folder whose **subfolders** you wish to sort. Use option 4 to sort the folder and confirm. Double check that you agree with all the actions the sorter took. Undo any actions you didn't like manually. Then press enter to continue. (The screen will be cleared of the output.)

### Step 4: Scheduling the Sorter

Use **Step 1** to change the target folder to the folder you wish. Then select option 5 to schedule the sorter. Enter the interval in minutes you wish to run the file sorter at and confirm. 

### Final Step: Exiting

Note that for current versions the sorter would not be able to run when you exit, so try not to exit when you have scheduled a sorter. The program will simply standby as the sorter waits in the background. Once you exit, all the scheduled sorters will be saved and reloaded at the next time you open the app in a file called `jobs.json`. 

### Note
It is OK to set up multiple directories and schedule muiltiple Sorters. The above steps are written in the order that it is assumed the user will experience them in. All of these actions can be conducted in any order as long as prerequisites are met. 