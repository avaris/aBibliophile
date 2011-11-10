#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 03.11.2011

from PyQt4 import QtCore, QtSql

class SqlModel(QtSql.QSqlTableModel):
    def __init__(self, parent=None):
        self.Database = QtSql.QSqlDatabase("QSQLITE")
        super(SqlModel, self).__init__(parent, self.Database)
        
    def data(self, index, role):
        if role==QtCore.Qt.DisplayRole and index.column()==9:
            # Replace is_read column to string from 0/1
            return self.tr("Read") if super(SqlModel,self).data(index,role)=="1" else self.tr("Not read")
        return super(SqlModel,self).data(index,role)

    def openDatabase(self, database_name):
        self.Database.close()
        self.Database.setDatabaseName(database_name)
        self.Database.open()

        if self.Database.isOpen():
            self.setTable("books")
            self.select()

    def createDatabase(self, database_name):
        self.clear()
        self.Database.close()
        QtCore.QFile.remove(database_name)
        self.Database.setDatabaseName(database_name)
        self.Database.open()
        if self.Database.isOpen():
            self.Database.exec_("""CREATE TABLE books (
                                id INTEGER PRIMARY KEY,
                                title TEXT,
                                writers TEXT,
                                publisher TEXT,
                                categories TEXT,
                                serie_name TEXT,
                                serie_no TEXT,
                                language TEXT,
                                pages TEXT,
                                is_read INTEGER,
                                excerpt TEXT,
                                cover_path TEXT,
                                date_added INTEGER)""")
            self.openDatabase(database_name)
