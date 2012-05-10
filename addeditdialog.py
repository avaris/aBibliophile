#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 05.11.2011

from uuid import uuid1 as uuid

from PyQt4 import QtGui, QtCore

from addeditsearchwidget import Search
from addeditbookwidget import Book
import icons

class AddEditDialog(QtGui.QDialog):
    def __init__(self, parent=None, record=None):
        super(AddEditDialog, self).__init__(parent)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setupUi()
        self.Record = record
        if self.Record.isNull("id"):
            self.setWindowTitle(self.tr("Add book..."))
            self.setWindowIcon(QtGui.QIcon(":icons/book_add.ico"))
        else:
            self.setWindowTitle(self.tr("Edit book..."))
            self.setWindowIcon(QtGui.QIcon(":icons/book_edit.ico"))
            self.recordToBook()

    def setupUi(self):
        self.Search = Search()
        self.Book = Book()
        self.Search.bookInfoDownloaded.connect(self.Book.fromDict)

        Splitter = QtGui.QSplitter()
        Splitter.addWidget(self.Search)
        Splitter.addWidget(self.Book)

        self.Ok = QtGui.QPushButton(self.tr("Ok"))
        self.Ok.setIcon(QtGui.QIcon(":icons/ok.ico"))
        self.Ok.setAutoDefault(False)
        self.Ok.clicked.connect(self.okClicked)
        self.Cancel = QtGui.QPushButton(self.tr("Cancel"))
        self.Cancel.setIcon(QtGui.QIcon(":icons/delete.ico"))
        self.Cancel.setAutoDefault(False)
        self.Cancel.clicked.connect(self.reject)

        ButtonGroup = QtGui.QHBoxLayout()
        ButtonGroup.addStretch()
        ButtonGroup.addWidget(self.Cancel)
        ButtonGroup.addWidget(self.Ok)

        Layout = QtGui.QVBoxLayout()
        Layout.addWidget(Splitter)
        Layout.addLayout(ButtonGroup)

        self.setLayout(Layout)

    def recordToBook(self):
        self.Book.fromDict({"title" : self.Record.value("title"),
                            "writers" : self.Record.value("writers").split("|"),
                            "publisher" : self.Record.value("publisher"),
                            "categories" : self.Record.value("categories").split("|"),
                            "serie_name" : self.Record.value("serie_name"),
                            "serie_no" : self.Record.value("serie_no"),
                            "language" : self.Record.value("language"),
                            "pages" : self.Record.value("pages"),
                            "is_read" : self.Record.value("is_read"),
                            "excerpt" : self.Record.value("excerpt"),
                            "cover_path" : self.Record.value("cover_path")})

    def bookToRecord(self):
        book_dict = self.Book.toDict()
        self.Record.setValue("title",book_dict["title"])
        self.Record.setValue("writers","|".join(book_dict["writers"]))
        self.Record.setValue("publisher",book_dict["publisher"])
        self.Record.setValue("categories","|".join(book_dict["categories"]))
        self.Record.setValue("serie_name",book_dict["serie_name"])
        self.Record.setValue("serie_no",book_dict["serie_no"])
        self.Record.setValue("language",book_dict["language"])
        self.Record.setValue("pages",book_dict["pages"])
        self.Record.setValue("is_read",book_dict["is_read"])
        self.Record.setValue("excerpt",book_dict["excerpt"])

        cover_path = self.Record.value("cover_path") if not self.Record.isNull("cover_path") else ''
        if book_dict["cover"].isEmpty():
            if cover_path:
                QtCore.QFile.remove(cover_path)
            self.Record.setValue("cover_path","")
        else:
            if not cover_path:
                cover_path = "covers/%s.jpg" % uuid()
            cover_file = QtCore.QFile(cover_path)
            cover_file.open(cover_file.WriteOnly)
            cover_file.write(book_dict["cover"])
            cover_file.close()
            self.Record.setValue("cover_path",cover_path)
        if not self.Record.value("date_added"):
            self.Record.setValue("date_added",QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate))
            
    def okClicked(self):
        self.bookToRecord()
        self.accept()
