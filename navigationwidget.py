#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 02.11.2011

from PyQt4 import QtGui, QtCore

from sortfilterproxy import SortFilterProxy
from grouperproxy import GrouperProxy

class Navigation(QtGui.QWidget):
    currentChanged = QtCore.pyqtSignal(QtCore.QModelIndex)
    
    def __init__(self, parent=None, filter_types=None, group_types=None):
        super(Navigation, self).__init__(parent)
        
        self.SortFilterProxy = SortFilterProxy(self)
        self.GrouperProxy = GrouperProxy(self)

        self.SortFilterProxy.layoutChanged.connect(self.hideColumns)

        self.setupUi(filter_types, group_types)

    def setupUi(self, filter_types, group_types):
        self.FilterType = QtGui.QComboBox()
        self.FilterQuery = QtGui.QLineEdit()
        FilterBox = QtGui.QGroupBox(self.tr("Filter"))
        FilterLayout = QtGui.QHBoxLayout()
        FilterLayout.addWidget(self.FilterType)
        FilterLayout.addWidget(self.FilterQuery)
        FilterBox.setLayout(FilterLayout)

        for filter_type in filter_types:
            self.FilterType.addItem(*filter_type)
        self.SortFilterProxy.setFilterKeyColumn(self.FilterType.itemData(0))

        self.FilterType.currentIndexChanged.connect(self.setFilterColumn)
        self.FilterQuery.textChanged.connect(self.SortFilterProxy.setFilterRegExp)

        self.GroupType = QtGui.QComboBox()
        self.GroupBox = QtGui.QGroupBox(self.tr("Group"))
        self.GroupBox.setCheckable(True)
        self.GroupBox.setChecked(False)
        self.GroupBox.setEnabled(False)
        GroupLayout = QtGui.QHBoxLayout()
        GroupLayout.addWidget(self.GroupType)
        self.GroupBox.setLayout(GroupLayout)

        for group_type in group_types:
            self.GroupType.addItem(*group_type)

        self.GroupBox.toggled.connect(self.setGrouping)
        self.GroupType.currentIndexChanged.connect(self.setGroupColumn)

        self.Tree = QtGui.QTreeView()
        self.Tree.setHeaderHidden(True)

        MainLayout = QtGui.QGridLayout()
        MainLayout.addWidget(FilterBox,0,0)
        MainLayout.addWidget(self.GroupBox,0,1)
        MainLayout.addWidget(self.Tree,1,0,1,2)

        self.setLayout(MainLayout)

    def setSourceModel(self, model):
        self.SourceModel = model
        self.SourceModel.modelReset.connect(self.modelReset)
        self.SortFilterProxy.setSourceModel(model)
        self.GrouperProxy.setSourceModel(model,2)
        self.Tree.setModel(self.SortFilterProxy)
        self.Tree.selectionModel().currentChanged.connect(self.currentChanged_)
        self.GroupBox.setEnabled(True)
        self.hideColumns()

    def modelReset(self):
        self.setGroupColumn(self.GroupType.currentIndex())

    def setFilterColumn(self, index):
        self.SortFilterProxy.setFilterKeyColumn(self.FilterType.itemData(index))

    def setGrouping(self, on):
        self.Tree.setCurrentIndex(QtCore.QModelIndex())
        if on:
            self.SortFilterProxy.setSourceModel(self.GrouperProxy)
        else:
            self.SortFilterProxy.setSourceModel(self.SourceModel)

    def setGroupColumn(self, index):
        self.Tree.setCurrentIndex(QtCore.QModelIndex())
        self.GrouperProxy.groupBy(self.GroupType.itemData(index))
    
    def hideColumns(self):
        for i in range(1,self.SortFilterProxy.columnCount()):
            self.Tree.hideColumn(i)

    def currentChanged_(self, CurrentIndex, PreviousIndex):
        self.currentChanged.emit(self.mapSelectionToSource(CurrentIndex))

    def mapSelectionToSource(self, CurrentIndex):
        ProxyModel = CurrentIndex.model()
        while isinstance(ProxyModel,QtGui.QAbstractProxyModel):
            CurrentIndex = ProxyModel.mapToSource(CurrentIndex)
            ProxyModel = CurrentIndex.model()
        return CurrentIndex
