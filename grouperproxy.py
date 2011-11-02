from collections import namedtuple
import random

from PyQt4 import QtCore, QtGui

groupItem = namedtuple("groupItem",["name","children","index"])
rowItem = namedtuple("rowItem",["groupIndex","random"])


class GrouperProxy(QtGui.QAbstractProxyModel):
    def __init__(self, parent=None):
        super(GrouperProxy, self).__init__(parent)

        self._rootItem = QtCore.QModelIndex()
        self._groups = []       # list of groupItems
        self._groupMap = {}     # map of group names to group indexes
        self._groupIndexes = [] # list of groupIndexes for locating group row
        self._sourceRows = []   # map of source rows to group index
        self._groupColumn = 0   # grouping column.

    def setSourceModel(self, source, groupColumn=0):
        super(GrouperProxy, self).setSourceModel(source)

        # connect signals
        self.sourceModel().rowsInserted.connect(self._rowsInserted)
        self.sourceModel().rowsRemoved.connect(self._rowsRemoved)
        self.sourceModel().dataChanged.connect(self._dataChanged)

        # set grouping
        self.groupBy(groupColumn)

    def rowCount(self, parent):
        if parent == self._rootItem:
            # root level
            return len(self._groups)
        elif parent.internalPointer() == self._rootItem:
            # children level
            return len(self._groups[parent.row()].children)
        else:
            return 0

    def columnCount(self, parent):
        if self.sourceModel():
            return self.sourceModel().columnCount(QtCore.QModelIndex())
        else:
            return 0
        
    def index(self, row, column, parent):
        if parent == self._rootItem:
            # this is a group
            return self.createIndex(row,column,self._rootItem)
        elif parent.internalPointer() == self._rootItem:
            return self.createIndex(row,column,self._groups[parent.row()].index)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        parent =  index.internalPointer()
        if parent == self._rootItem:
            return self._rootItem
        else:
            parentRow = self._getGroupRow(parent)
            return self.createIndex(parentRow,0,self._rootItem)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            parent = index.internalPointer()
            if parent == self._rootItem:
                return self._groups[index.row()].name
            else:
                parentRow = self._getGroupRow(parent)
                sourceRow = self._sourceRows.index(self._groups[parentRow].children[index.row()])
                sourceIndex = self.createIndex(sourceRow, index.column(), 0)
                return self.sourceModel().data(sourceIndex, role)
        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        return self.sourceModel().headerData(section, orientation, role)

    def mapToSource(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        
        parent = index.internalPointer()
        if parent == self._rootItem:
            return QtCore.QModelIndex()
        else:
            rowItem_ = self._groups[parent.row()].children[index.row()]
            sourceRow = self._sourceRows.index(rowItem_)
            return self.sourceModel().createIndex(sourceRow, index.column(), QtCore.QModelIndex())

    def mapFromSource(self, index):
        rowItem_ = self._sourceRows[index.row()]
        groupRow = self._getGroupRow(rowItem_.groupIndex)
        itemRow = self._groups[groupRow].children.index(rowItem_)
        return self.index(itemRow,index.column(),self._groupIndexes[groupRow])

    def _clearGroups(self):
        self._groupMap = {}
        self._groups = []
        self._sourceRows = []
        self._groupIndexes = []

    def groupBy(self,column=0):
        self.beginResetModel()
        self._clearGroups()
        self._groupColumn = column
        sourceModel = self.sourceModel()
        for row in range(sourceModel.rowCount(QtCore.QModelIndex())):
            groupName = sourceModel.data(self.createIndex(row,column,0),
                                         QtCore.Qt.DisplayRole)

            groupIndex = self._getGroupIndex(groupName)
            groupRow = self._getGroupRow(groupIndex)
            rowItem_ = rowItem(groupIndex,random.random())
            self._groups[groupRow].children.append(rowItem_)
            self._sourceRows.append(rowItem_)
        self.endResetModel()

    def _getGroupIndex(self, groupName):
        """ return the index for a group denoted with name.
        if there is no group with given name, create and then return"""
        if groupName in self._groupMap:
            return self._groupMap[groupName]
        else:
            groupRow = len(self._groupMap)
            groupIndex = self.createIndex(groupRow,0,self._rootItem)
            self.layoutAboutToBeChanged.emit()
            self._groupMap[groupName] = groupIndex
            self._groups.append(groupItem(groupName,[],groupIndex))
            self._groupIndexes.append(groupIndex)
            self.layoutChanged.emit()
            return groupIndex

    def _getGroupRow(self, groupIndex):
        for i,x in enumerate(self._groupIndexes):
            if id(groupIndex)==id(x):
                return i
        return 0

    def _rowsInserted(self, parent, start, end):
        self.layoutAboutToBeChanged.emit()
        for row in range(start, end+1):
            groupName = self.sourceModel().data(self.createIndex(row,self._groupColumn,0),
                                                QtCore.Qt.DisplayRole)
            groupIndex = self._getGroupIndex(groupName)
            groupItem_ = self._groups[self._getGroupRow(groupIndex)]
            #print self._groupColumn,groupName, groupItem_
            #self.beginInsertRows(groupIndex,len(groupItem_.children),len(groupItem_.children))
            rowItem_ = rowItem(groupIndex,random.random())
            groupItem_.children.append(rowItem_)
            self._sourceRows.insert(row, rowItem_)
            #self.endInsertRows()
        self.layoutChanged.emit()

    def _rowsRemoved(self, parent, start, end):
        self.layoutAboutToBeChanged.emit()
        for row in range(start, end+1):
            rowItem_ = self._sourceRows[start]
            groupIndex = rowItem_.groupIndex
            groupItem_ = self._groups[self._getGroupRow(groupIndex)]
            childrenRow = groupItem_.children.index(rowItem_)
            groupItem_.children.pop(childrenRow)
            self._sourceRows.pop(start)
            if not len(groupItem_.children):
                # remove the group
                groupRow = self._getGroupRow(groupIndex)
                groupName = self._groups[groupRow].name
                self._groups.pop(groupRow)
                self._groupIndexes.pop(groupRow)
                del self._groupMap[groupName]
        self.layoutChanged.emit()
            
    def _dataChanged(self, topLeft, bottomRight):
        self.layoutAboutToBeChanged.emit()
        topRow = topLeft.row()
        bottomRow = bottomRight.row()
        sourceModel = self.sourceModel()
        # loop through all the changed data
        for row in range(topRow,bottomRow+1):
            oldGroupIndex = self._sourceRows[row].groupIndex
            oldGroupItem = self._groups[self._getGroupRow(oldGroupIndex)]
            newGroupName = sourceModel.data(self.createIndex(row,self._groupColumn,0),QtCore.Qt.DisplayRole)
            if newGroupName != oldGroupItem.name:
                # move to new group...
                newGroupIndex = self._getGroupIndex(newGroupName)
                newGroupItem = self._groups[self._getGroupRow(newGroupIndex)]
                
                rowItem_ = self._sourceRows[row]
                newGroupItem.children.append(rowItem_)

                # delete from old group
                oldGroupItem.children.remove(rowItem_)
                if not len(oldGroupItem.children):
                    # remove the group
                    groupRow = self._getGroupRow(oldGroupItem.index)
                    groupName = oldGroupItem.name
                    self._groups.pop(groupRow)
                    self._groupIndexes.pop(groupRow)
                    del self._groupMap[groupName]

        self.layoutChanged.emit()
