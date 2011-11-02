from PyQt4 import QtGui, QtCore

class SortFilterProxy(QtGui.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(SortFilterProxy,self).__init__(parent)
        self.setSortLocaleAware(True)
        self.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setDynamicSortFilter(True)
        self.sort(1)
        self.setFilterKeyColumn(1)
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

    def data(self, index, role):
        if role==QtCore.Qt.DisplayRole:
            if index.column() == 0:
                sourceIndex = self.mapToSource(index)
                return self.sourceModel().data(self.createIndex(sourceIndex.row(),1,sourceIndex.internalPointer()),role)
            else:
                sourceIndex = self.mapToSource(index)
                return self.sourceModel().data(sourceIndex,role)

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def filterAcceptsRow(self, sourceRow, sourceParent):
        item = self.sourceModel().index(sourceRow,0,sourceParent)
        if not item.isValid():
            return False

        rows = self.sourceModel().rowCount(item)

        if rows:
            for i in range(rows):
                if super(SortFilterProxy,self).filterAcceptsRow(i, item):
                    return True
        else:
            return super(SortFilterProxy,self).filterAcceptsRow(sourceRow, sourceParent)
        return False
