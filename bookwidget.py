#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 03.11.2011

from PyQt4 import QtGui, QtCore

class Book(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Book, self).__init__(parent)

        self.setupUi()

    def setupUi(self):
        self.Title = QtGui.QLabel()
        self.Title.setWordWrap(True)
        self.Title.setAlignment(QtCore.Qt.AlignHCenter)
        self.Title.setStyleSheet("color: #fc3;"
                                 "background: #222;"
                                 "font: 14pt 'Tahoma';"
                                 "border: 2px solid #900;"
                                 "border-radius: 10px;"
                                 "padding: 5px;"
                                 "margin: 10px;")

        self.Writers = QtGui.QLabel()
        self.Writers.setStyleSheet("color: #33f;"
                                   "font: italic 12pt 'Verdana';")
        
        self.Publisher = QtGui.QLabel()
        self.Publisher.setStyleSheet("color: #531;"
                                     "font: bold 10pt 'Tahoma';")
        
        self.Categories = QtGui.QLabel()
        
        self.Series = QtGui.QLabel()
        self.Series.setStyleSheet("color: #919;"
                                  "font: italic 8pt 'Verdana';")
        self.Language = QtGui.QLabel()
        self.Language.setStyleSheet("font: italic 8pt 'Verdana';")
        self.Pages = QtGui.QLabel()
        self.Pages.setStyleSheet("font: italic 8pt 'Verdana';")
        self.IsRead = QtGui.QLabel()
        self.Cover = QtGui.QLabel()
        self.Cover.setFixedSize(200,300)
        self.Cover.setAlignment(QtCore.Qt.AlignHCenter)
        self.Cover.setStyleSheet("border: 1px solid")

        self.Excerpt = QtGui.QTextBrowser()
        self.OtherTab = QtGui.QTabWidget()
        self.OtherTab.addTab(self.Excerpt,self.tr("Excerpt"))

        Layout = QtGui.QGridLayout()
        Layout.addWidget(self.Title,0,0,1,4)
        Layout.addWidget(self.Writers,1,0,1,3)
        Layout.addWidget(self.Publisher,2,0,1,3)
        Layout.addWidget(self.Categories,3,0,1,3)
        Layout.addWidget(self.Series,4,0,1,3)
        Layout.addWidget(self.Language,5,0)
        Layout.addWidget(self.Pages,5,1)
        Layout.addWidget(self.IsRead,5,2)
        Layout.addWidget(self.Cover,1,3,5,1,QtCore.Qt.AlignTop|QtCore.Qt.AlignRight)
        Layout.addWidget(self.OtherTab,6,0,1,4)

        Layout.setVerticalSpacing(20)
        Layout.setRowStretch(6,1)

        self.setLayout(Layout)

    def fillData(self, SqlRecord):
        self.Title.setText(SqlRecord.value("title"))
        self.Writers.setText(SqlRecord.value("writers").replace("|","\n"))
        self.Publisher.setText(SqlRecord.value("publisher"))
        self.Categories.setText(SqlRecord.value("categories").replace("|","\n"))
        if SqlRecord.value("series_name"):
            self.Series.setText("%s / %s" % (SqlRecord.value("series_name"),
                                             SqlRecord.value("series_no")))
        else:
            self.Series.setText("")
        self.Language.setText(SqlRecord.value("language"))
        if SqlRecord.value("pages"):
            self.Pages.setText(self.tr("%s pages") % SqlRecord.value("pages"))
        else:
            self.Pages.setText("")
        if SqlRecord.value("is_read"):
            self.IsRead.setText(self.tr("Read"))
            self.IsRead.setStyleSheet("color: #090;"
                                      "font: bold italic 8pt 'Verdana';")
        else:
            self.IsRead.setText(self.tr("Not read"))
            self.IsRead.setStyleSheet("color: #900;"
                                      "font: bold italic 8pt 'Verdana';")
        self.Excerpt.setPlainText(SqlRecord.value("excerpt"))
        if SqlRecord.value("cover_path"):
            self.Cover.setPixmap(QtGui.QPixmap(SqlRecord.value("cover_path")))
        else:
            self.Cover.setPixmap(QtGui.QPixmap())

