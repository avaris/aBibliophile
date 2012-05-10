#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 09.02.2012

from collections import namedtuple
from PyQt4 import QtGui, QtCore

# each group item has a 'name' and a list of 'children' consisting
# of each child's QPersistentModelIndex (pmi)
groupItem = namedtuple('groupItem',['name', 'children'])

# each row item has 'pmi' and a list of groups it is assigned
rowItem = namedtuple('rowItem',['pmi', 'groups'])

class GrouperProxy(QtGui.QAbstractProxyModel):
    def __init__(self, parent = None):
        super(GrouperProxy, self).__init__(parent)
        self._root = QtCore.QModelIndex()
        self.clear()

    def clear(self):
        self._groups = []   # stores the groups and their children
        self._rows = []     # stores the rows from original model and their groups

    def setSourceModel(self, model, displayColumn=None, groupColumn=0, groupSeparator=None):
        '''
        sets the source model.

        arguments:
         - model: source model
         - displayColumn: column to be displayed. use 'None' to show all. (default = None)
         - groupColumn: column to be used for grouping. (default = 0)
         - groupSeparator: string used for separating groups from groupColumn.
                           use 'None' for no separation. (default = None)
        '''
        super(GrouperProxy, self).setSourceModel(model)
        self.connectSignals()
        self.setDisplayColumn(displayColumn)
        self.setGroupColumn(groupColumn, groupSeparator)

    def setGroupColumn(self, column, separator=None):
        self._groupColumn = column
        self._groupSeparator = separator
        self._group()

    def setDisplayColumn(self, column):
        self.beginResetModel()
        self._displayColumn = column
        self.endResetModel()
            
    def connectSignals(self):
        sourceModel = self.sourceModel()
        #sourceModel.columnsAboutToBeInserted.connect(self.beginInsertColumns)
        #sourceModel.columnsAboutToBeMoved.connect(self.beginMoveColumns)
        #sourceModel.columnsAboutToBeRemoved.connect(self.beginRemoveColumns)
        #sourceModel.columnsInserted.connect(self.endInsertColumns)
        #sourceModel.columnsMoved.connect(self.endMoveColumns)
        #sourceModel.columnsRemoved.connect(self.endRemoveColumns)

        sourceModel.dataChanged.connect(self._dataChanged)
        #sourceModel.headerDataChanged.connect(self.headerDataChanged.emit)
        #sourceModel.layoutAboutToBeChanged.connect(self.layoutAboutToBeChanged.emit)
        sourceModel.layoutChanged.connect(self._group)
        #sourceModel.modelAboutToBeReset.connect(self.beginResetModel)
        sourceModel.modelReset.connect(self._group)        

        #sourceModel.rowsAboutToBeInserted.connect(self.beginInsertRows)
        #sourceModel.rowsAboutToBeMoved.connect(self.beginMoveRows)
        #sourceModel.rowsAboutToBeRemoved.connect(self.beginRemoveRows)
        sourceModel.rowsInserted.connect(self._rowsInserted)
        sourceModel.rowsMoved.connect(self.endMoveRows)
        sourceModel.rowsRemoved.connect(self._rowsRemoved)

    def mapToSource(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        
        parent = index.internalPointer()
        if parent == self._root:
            return QtCore.QModelIndex()
        else:
            groupIndex, group = self._getGroup(parent)
            pmi = group.children[index.row()]
            if self._displayColumn is None:
                column = index.column()
            else:
                column = self._displayColumn
            return self.sourceModel().index(pmi.row(), column)

    def mapFromSource(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        pmi = QtCore.QPersistentModelIndex(self.sourceModel().index(index.row(), self._groupColumn))
        rowIndex, row = self._getRow(pmi)

        if row.groups:
            groupIndex, group = self._getGroup(row.groups[0])
            rowIndex = group.children.index(row.pmi)
            column = 0 if self._displayColumn is not None else index.column()
            return self.index(rowIndex, column, self.index(groupIndex, 0, self._root))
        else:
            return QtCore.QModelIndex()


    def rowCount(self, parent):
        if parent == self._root:
            return len(self._groups)
        elif parent.internalPointer() == self._root:
            return len(self._groups[parent.row()].children)
        else:
            return 0

    def columnCount(self, parent):
        if self._displayColumn is not None:
            return 1
        else:
            return self.sourceModel().columnCount(QtCore.QModelIndex())

    def index(self, row, column, parent):
        if self.hasIndex(row, column, parent):
            if parent == self._root:
                return self.createIndex(row, column, self._root)
            else:
                return self.createIndex(row, column, self._groups[parent.row()].name)
        return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        parent = index.internalPointer()
        if parent == self._root:
            return self._root
        else:
            groupIndex, group = self._getGroup(parent)
            return self.index(groupIndex, 0, self._root)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            parent = index.internalPointer()
            if parent == self._root:
                return self._groups[index.row()].name
            else:
                column = index.column() if self._displayColumn is None else self._displayColumn
                groupIndex, group = self._getGroup(parent)
                itemPmi = group.children[index.row()]
                return self.sourceModel().index(itemPmi.row(), column).data()
                
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def _group(self):
        self.beginResetModel()
        self.clear()
        sourceModel = self.sourceModel()
        for i in range(sourceModel.rowCount(QtCore.QModelIndex())):
            index = sourceModel.index(i, self._groupColumn)
            pmi = QtCore.QPersistentModelIndex(index)
            rowIndex, row = self._getRow(pmi)
            
            groups = self._findGroups(i)
            for groupName in groups:
                groupIndex, group = self._getGroup(groupName, False)
                group.children.append(pmi)
                row.groups.append(groupName)
        self.endResetModel()

    def _getGroup(self, groupName, emitSignals=True):
        '''
        returns 'index, groupItem' with '.name == groupName'
        if no item is found, a new item is appended with 'name == groupName' and returned
        '''
        
        for index, group in enumerate(self._groups):
            if groupName == group.name:
                return index, group
        index = len(self._groups)
        if emitSignals: self.beginInsertRows(self._root, index, index)
        self._groups.append(groupItem(groupName, []))
        if emitSignals: self.endInsertRows()
        return index, self._groups[-1]

    def _getRow(self, pmi):
        '''
        returns 'index, rowItem' with '.pmi == pmi'
        if no item is found, a new item is appended with '.pmi == pmi' and returned
        '''
        for index, row in enumerate(self._rows):
            if pmi == row.pmi:
                return index, row
        index = len(self._rows)
        self._rows.append(rowItem(pmi, []))
        return index, self._rows[-1]

    def _findGroups(self, sourceRow):
        '''
        returns a list of groups for item in row in sourceModel.
        '''

        rowData = unicode(self.sourceModel().index(sourceRow, self._groupColumn).data())
        if self._groupSeparator is None:
            return [rowData]
        else:
            return rowData.split(self._groupSeparator)


    def _rowsRemoved(self, parent_, start, end):
        for row in self._rows[start:end+1]:
            for groupName in row.groups:
                groupIndex, group = self._getGroup(groupName)
                parent = self.index(groupIndex, 0, self._root)
                childIndex = group.children.index(row.pmi)
                
                self.beginRemoveRows(parent, childIndex, childIndex)
                group.children.pop(childIndex)
                self.endRemoveRows()

                if not len(group.children):
                    self.beginRemoveRows(self._root, groupIndex, groupIndex)
                    self._groups.pop(groupIndex)
                    self.endRemoveRows()
                    
        self._rows[start:end+1] = []

    def _rowsInserted(self, parent_, start, end):
        for i in range(start, end+1):
            pmi = QtCore.QPersistentModelIndex(self.sourceModel().index(i, self._groupColumn))
            groups = self._findGroups(i)
            for groupName in groups:
                groupIndex, group = self._getGroup(groupName)
                parent = self.createIndex(groupIndex, 0, self._root)
                self.beginInsertRows(parent, len(group.children), len(group.children))
                group.children.append(pmi)
                self.endInsertRows()
            self._rows.insert(i, rowItem(pmi, groups))


    def _dataChanged(self, topleft, bottomright):
        for i in range(topleft.row(), bottomright.row()+1):
            row = self._rows[i]
            if (self._displayColumn is None or 
                topleft.column() <= self._displayColumn <= bottomright.column()):
                
                for groupName in row.groups:
                    groupIndex, group = self._getGroup(groupName)
                    rowIndex = group.children.index(row.pmi)
                    parent = self.index(groupIndex, 0, self._root)

                    # emit dataChanged
                    self.dataChanged.emit(self.index(rowIndex, 0, parent),
                                          self.index(rowIndex, self.columnCount(parent)-1, parent))

            
            if topleft.column() <= self._groupColumn <= bottomright.column():
                oldGroupSet = set(row.groups)
                newGroupSet = set(self._findGroups(i))

                for groupName in oldGroupSet - newGroupSet:
                    # things to remove
                    
                    groupIndex, group = self._getGroup(groupName)
                    rowIndex = group.children.index(row.pmi)
                    parent = self.index(groupIndex, 0, self._root)

                    self.beginRemoveRows(parent, rowIndex, rowIndex)
                    group.children.pop(rowIndex)
                    self.endRemoveRows()

                    if not group.children:
                        # empty group
                        self.beginRemoveRows(self._root, groupIndex, groupIndex)
                        self._groups.pop(groupIndex)
                        self.endRemoveRows()

                    row.groups.remove(groupName)

                for groupName in newGroupSet - oldGroupSet:
                    # things to add

                    groupIndex, group = self._getGroup(groupName)
                    parent = self.index(groupIndex, 0, self._root)

                    self.beginInsertRows(parent, len(group.children), len(group.children))
                    group.children.append(row.pmi)
                    self.endInsertRows()

                    row.groups.append(groupName)
