#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 05.11.2011

from PyQt4 import QtGui, QtCore

from searchmodel import SearchModel
import idefix
import icons

class SearchThread(QtCore.QThread):
    searchCompleted = QtCore.pyqtSignal(list)
    progressUpdated = QtCore.pyqtSignal(int,int,int)
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self,parent)

    def setup(self,SearchType,SearchData):
        self.SearchParameters = {SearchType: SearchData,
                                 "hook" : self.progress}

    def run(self):
        Results = idefix.SearchBook(**self.SearchParameters)
        self.searchCompleted.emit(Results)

    def progress(self,minimum,maximum,value):
        self.progressUpdated.emit(minimum,maximum,value)


class DownloadThread(QtCore.QThread):
    downloadCompleted = QtCore.pyqtSignal(dict)
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def setup(self, url):
        self.url = url

    def run(self):
        result = idefix.GetBookDetails(self.url)
        self.downloadCompleted.emit(result)


class Search(QtGui.QWidget):
    bookInfoDownloaded = QtCore.pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super(Search, self).__init__(parent)

        self.Model = SearchModel()
        self.Searcher = SearchThread(self)
        self.Downloader = DownloadThread(self)

        self.setupUi()

    def setupUi(self):
        self.Type = QtGui.QComboBox()
        self.Type.addItem(self.tr(u"Keyword"),"keyword")
        self.Type.addItem(self.tr(u"Title"),"title")
        self.Type.addItem(self.tr(u"Writer"),"writer")

        self.Query = QtGui.QLineEdit()
        self.Query.setPlaceholderText(self.tr(u"search idefix..."))
        self.Query.textChanged.connect(self.setButtonStatus)
        self.Query.returnPressed.connect(self.searchBook)

        self.Button = QtGui.QPushButton()
        self.Button.setFixedSize(25,25)
        self.Button.setAutoDefault(False)
        self.Button.setIcon(QtGui.QIcon(":icons/search.ico"))
        self.Button.setEnabled(False)
        self.Button.clicked.connect(self.searchBook)
        
        self.List = QtGui.QListView()
        self.List.setModel(self.Model)
        self.List.doubleClicked.connect(self.downloadBookInfo)

        self.Progress = QtGui.QProgressBar()
        self.Progress.setTextVisible(False)

        self.Status = QtGui.QLabel()

        Layout = QtGui.QGridLayout()
        Layout.addWidget(self.Type,0,0)
        Layout.addWidget(self.Query,0,1)
        Layout.addWidget(self.Button,0,2)
        Layout.addWidget(self.List,1,0,1,3)
        Layout.addWidget(self.Progress,2,0,1,3)
        Layout.addWidget(self.Status,3,0,1,3)

        self.setLayout(Layout)

    def searchBook(self):
        if self.Button.isEnabled():
            self.Button.setDisabled(True)
            self.Status.setText(self.tr("Searching..."))
            self.Searcher.setup(self.Type.itemData(self.Type.currentIndex()),
                                self.Query.text())
            self.Searcher.progressUpdated.connect(self.setProgressBar)
            self.Searcher.searchCompleted.connect(self.addSearchedBooks)
            self.Searcher.start()

    def setButtonStatus(self, Text=""):
        self.Button.setEnabled(bool(Text))

    def setProgressBar(self, minimum, maximum, value):
        self.Progress.setMinimum(minimum)
        self.Progress.setMaximum(maximum)
        self.Progress.setValue(value)

    def addSearchedBooks(self, bookList):
        self.Searcher.wait()
        self.Model.clear()
        self.Status.setText(self.tr("%d books found.") % len(bookList))
        self.Model.addDataFromList(bookList)
        self.Button.setDisabled(False)

    def downloadBookInfo(self, index):
        if not self.Downloader.isRunning():
            url = self.Model.data(index, QtCore.Qt.UserRole)
            self.Downloader.setup(url)
            self.Downloader.downloadCompleted.connect(self.bookInfoDownloaded.emit)
            self.Downloader.start()
