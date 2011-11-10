#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 05.11.2011

from PyQt4 import QtGui, QtCore

class SearchModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(SearchModel, self).__init__(parent)
        self.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setSortLocaleAware(True)
        self.setDynamicSortFilter(True)
        self.setSourceModel(SearchBaseModel())
        self.sort(0)

    def clear(self):
        self.sourceModel().clear()

    def addDataFromList(self, bookList):
        self.sourceModel().addDataFromList(bookList)

class SearchBaseModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(SearchBaseModel, self).__init__(parent)
        self._data = []

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return 1

    def index(self, row, column, parent):
        return self.createIndex(row, column, QtCore.QModelIndex())

    def parent(self, index):
        return QtCore.QModelIndex()

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self._data[index.row()]["title"]
        elif role == QtCore.Qt.ToolTipRole:
            writer = ", ".join(self._data[index.row()]["writers"])
            publisher = self._data[index.row()]["publisher"]
            return self.tr("Writer: %s\nPublisher: %s") % (writer, publisher)
        elif role == QtCore.Qt.UserRole:
            return self._data[index.row()]["url"]
        

    def addData(self, data):
        self._data.append(data)

    def addDataFromList(self, dataList):
        self.layoutAboutToBeChanged.emit()
        for data in dataList:
            self.addData(data)
        self.layoutChanged.emit()

    def clear(self):
        self._data=[]
