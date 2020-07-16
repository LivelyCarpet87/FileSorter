from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.widget import Widget
from os.path import isdir
import re


class filebin:


    def __init__(self):
        self.active = "ON"
        self.name = ""
        self.dir = ""
        self.tag = ""
        self.tagAlt = ""
        self.regex_tag = ""


    def activeState(state):
        if state == True:
            self.active = "ON"
        else:
            self.active = "OFF"


    def setDir(dir):
        if isdir(dir):
            self.dir = dir
        else:
            raise NotADirectoryError


class fileSorter:


    def __init__(self):
        self.rootDir = ""
        self.rootStatus = "ON"
        self.misplacedDirName = "Misplaced"
        self.groupversions = "OFF"
        self.groupthreshold = 3
        self.tag_separator = '_'
        self.filebins = []

    def changeRootStatus(self,state):
        if state == True:
            self.rootStatus = "ON"
        elif state == False:
            self.rootStatus = "OFF"
        else:
            raise ValueError


    def getRootStatus(self):
        if self.rootStatus == "ON":
            return True
        elif self.rootStatus == "OFF":
            return False
        else:
            raise ValueError

    def setRootDir(dir):
        if isdir(dir):
            self.rootDir = dir
        else:
            raise NotADirectoryError


    def changeGroupVersionsState(state):
        if state == True:
            self.groupversions = "ON"
        else:
            self.groupversions = "OFF"

    def addFilebin(active, name, dir, tag, altTag, regex_tag):
        newBin = filebin()
        newBin.activeState(active)
        newBin.name = name
        newBin.setDir(dir)
        newBin.tag = tag
        newBin.altTag = altTag
        newBin.regex_tag = regex_tag
        self.filebins.append(newBin)


defaultFileSorter = fileSorter()


class editFileSorterScreen(GridLayout,Screen):


    def __init__(self, **kwargs):
        super(editFileSorterScreen, self).__init__(**kwargs)

        self.cols = 1

        self.label1 = Label(text = "Edit File Sorter",font_size = 30)
        self.add_widget(self.label1)

        self.rootStatus = defaultFileSorter.rootStatus
        self.label2 = Label(text = "Status : ", font_size = 30)
        self.add_widget(self.label2)


        if defaultFileSorter.getRootStatus():
            self.toggleRootStatus = ToggleButton(text='ON', group='RootState', state='down')
        else:
            self.toggleRootStatus = ToggleButton(text='OFF', group='RootState')

        self.toggleRootStatus.bind(on_press = self.toggledRootStatus)
        self.add_widget(self.toggleRootStatus)


    def toggledRootStatus(self, instance):
        if defaultFileSorter.getRootStatus():
            defaultFileSorter.changeRootStatus(False)
        elif not defaultFileSorter.getRootStatus():
            defaultFileSorter.changeRootStatus(True)
        else:
            raise ValueError
        print(defaultFileSorter.rootStatus)
        sm.switch_to(editFileSorterScreen(), direction='right', duration=0.001)


    def update(self):
        editFileSorterScreen.rootStatus = defaultFileSorter.rootStatus



class mainScreen(GridLayout,Screen):


    def __init__(self, **kwargs):
        super(mainScreen, self).__init__(**kwargs)

        self.cols = 1

        self.smallGrid = GridLayout()
        self.smallGrid.cols = 1

        self.label1 = Label(text = "File Sorter")
        self.smallGrid.add_widget(self.label1)

        self.label2 = Label(text = "Status : Enabled")
        self.smallGrid.add_widget(self.label2)


        self.editFileSorter = Button(text = "Edit", font_size = 40)
        self.editFileSorter.bind(on_press = self.pressedEdit)
        self.smallGrid.add_widget(self.editFileSorter)

        self.add_widget(self.smallGrid)

    def pressedEdit(self, instance):
        print("button pressed")
        sm.switch_to(editFileSorterScreen(), direction='left')


sm = ScreenManager()
sm.add_widget(mainScreen(name='mainScreen'))
sm.add_widget(editFileSorterScreen(name='editFileSorterScreen'))


class FileSorterGUIApp(App):
    def build(self):
        Clock.schedule_interval(editFileSorterScreen.update, 1.0/60.0)
        return sm

if __name__ == '__main__':
    FileSorterGUIApp().run()
