#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 08.11.2011

from PyQt4 import QtGui, QtCore

from coverwidget import Cover
from listwidget import ListWidget

class Book(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Book, self).__init__(parent)

        self.setupUi()

    def setupUi(self):
        self.Title = QtGui.QLineEdit()
        self.Writers = ListWidget()
        self.Writers.setFixedHeight(120)
        self.Publisher = QtGui.QLineEdit()
        self.Categories = ListWidget()
        self.Categories.setFixedHeight(120)
        self.SerieName = QtGui.QLineEdit()
        self.SerieNo = QtGui.QLineEdit()
        self.Language = QtGui.QLineEdit()
        self.Pages = QtGui.QLineEdit()
        self.IsRead = QtGui.QCheckBox(self.tr("Read"))
        self.Excerpt = QtGui.QTextEdit()
        self.Cover = Cover()

        SerieLayout = QtGui.QHBoxLayout()
        SerieLayout.addWidget(self.SerieName)
        SerieLayout.addWidget(self.SerieNo)
        SerieLayout.setStretch(0,5)
        SerieLayout.setStretch(1,1)
        SerieLayout.setSpacing(20)
        self.SerieName.setPlaceholderText(self.tr("Name"))
        self.SerieNo.setPlaceholderText(self.tr("No"))

        OtherLayout = QtGui.QHBoxLayout()
        OtherLayout.addWidget(self.Language)
        OtherLayout.addWidget(self.Pages)
        OtherLayout.setStretch(0,5)
        OtherLayout.setStretch(1,1)
        OtherLayout.setSpacing(20)
        self.Language.setPlaceholderText(self.tr("Language"))
        self.Pages.setPlaceholderText(self.tr("Pages"))
        
        FormLayout = QtGui.QFormLayout()
        FormLayout.setRowWrapPolicy(FormLayout.WrapLongRows)
        FormLayout.setSpacing(10)
        FormLayout.addRow(self.tr("Title"), self.Title)
        FormLayout.addRow(self.tr("Writers"), self.Writers)
        FormLayout.addRow(self.tr("Publisher"), self.Publisher)
        FormLayout.addRow(self.tr("Categories"), self.Categories)
        FormLayout.addRow(self.tr("Serie"), SerieLayout)
        FormLayout.addRow(self.tr("Other"), OtherLayout)

        Tab = QtGui.QTabWidget()
        Tab.addTab(self.Excerpt,self.tr("Excerpt"))

        Layout = QtGui.QGridLayout()
        Layout.addLayout(FormLayout,0,0,2,1)
        Layout.addWidget(self.Cover,0,1)
        Layout.addWidget(self.IsRead,1,1,QtCore.Qt.AlignHCenter)
        Layout.addWidget(Tab,2,0,1,2)
        Layout.setSpacing(30)

        self.setLayout(Layout)

    def fromDict(self, book):
        self.Title.setText(book.get("title",""))
        self.Writers.addItems(book.get("writers",[]))
        self.Publisher.setText(book.get("publisher",""))
        self.Categories.addItems(book.get("categories",[]))
        self.SerieName.setText(book.get("serie_name",""))
        self.SerieNo.setText(book.get("serie_no",""))
        self.Language.setText(book.get("language",""))
        self.Pages.setText(book.get("pages",""))
        self.IsRead.setChecked(book.get("is_read",False))
        self.Excerpt.setText(book.get("excerpt",""))
        if book.get("cover_path",""):
            self.Cover.fromFile(book["cover_path"])
        elif book.get("cover_url",""):
            self.Cover.fromUrl(book["cover_url"])
        else:
            self.Cover._remove()

    def toDict(self):
        return {"title": self.Title.text(),
                "writers": self.Writers.getItems(),
                "publisher": self.Publisher.text(),
                "categories": self.Categories.getItems(),
                "serie_name": self.SerieName.text(),
                "serie_no": self.SerieNo.text(),
                "language": self.Language.text(),
                "pages": self.Pages.text(),
                "is_read": int(self.IsRead.isChecked()),
                "excerpt": self.Excerpt.toPlainText(),
                "cover": self.Cover.toByteArray()}
