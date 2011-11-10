# -.- coding: utf-8 -.-
from PyQt4 import QtGui, QtCore

import icons

class ListWidgetItem(QtGui.QWidget):
    moveUp = QtCore.pyqtSignal(QtGui.QWidget)
    moveDown = QtCore.pyqtSignal(QtGui.QWidget)
    
    def __init__(self,Parent,ItemText):
        QtGui.QWidget.__init__(self,Parent)
        
        self.ItemText = QtGui.QLabel(ItemText)
        self.ItemText.setStyleSheet("font-weight: bold;")
        
        self.ItemRemove = QtGui.QPushButton()
        self.ItemRemove.setAutoDefault(False)
        self.ItemRemove.setIcon(QtGui.QIcon(":icons/delete.ico"))
        self.ItemRemove.setFixedSize(20,20)
        self.ItemRemove.clicked.connect(self.removeMe)

        self.ItemMoveUp = QtGui.QPushButton()
        self.ItemMoveUp.setAutoDefault(False)
        self.ItemMoveUp.setIcon(QtGui.QIcon(":icons/up.ico"))
        self.ItemMoveUp.setFixedSize(20,20)
        self.ItemMoveUp.clicked.connect(self.moveMeUp)

        self.ItemMoveDown = QtGui.QPushButton()
        self.ItemMoveDown.setAutoDefault(False)
        self.ItemMoveDown.setIcon(QtGui.QIcon(":icons/down.ico"))
        self.ItemMoveDown.setFixedSize(20,20)
        self.ItemMoveDown.clicked.connect(self.moveMeDown)

        WidgetLayout = QtGui.QHBoxLayout()
        WidgetLayout.setContentsMargins(3,3,3,3)
        WidgetLayout.addWidget(self.ItemText)
        WidgetLayout.addWidget(self.ItemMoveUp)
        WidgetLayout.addWidget(self.ItemMoveDown)
        WidgetLayout.addWidget(self.ItemRemove)

        self.setLayout(WidgetLayout)

    def removeMe(self):
        self.setParent(None)

    def moveMeUp(self):
        self.moveUp.emit(self)

    def moveMeDown(self):
        self.moveDown.emit(self)

class ListWidget(QtGui.QWidget):
    def __init__(self,Parent=None):
        QtGui.QWidget.__init__(self,Parent)

        self.Input = QtGui.QLineEdit()
        self.Input.returnPressed.connect(self.addItem)
        self.Add = QtGui.QPushButton()
        self.Add.setAutoDefault(False)
        self.Add.setIcon(QtGui.QIcon(":icons/add.ico"))
        self.Add.setFixedSize(20,20)
        self.Add.clicked.connect(self.addItem)
        AddLayout = QtGui.QHBoxLayout()
        AddLayout.addWidget(self.Input)
        AddLayout.addWidget(self.Add)

        ScrollArea = QtGui.QScrollArea()
        self.ItemLayout = QtGui.QVBoxLayout()
        self.ItemLayout.setContentsMargins(0,0,0,0)
        self.ItemLayout.setSpacing(0)
        self.ItemLayout.addStretch(1)
        ItemLayoutWidget = QtGui.QWidget()
        ItemLayoutWidget.setLayout(self.ItemLayout)
        ScrollArea.setWidget(ItemLayoutWidget)
        ScrollArea.setWidgetResizable(True)

        WidgetLayout = QtGui.QVBoxLayout()
        WidgetLayout.setContentsMargins(0,0,0,0)
        WidgetLayout.addLayout(AddLayout)
        WidgetLayout.addWidget(ScrollArea)

        self.setLayout(WidgetLayout)

    def addItem(self,Text=None):
        if not Text:
            Text = self.Input.text()
            self.Input.setText("")
        if Text:
            ListItem = ListWidgetItem(self,Text)
            self.ItemLayout.insertWidget(self.ItemLayout.count()-1,ListItem)
            ListItem.moveUp.connect(self.moveItemUp)
            ListItem.moveDown.connect(self.moveItemDown)

    def addItems(self, items):
        self.clear()
        for item in items:
            self.addItem(item)
        
    def getItems(self):
        return [self.ItemLayout.itemAt(x).widget().ItemText.text() for x in range(self.ItemLayout.count()-1)]

    def moveItemUp(self,ListItem):
        Index = self.ItemLayout.indexOf(ListItem)
        if Index>0:
            self.ItemLayout.insertWidget(Index-1,ListItem)

    def moveItemDown(self,ListItem):
        Index = self.ItemLayout.indexOf(ListItem)
        if Index<self.ItemLayout.count()-2:
            self.ItemLayout.insertWidget(Index+1,ListItem)

    def clear(self):
        for x in range(self.ItemLayout.count()-1):
            self.ItemLayout.itemAt(0).widget().setParent(None)
