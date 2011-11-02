# -.- coding: utf-8 -.-
from PyQt4 import QtGui, QtCore

class MyListWidgetItem(QtGui.QWidget):
    MoveUp = QtCore.pyqtSignal(QtGui.QWidget)
    MoveDown = QtCore.pyqtSignal(QtGui.QWidget)
    
    def __init__(self,Parent,ItemText):
        QtGui.QWidget.__init__(self,Parent)
        
        self.ItemText = QtGui.QLabel(ItemText)
        self.ItemText.setStyleSheet("font-weight: bold;")
        
        self.ItemRemove = QtGui.QPushButton()
        self.ItemRemove.setAutoDefault(False)
        self.ItemRemove.setIcon(QtGui.QIcon(":icons/delete.ico"))
        self.ItemRemove.setFixedSize(20,20)
        self.ItemRemove.clicked.connect(self.RemoveMe)

        self.ItemMoveUp = QtGui.QPushButton()
        self.ItemMoveUp.setAutoDefault(False)
        self.ItemMoveUp.setIcon(QtGui.QIcon(":icons/up.ico"))
        self.ItemMoveUp.setFixedSize(20,20)
        self.ItemMoveUp.clicked.connect(self.MoveMeUp)

        self.ItemMoveDown = QtGui.QPushButton()
        self.ItemMoveDown.setAutoDefault(False)
        self.ItemMoveDown.setIcon(QtGui.QIcon(":icons/down.ico"))
        self.ItemMoveDown.setFixedSize(20,20)
        self.ItemMoveDown.clicked.connect(self.MoveMeDown)

        WidgetLayout = QtGui.QHBoxLayout()
        WidgetLayout.setContentsMargins(3,3,3,3)
        WidgetLayout.addWidget(self.ItemText)
        WidgetLayout.addWidget(self.ItemMoveUp)
        WidgetLayout.addWidget(self.ItemMoveDown)
        WidgetLayout.addWidget(self.ItemRemove)

        self.setLayout(WidgetLayout)

    def RemoveMe(self):
        self.setParent(None)

    def MoveMeUp(self):
        self.MoveUp.emit(self)

    def MoveMeDown(self):
        self.MoveDown.emit(self)

class MyListWidget(QtGui.QWidget):
    def __init__(self,Parent=None):
        QtGui.QWidget.__init__(self,Parent)

        self.Input = QtGui.QLineEdit()
        self.Input.returnPressed.connect(self.AddItem)
        self.Add = QtGui.QPushButton()
        self.Add.setAutoDefault(False)
        self.Add.setIcon(QtGui.QIcon(":icons/add.ico"))
        self.Add.setFixedSize(20,20)
        self.Add.clicked.connect(self.AddItem)
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

    def AddItem(self,Text=None):
        if Text is None:
            Text = self.Input.text()
            self.Input.setText("")
        if Text:
            ListItem = MyListWidgetItem(self,Text)
            self.ItemLayout.insertWidget(self.ItemLayout.count()-1,ListItem)
            ListItem.MoveUp.connect(self.MoveItemUp)
            ListItem.MoveDown.connect(self.MoveItemDown)
        
    def GetItems(self):
        return [unicode(self.ItemLayout.itemAt(x).widget().ItemText.text()) for x in range(self.ItemLayout.count()-1)]

    def MoveItemUp(self,ListItem):
        Index = self.ItemLayout.indexOf(ListItem)
        if Index>0:
            self.ItemLayout.insertWidget(Index-1,ListItem)

    def MoveItemDown(self,ListItem):
        Index = self.ItemLayout.indexOf(ListItem)
        if Index<self.ItemLayout.count()-2:
            self.ItemLayout.insertWidget(Index+1,ListItem)

    def Clear(self):
        for x in range(self.ItemLayout.count()-1):
            self.ItemLayout.itemAt(0).widget().setParent(None)
