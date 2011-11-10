#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 04.11.2011

from PyQt4 import QtGui, QtCore

from addeditdialog import AddEditDialog
from navigationwidget import Navigation
from bookwidget import Book
from sqlmodel import SqlModel
import icons

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowIcon(QtGui.QIcon(":icons/abibliophile.ico"))
        self.setWindowTitle(self.tr("aBibliophile (c) Avaris"))

        self.SqlModel = SqlModel()
        
        self.setupUi()

    def setupUi(self):
        NavigationFilterTypes = [(self.tr("Title"),1),
                                 (self.tr("Writer"),2),
                                 (self.tr("Publisher"),3),
                                 (self.tr("Category"),4)]
        NavigationGroupTypes = [(self.tr("Writer"),2),
                                (self.tr("Publisher"),3),
                                (self.tr("Category"),4),
                                (self.tr("Language"),7),
                                (self.tr("Read"),9)]

        self.Navigation = Navigation(self, NavigationFilterTypes, NavigationGroupTypes)
        self.Navigation.currentChanged.connect(self.updateBook)
        self.Navigation.setSourceModel(self.SqlModel)
        self.Book = Book(self)
        self.Book.setVisible(False)

        Splitter = QtGui.QSplitter()
        Splitter.addWidget(self.Navigation)
        Splitter.addWidget(self.Book)
        self.setCentralWidget(Splitter)
        self.createActions()

    def _createAction(self,text,slot=None,shortcut=None,icon=None,tip=None,checkable=False,signal="triggered()"):
        action=QtGui.QAction(text,self)
        if icon is not None:
            action.setIcon(QtGui.QIcon("%s.ico"%icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action,QtCore.SIGNAL(signal),slot)
        if checkable:
            action.setCheckable(True)
        return action

    def createActions(self):
        self.Actions = {}
        self.Actions["CreateDatabase"] = self._createAction(self.tr("Create new database..."),
                                                            self.createDatabase,
                                                            self.tr("Ctrl+N","Create new database"),
                                                            ":icons/database_new",
                                                            self.tr("Create a new database"))
        self.Actions["OpenDatabase"] = self._createAction(self.tr("Open database..."),
                                                          self.openDatabase,
                                                          self.tr("Ctrl+O","Open database"),
                                                          ":icons/database_open",
                                                          self.tr("Open existing database"))
        self.Actions["AddBook"] = self._createAction(self.tr("Add book..."),
                                                     self.addBook,
                                                     self.tr("Ctrl+A","Add book"),
                                                     ":icons/book_add",
                                                     self.tr("Add a book"))
        self.Actions["EditBook"] = self._createAction(self.tr("Edit book..."),
                                                      self.editBook,
                                                      self.tr("Ctrl+E","Edit book"),
                                                      ":icons/book_edit",
                                                      self.tr("Edit book"))
        self.Actions["DeleteBook"] = self._createAction(self.tr("Delete book..."),
                                                        self.deleteBook,
                                                        self.tr("Ctrl+D","Delete book"),
                                                        ":icons/book_delete",
                                                        self.tr("Delete selected book"))
        self.Actions["About"] = self._createAction(self.tr("About..."),
                                                   self.about,
                                                   self.tr("F1","About"),
                                                   ":icons/about",
                                                   self.tr("About aBibliophile"))
        self.Actions["Exit"] = self._createAction(self.tr("Exit"),
                                                  self.exit_,
                                                  self.tr("Esc","Exit"),
                                                  ":icons/delete",
                                                  self.tr("Exit aBibliophile"))
        
        self.updateActionStatus()
        self.createToolbar()
        self.createMenu()

    def createToolbar(self):
        Toolbar = QtGui.QToolBar()
        Toolbar.addAction(self.Actions["CreateDatabase"])
        Toolbar.addAction(self.Actions["OpenDatabase"])
        Toolbar.addSeparator()
        Toolbar.addAction(self.Actions["AddBook"])
        Toolbar.addAction(self.Actions["EditBook"])
        Toolbar.addAction(self.Actions["DeleteBook"])
        Toolbar.addSeparator()
        Toolbar.addAction(self.Actions["About"])
        Toolbar.addSeparator()
        Toolbar.addAction(self.Actions["Exit"])
        
        self.addToolBar(Toolbar)

    def createMenu(self):
        MenuBar = QtGui.QMenuBar()
        MenuFile = MenuBar.addMenu(self.tr("File"))
        MenuBook = MenuBar.addMenu(self.tr("Book"))
        
        MenuFile.addAction(self.Actions["CreateDatabase"])
        MenuFile.addAction(self.Actions["OpenDatabase"])
        MenuFile.addSeparator()
        MenuFile.addAction(self.Actions["About"])
        MenuFile.addSeparator()
        MenuFile.addAction(self.Actions["Exit"])
        
        MenuBook.addAction(self.Actions["AddBook"])
        MenuBook.addAction(self.Actions["EditBook"])
        MenuBook.addAction(self.Actions["DeleteBook"])
                
        self.setMenuBar(MenuBar)

    def updateActionStatus(self):
        self.Actions["AddBook"].setEnabled(self.SqlModel.Database.isOpen())

        CurrentIndex = self.Navigation.mapSelectionToSource(self.Navigation.Tree.currentIndex())
        self.Actions["EditBook"].setEnabled(CurrentIndex.isValid())
        self.Actions["DeleteBook"].setEnabled(CurrentIndex.isValid())
        self.Book.setVisible(CurrentIndex.isValid())

    def updateBook(self, index):
        if index.isValid():
            self.Book.setVisible(True)
            self.Book.fillData(self.SqlModel.record(index.row()))
        else:
            self.Book.setVisible(False)
        self.updateActionStatus()

    def createDatabase(self):
        database_name = QtGui.QFileDialog.getSaveFileName(self,
                                                          self.tr("Create new aBibliophile database..."),
                                                          ".",
                                                          self.tr("aBibliophile databases (*.adb)"))
        
        if database_name:
            self.SqlModel.createDatabase(database_name)
            self.updateActionStatus()
        else:
            pass # Cancel

    def openDatabase(self):
        database_name = QtGui.QFileDialog.getOpenFileName(self,
                                                          self.tr("Open existing aBibliophile database..."),
                                                          ".",
                                                          self.tr("aBibliophile databases (*.adb)"))

        if database_name:
            self.SqlModel.openDatabase(database_name)
            self.updateActionStatus()
        else:
            pass # Cancel

    def addBook(self):
        record = self.SqlModel.record()
        AddDialog = AddEditDialog(self, record)
        if AddDialog.exec_():
            self.SqlModel.insertRecord(-1, AddDialog.Record)

    def editBook(self):
        row = self.Navigation.mapSelectionToSource(self.Navigation.Tree.currentIndex()).row()
        record = self.SqlModel.record(row)
        EditDialog = AddEditDialog(self, record)
        if EditDialog.exec_():
            self.SqlModel.setRecord(row, EditDialog.Record)
            self.SqlModel.submitAll()

    def deleteBook(self):
        index = self.Navigation.mapSelectionToSource(self.Navigation.Tree.currentIndex())
        row = index.row()
        parent = index.parent()
        record = self.SqlModel.record(row)

        m = QtGui.QMessageBox(QtGui.QMessageBox.Critical,
                              self.tr("Confirm delete book..."),
                              self.tr("You are about to delete book:\n%s\n\nAre you sure?") % record.value("title"),
                              QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                              self)
        m.setWindowIcon(QtGui.QIcon(":icons/book_delete.ico"))
        if m.exec_() == QtGui.QMessageBox.Ok:
            if record.value("cover_path"):
                QtCore.QFile.remove(record.value("cover_path"))
            self.SqlModel.removeRow(row, parent)
            self.SqlModel.submitAll()

    def about(self):
        m = QtGui.QMessageBox(QtGui.QMessageBox.Information,
                              self.tr("About aBibliophile"),
                              self.tr("""aBibliophile
Avaris (c) 2011
version: 0.2b

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""),
                              QtGui.QMessageBox.Ok,
                              self)
        m.setWindowIcon(QtGui.QIcon(":icons/abibliophile.ico"))
        m.exec_()

    def exit_(self):
        self.close()
