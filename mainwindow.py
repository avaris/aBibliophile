# -.- coding: utf-8 -.-
import os
import shutil

from PyQt4 import QtGui, QtCore, QtSql

from addeditdialog import AddEditDialog
from grouperproxy import GrouperProxy
from sortfilterproxy import SortFilterProxy
import icons

class MainWindow(QtGui.QMainWindow):
    def __init__(self,Parent=None):
        QtGui.QMainWindow.__init__(self,Parent)
        self.setWindowTitle("aBibliophile (c) Avaris")
        self.setWindowIcon(QtGui.QIcon(":icons/abibliophile.ico"))
        self.setFont(QtGui.QFont("Verdana"))
        self.Database = QtSql.QSqlDatabase("QSQLITE")
        self.Model = QtSql.QSqlTableModel(self,self.Database)
        self.GrouperProxy = GrouperProxy()
        self.GrouperProxy.setSourceModel(self.Model,2)
        self.ProxyModel = SortFilterProxy()
        self.ProxyModel.setSourceModel(self.Model)
        self.Mapper = QtGui.QDataWidgetMapper()
        self.Mapper.setModel(self.Model)
        self.CreateCentralWidget()
        self.CreateActions()
        self.CreateToolbar()
        self.CreateMenu()
        self.DatabaseConnect("deneme.adb")
        self.showMaximized()

    def CreateCentralWidget(self):
        CentralWidget = QtGui.QSplitter()
        CentralWidget.addWidget(self.CreateNavigationWidget())
        CentralWidget.addWidget(self.CreateBookWidget())
        self.setCentralWidget(CentralWidget)

    def CreateNavigationWidget(self):
        self.NavigationFilterType = QtGui.QComboBox()
        self.NavigationFilterType.addItems([u"Kitap adı",u"Yazar",u"Yayınevi",u"Kategori"])
        self.NavigationFilterType.currentIndexChanged.connect(self.SetFilterColumn)
        self.NavigationFilterQuery = QtGui.QLineEdit()
        self.NavigationFilterQuery.textChanged.connect(self.ProxyModel.setFilterRegExp)
        NavigationFilterBox = QtGui.QGroupBox(u"Filtrele")
        NavigationFilterLayout = QtGui.QHBoxLayout()
        NavigationFilterLayout.addWidget(self.NavigationFilterType)
        NavigationFilterLayout.addWidget(self.NavigationFilterQuery)
        NavigationFilterBox.setLayout(NavigationFilterLayout)

        self.NavigationGroupBy = QtGui.QComboBox()
        self.NavigationGroupBy.addItem(u"Yazar",2)
        self.NavigationGroupBy.addItem(u"Yayınevi",3)
        self.NavigationGroupBy.addItem(u"Kategori",4)
        self.NavigationGroupBy.addItem(u"Dil",7)
        self.NavigationGroupBy.addItem(u"Okunma",9)
        self.NavigationGroupBy.currentIndexChanged.connect(self.SetGroupColumn)
        NavigationGroupLayout = QtGui.QHBoxLayout()
        NavigationGroupLayout.addWidget(self.NavigationGroupBy)
        NavigationGroupBox = QtGui.QGroupBox(u"Grupla")
        NavigationGroupBox.setCheckable(True)
        NavigationGroupBox.setChecked(False)
        NavigationGroupBox.setLayout(NavigationGroupLayout)
        NavigationGroupBox.toggled.connect(self.SetGrouping)
        
        self.NavigationTree = QtGui.QTreeView()
        self.NavigationTree.setModel(self.ProxyModel)
        self.NavigationTree.setHeaderHidden(True)

        NavigationGroupFilterLayout = QtGui.QHBoxLayout()
        NavigationGroupFilterLayout.addWidget(NavigationFilterBox)
        NavigationGroupFilterLayout.addWidget(NavigationGroupBox)

        NavigationLayout = QtGui.QVBoxLayout()
        NavigationLayout.addLayout(NavigationGroupFilterLayout)
        NavigationLayout.addWidget(self.NavigationTree)

        NavigationWidget = QtGui.QWidget()
        NavigationWidget.setLayout(NavigationLayout)
        return NavigationWidget

    def CreateBookWidget(self):
        self.BookTitle = QtGui.QLabel()
        self.BookTitle.setWordWrap(True)
        self.BookTitle.setAlignment(QtCore.Qt.AlignHCenter)
        self.BookTitle.setStyleSheet("color: #fc3;"
                                     "background: #222;"
                                     "font: 14pt 'Tahoma';"
                                     "border: 2px solid #900;"
                                     "border-radius: 10px;"
                                     "padding: 5px;"
                                     "margin: 10px;")

        self.BookWriters = QtGui.QLabel()
        self.BookWriters.setStyleSheet("color: #33f;"
                                       "font: italic 12pt 'Verdana';")
        
        self.BookPublisher = QtGui.QLabel()
        self.BookPublisher.setStyleSheet("color: #531;"
                                          "font: bold 10pt 'Tahoma';")
        
        self.BookCategories = QtGui.QLabel()
        
        self.BookSeries = QtGui.QLabel()
        self.BookSeries.setStyleSheet("color: #919;"
                                      "font: italic 8pt 'Verdana';")
        self.BookLanguage = QtGui.QLabel()
        self.BookLanguage.setStyleSheet("font: italic 8pt 'Verdana';")
        self.BookPages = QtGui.QLabel()
        self.BookPages.setStyleSheet("font: italic 8pt 'Verdana';")
        self.BookIsRead = QtGui.QLabel()
        self.BookCover = QtGui.QLabel()
        self.BookCover.setFixedSize(200,300)
        self.BookCover.setAlignment(QtCore.Qt.AlignHCenter)
        self.BookCover.setStyleSheet("border: 1px solid")

        self.BookExcerpt = QtGui.QTextBrowser()
        self.BookOtherTab = QtGui.QTabWidget()
        self.BookOtherTab.addTab(self.BookExcerpt,"Konu")

        LayoutBookSmallStuff = QtGui.QHBoxLayout()
        LayoutBookSmallStuff.addWidget(self.BookLanguage)
        LayoutBookSmallStuff.addWidget(self.BookPages)
        LayoutBookSmallStuff.addWidget(self.BookIsRead)
        LayoutBookInfo = QtGui.QVBoxLayout()
        LayoutBookInfo.addWidget(self.BookWriters)
        LayoutBookInfo.addWidget(self.BookPublisher)
        LayoutBookInfo.addWidget(self.BookCategories)
        LayoutBookInfo.addWidget(self.BookSeries)
        LayoutBookInfo.addLayout(LayoutBookSmallStuff)
        LayoutBookInfo.addStretch()
        LayoutBookInfo.setSpacing(30)

        LayoutBookInfoCover = QtGui.QHBoxLayout()
        LayoutBookInfoCover.addLayout(LayoutBookInfo)
        LayoutBookInfoCover.addWidget(self.BookCover,0,QtCore.Qt.AlignRight)

        LayoutBook = QtGui.QVBoxLayout()
        LayoutBook.addWidget(self.BookTitle)
        LayoutBook.addLayout(LayoutBookInfoCover)
        LayoutBook.addWidget(self.BookOtherTab)

        self.BookWidget = QtGui.QWidget()
        self.BookWidget.setLayout(LayoutBook)
        self.BookWidget.setVisible(False)
        return self.BookWidget

        

    def _CreateAction(self,text,slot=None,shortcut=None,icon=None,tip=None,checkable=False,signal="triggered()"):
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
    
    def CreateActions(self):
        self.ActionDatabaseNew = self._CreateAction("New Database...",self.TriggeredDatabaseNew,"Ctrl+N",":icons/database_new","Create a new database")
        self.ActionDatabaseOpen = self._CreateAction("Open Database...",self.TriggeredDatabaseOpen,"Ctrl+O",":icons/database_open","Open existing database")
        self.ActionBookAdd = self._CreateAction("Add Book...",self.TriggeredBookAdd,"Ctrl+A",":icons/book_add","Add a book")
        self.ActionBookEdit = self._CreateAction("Edit Book...",self.TriggeredBookEdit,"Ctrl+E",":icons/book_edit","Edit book")
        self.ActionBookDelete = self._CreateAction("Delete Book",self.TriggeredBookDelete,"Ctrl+D",":icons/book_delete","Delete book")
        self.ActionAbout = self._CreateAction("About...",self.TriggeredAbout,"F1",":icons/about","About avaShelf")
        self.ActionExit = self._CreateAction("Exit",self.TriggeredExit,"Esc",":icons/delete","Exit avaShelf")
        
        self.UpdateActionStatus()

    def UpdateActionStatus(self):
        self.ActionBookAdd.setEnabled(self.Database.isOpen())

        CurrentIndex = self.MapSelectionToSource(self.NavigationTree.currentIndex())
        self.ActionBookEdit.setEnabled(CurrentIndex.isValid())
        self.ActionBookDelete.setEnabled(CurrentIndex.isValid())
        self.BookWidget.setVisible(CurrentIndex.isValid())
    
    def CreateToolbar(self):
        Toolbar = QtGui.QToolBar()
        Toolbar.addAction(self.ActionDatabaseNew)
        Toolbar.addAction(self.ActionDatabaseOpen)
        Toolbar.addSeparator()
        Toolbar.addAction(self.ActionBookAdd)
        Toolbar.addAction(self.ActionBookEdit)
        Toolbar.addAction(self.ActionBookDelete)
        Toolbar.addSeparator()
        Toolbar.addAction(self.ActionAbout)
        Toolbar.addSeparator()
        Toolbar.addAction(self.ActionExit)
        
        self.addToolBar(Toolbar)

    def CreateMenu(self):
        MenuBar = QtGui.QMenuBar()
        MenuFile = MenuBar.addMenu("File")
        MenuBook = MenuBar.addMenu("Book")
        
        MenuFile.addAction(self.ActionDatabaseNew)
        MenuFile.addAction(self.ActionDatabaseOpen)
        MenuFile.addSeparator()
        MenuFile.addAction(self.ActionAbout)
        MenuFile.addSeparator()
        MenuFile.addAction(self.ActionExit)
        
        MenuBook.addAction(self.ActionBookAdd)
        MenuBook.addAction(self.ActionBookEdit)
        MenuBook.addAction(self.ActionBookDelete)
                
        self.setMenuBar(MenuBar)

    def TriggeredDatabaseNew(self):
        self.DatabaseNew()
        
    def TriggeredDatabaseOpen(self):
        self.DatabaseOpen()

    def TriggeredBookAdd(self):
        AddBookDialog = AddEditDialog(self)
        #AddBookDialog.setModal(True)
        if AddBookDialog.exec_():
            self.Model.insertRecord(-1,AddBookDialog.Book)
            if AddBookDialog.BookCoverPath:
                shutil.move(AddBookDialog.BookCoverPath,
                            "covers/%d.jpg"%self.Model.query().lastInsertId())
            

    def TriggeredBookEdit(self):
        CurrentIndex = self.ProxyModel.mapToSource(self.NavigationTree.currentIndex())
        Row = CurrentIndex.row()
        Record = self.Model.record(Row)
        EditBookDialog = AddEditDialog(self,Record)
        EditBookDialog.setModal(True)
        if EditBookDialog.exec_():
            self.Model.setRecord(Row,EditBookDialog.Book)
            self.Model.submitAll()
            if EditBookDialog.BookCoverPath:
                shutil.move(EditBookDialog.BookCoverPath,
                            "covers/%d.jpg"%Record.value(0))
            self.NavigationTree.setCurrentIndex(CurrentIndex)

    def TriggeredBookDelete(self):
        SelectedIndex = self.MapSelectionToSource(self.NavigationTree.currentIndex())
        SelectedRow = SelectedIndex.row()
        SelectedParent = SelectedIndex.parent()
        SelectedRecord = self.Model.record(SelectedRow)
        SelectedName = SelectedRecord.value(1)
        DeleteConfirm = QtGui.QMessageBox()
        DeleteConfirm.setWindowIcon(QtGui.QIcon("icons/book_delete.ico"))
        DeleteConfirm.setWindowTitle("Kitap sil...")
        DeleteConfirm.setIcon(QtGui.QMessageBox.Warning)
        DeleteConfirm.setText(u"'%s' isimli kitabı silmek istediğinize emin misiniz?" % SelectedName)
        DeleteConfirm.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        if DeleteConfirm.exec_() == QtGui.QMessageBox.Ok:
            self.Model.removeRow(SelectedRow,SelectedParent)
            self.Model.submitAll()

    def TriggeredBookSelected(self,Item,Column):
        self.UpdateActionStatus()

    def TriggeredAbout(self):
        AboutBox = QtGui.QMessageBox()
        AboutBox.setIcon(QtGui.QMessageBox.NoIcon)
        AboutBox.setWindowTitle("About avaShelf")
        AboutBox.setWindowIcon(QtGui.QIcon(":icons/avashelf.ico"))
        AboutBox.setText("aBibliophile ... by Avaris\n(c) 2011")
        AboutBox.setStandardButtons(QtGui.QMessageBox.Ok)
        AboutBox.exec_()
    
    def TriggeredExit(self):
        self.close()

    def DatabaseNew(self):
        DatabaseName = unicode(QtGui.QFileDialog.getSaveFileName(self,
                                                                 "New Database",
                                                                 ".",
                                                                 "avaShelf Databases (*.adb)"))
        if DatabaseName:
            self.DatabaseCreate(DatabaseName)
        else:
            pass # Cancel
    
    def DatabaseOpen(self):
        DatabaseName = unicode(QtGui.QFileDialog.getOpenFileName(self,
                                                                 "Open Database",
                                                                 ".",
                                                                 "avaShelf Databases (*.adb)"))
        if DatabaseName:
            self.DatabaseConnect(DatabaseName)
        else:
            pass # Cancel
    
    def DatabaseCreate(self,DatabaseName):
        self.DatabaseClose()
        if os.path.exists(DatabaseName):
            os.remove(DatabaseName)
        self.Database.setDatabaseName(DatabaseName)
        self.Database.open()
        if self.Database.isOpen():
            self.Database.exec_("""CREATE TABLE books (
                                id INTEGER PRIMARY KEY,
                                title TEXT,
                                writers TEXT,
                                publisher TEXT,
                                categories TEXT,
                                series_name TEXT,
                                series_no TEXT,
                                language TEXT,
                                pages TEXT,
                                is_read TEXT,
                                excerpt TEXT,
                                date_added INTEGER)""")
            self.DatabaseConnect(DatabaseName)
        else:
            print "Problem?"
    
    def DatabaseConnect(self,DatabaseName):
        self.DatabaseClose()
        self.Database.setDatabaseName(DatabaseName)
        self.Database.open()
        if self.Database.isOpen():
            self.Model.setTable("books")
            self.Model.select()
            for i in range(self.Model.columnCount()):
                self.NavigationTree.hideColumn(i)
            self.NavigationTree.showColumn(0)
            self.connect(self.NavigationTree.selectionModel(),
                         QtCore.SIGNAL("currentChanged(QModelIndex,QModelIndex)"),
                         self.SelectionMapper)
            self.UpdateActionStatus()
        else:
            print "Problem?"
            
    def DatabaseClose(self):
        if self.Database.isOpen():
            self.Database.close()

    @QtCore.pyqtSlot(int)
    def SetFilterColumn(self, i):
        self.ProxyModel.setFilterKeyColumn(i+1)

    @QtCore.pyqtSlot(bool)
    def SetGrouping(self, on):
        self.NavigationTree.setCurrentIndex(QtCore.QModelIndex())
        if on:
            self.ProxyModel.setSourceModel(self.GrouperProxy)
        else:
            self.ProxyModel.setSourceModel(self.Model)

    @QtCore.pyqtSlot(int)
    def SetGroupColumn(self, i):
        self.NavigationTree.setCurrentIndex(QtCore.QModelIndex())
        self.GrouperProxy.groupBy(self.NavigationGroupBy.itemData(i))

    def MapSelectionToSource(self, ProxyIndex):
        CurrentIndex = ProxyIndex
        ProxyModel = CurrentIndex.model()
        while isinstance(ProxyModel,QtGui.QAbstractProxyModel):
            CurrentIndex = ProxyModel.mapToSource(CurrentIndex)
            ProxyModel = CurrentIndex.model()
        return CurrentIndex

    def SelectionMapper(self,CurrentProxyIndex,PreviousProxyIndex):
        CurrentIndex = self.MapSelectionToSource(CurrentProxyIndex)

        self.UpdateActionStatus()
        if not CurrentIndex.isValid():
            return
        
        row = CurrentIndex.row()
        record = self.Model.record(row)

        ID = record.value(0)
        CoverFile = "covers/%s.jpg" % ID
        Title = record.value(1)
        Writers = record.value(2).replace("|","\n")
        Publisher = record.value(3)
        Categories = record.value(4).replace("|","\n")
        SeriesName = record.value(5)
        SeriesNo = record.value(6)
        Language = record.value(7)
        Pages = record.value(8)
        if Pages:
            Pages = "%s Sayfa" % Pages
        IsRead = record.value(9)
        Excerpt = record.value(10)
        #DateAdded = record.value(11).toString()

        self.BookTitle.setText(Title)
        self.BookWriters.setText(Writers)
        self.BookPublisher.setText(Publisher)
        self.BookCategories.setText(Categories)
        if SeriesName:
            self.BookSeries.setVisible(True)
            self.BookSeries.setText("%s / %s" % (SeriesName,SeriesNo))
        else:
            self.BookSeries.setVisible(False)
        self.BookLanguage.setText(Language)
        self.BookPages.setText(Pages)
        if IsRead=="0":
            self.BookIsRead.setText(u"Okunmadı")
            self.BookIsRead.setStyleSheet("color: #900;"
                                          "font: bold italic 8pt 'Verdana';")
        else:
            self.BookIsRead.setText(u"Okundu")
            self.BookIsRead.setStyleSheet("color: #090;"
                                          "font: bold italic 8pt 'Verdana';")
        self.BookExcerpt.setPlainText(Excerpt)
        if os.path.exists(CoverFile):
            self.BookCover.setPixmap(QtGui.QPixmap(CoverFile).scaled(200,300,QtCore.Qt.KeepAspectRatio))
        else:
            self.BookCover.setPixmap(QtGui.QPixmap())
