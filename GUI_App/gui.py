from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QTextEdit, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys, os

class RootPage(QWidget):
    def __init__(self):
        super(RootPage,self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("FileSorter")
        self.setGeometry(400,400,300,260)

        self.targetPathLabel = QLabel(self)
        self.targetPathLabel.setText("Target Directory:")

        self.targetPath = QTextEdit()
        self.targetPath.setPlainText(os.getcwd())

        self.option1btn = QPushButton(self)
        self.option1btn.setText("Rename Files")          #text
        self.option1btn.setShortcut('Ctrl+R')  #shortcut key
        self.option1btn.clicked.connect(self.confirmRename)
        self.option1btn.setToolTip("Renames the files of a directory. Shortcut Ctrl+R") #Tool tip

        self.option2btn = QPushButton(self)
        self.option2btn.setText("Setup FileSorter")  # text
        self.option2btn.setShortcut('Ctrl+S')  # shortcut key
        self.option2btn.clicked.connect(self.confirmConfigure)
        self.option2btn.setToolTip("Set up the configuration files of FileSorter for a directory.")  # Tool tip

        self.option3btn = QPushButton(self)
        self.option3btn.setText("Setup FileSorter [Advanced Setup]")  # text
        self.option3btn.setShortcut('Ctrl+A')  # shortcut key
        self.option3btn.clicked.connect(self.confirmConfigure)
        self.option3btn.setToolTip("Set up the configuration files of FileSorter for a directory. Advanced Options available.")  # Tool tip

        self.option4btn = QPushButton(self)
        self.option4btn.setText("Sort Files")  # text
        self.option4btn.setShortcut('Ctrl+D')  # shortcut key
        self.option4btn.clicked.connect(self.confirmSort)
        self.option4btn.setToolTip("Sort the files of a directory with existing FileSorter configuration.")  # Tool tip

        layout = QVBoxLayout()
        layout.addWidget(self.targetPathLabel)
        layout.addWidget(self.targetPath)
        layout.addWidget(self.option1btn)
        layout.addWidget(self.option2btn)
        layout.addWidget(self.option3btn)
        layout.addWidget(self.option4btn)
        self.setLayout(layout)


    def confirmAction(self,action):
        reply = QMessageBox.question(self, (action[0].upper()+action[1::]), f'Are you sure you want to {action} this directory?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply

    def confirmSort(self):
        action = "sort"
        self.confirmAction(action)

    def confirmRename(self):
        action = "rename"
        self.confirmAction(action)

    def confirmConfigure(self):
        action = "configure"
        self.confirmAction(action)



app = QApplication(sys.argv)

ex = RootPage()
ex.show()
sys.exit(app.exec_())