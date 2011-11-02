# -.- coding: utf-8 -.-
import os

from PyQt4 import QtGui, QtCore, QtSql

from mylistwidget import MyListWidget
import idefix
import icons

class SearchThread(QtCore.QThread):
    searchCompleted = QtCore.pyqtSignal(list)
    progressUpdated = QtCore.pyqtSignal(int,int,int)
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self,parent)

    def SetUp(self,SearchType,SearchData):
        if SearchType == 0: # Keyword search
            self.SearchParameters = SearchData
            self.Searcher = idefix.SearchBooksWithKeyword
        elif SearchType == 1: # Book name search
            self.SearchParameters = {"aranan_yer":"1",
                                     "dukkan":"1",
                                     "eser":SearchData,
                                     "kisi":"",
                                     "sayfa":"1",
                                     "sira":"4",
                                     "yayID":"0"}
            self.Searcher = idefix.SearchBooksWithName
        else: # Writer search
            self.SearchParameters = {"aranan_yer":"1",
                                     "dukkan":"1",
                                     "eser":"",
                                     "kisi":SearchData,
                                     "sayfa":"1",
                                     "sira":"4",
                                     "yayID":"0"}
            self.Searcher = idefix.SearchBooksWithName

    def run(self):
        Results = self.Searcher(self.SearchParameters,self.Progress)
        self.searchCompleted.emit(Results)

    def Progress(self,minimum,maximum,value):
        self.progressUpdated.emit(minimum,maximum,value)


class DownloadThread(QtCore.QThread):
    downloadCompleted = QtCore.pyqtSignal(dict)
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def SetUp(self, url):
        self.url = url

    def run(self):
        result = idefix.DownloadBookInfo(self.url)
        self.downloadCompleted.emit(result)

class AddEditDialog(QtGui.QDialog):
    def __init__(self,Parent=None,Book=None):
        QtGui.QDialog.__init__(self,Parent,QtCore.Qt.WindowMaximizeButtonHint)
        self.setWindowIcon(QtGui.QIcon(":icons/book_add.ico"))
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.Book = Book
        self.BookCoverPath = ""
        self.CreateWidgets()
        self.UpdateSearchButtonStatus()
        self.Searcher = SearchThread(self)
        self.Downloader = DownloadThread(self)
        if Book is None:
            self.setWindowTitle("Kitap ekle...")
            self.Book = QtSql.QSqlRecord()
            self.Book.append(QtSql.QSqlField("id"))
            self.Book.append(QtSql.QSqlField("title"))
            self.Book.append(QtSql.QSqlField("writers"))
            self.Book.append(QtSql.QSqlField("publisher"))
            self.Book.append(QtSql.QSqlField("categories"))
            self.Book.append(QtSql.QSqlField("series_name"))
            self.Book.append(QtSql.QSqlField("series_no"))
            self.Book.append(QtSql.QSqlField("language"))
            self.Book.append(QtSql.QSqlField("pages"))
            self.Book.append(QtSql.QSqlField("is_read"))
            self.Book.append(QtSql.QSqlField("excerpt"))
            self.Book.append(QtSql.QSqlField("date_added"))
        else:
            self.setWindowTitle(u"Kitap düzenle...")
            if os.path.exists("covers/%s.jpg" % self.Book.value(0)):
                self.BookCoverPath = "covers/%s.jpg" % self.Book.value(0)
            self.RecordToWidget()
            self.SearchQuery.setText(self.Book.value(1))

    def CreateWidgets(self):
        Splitter = QtGui.QSplitter()        
        Splitter.addWidget(self.CreateSearchWidget())
        Splitter.addWidget(self.CreateBookWidget())
        
        LayoutCentral = QtGui.QVBoxLayout()
        LayoutCentral.addWidget(Splitter)
        
        self.setLayout(LayoutCentral)

    def CreateSearchWidget(self):
        WidgetSearch = QtGui.QWidget()

        # Widgets
        self.SearchType = QtGui.QComboBox()
        self.SearchType.addItems([u"Kelime",u"Kitap adı",u"Yazar"])
        self.SearchQuery = QtGui.QLineEdit()
        self.SearchQuery.textChanged.connect(self.UpdateSearchButtonStatus)
        self.SearchQuery.returnPressed.connect(self.SearchBook)
        self.SearchQuery.setPlaceholderText(u"idefix'te ara...")
        self.SearchButton = QtGui.QPushButton()
        self.SearchButton.setAutoDefault(False)
        self.SearchButton.setIcon(QtGui.QIcon(":icons/search.ico"))
        self.SearchButton.setFixedSize(25,25)
        self.SearchButton.clicked.connect(self.SearchBook)
        self.SearchList = QtGui.QListWidget()
        self.SearchList.setSortingEnabled(True)
        self.SearchList.doubleClicked.connect(self.DownloadBookInfo)
        self.SearchProgress = QtGui.QProgressBar()
        self.SearchProgress.setTextVisible(False)
        self.SearchStatus = QtGui.QLabel()

        LayoutSearchField = QtGui.QHBoxLayout()
        LayoutSearchField.addWidget(self.SearchType)
        LayoutSearchField.addWidget(self.SearchQuery)
        LayoutSearchField.addWidget(self.SearchButton)

        LayoutSearch = QtGui.QVBoxLayout()
        LayoutSearch.addLayout(LayoutSearchField)
        LayoutSearch.addWidget(self.SearchList)
        LayoutSearch.addWidget(self.SearchProgress)
        LayoutSearch.addWidget(self.SearchStatus)

        WidgetSearch.setLayout(LayoutSearch)
        return WidgetSearch

    def CreateBookWidget(self):
        WidgetBook = QtGui.QWidget()
        LayoutBook = QtGui.QGridLayout()
        WidgetBook.setLayout(LayoutBook)

        self.BookTitle = QtGui.QLineEdit()
        self.BookWriters = MyListWidget()
        self.BookWriters.setFixedHeight(120)
        self.BookPublisher = QtGui.QLineEdit()
        self.BookCategories = MyListWidget()
        self.BookCategories.setFixedHeight(120)
        self.BookSeriesName = QtGui.QLineEdit()
        self.BookSeriesNo = QtGui.QLineEdit()
        self.BookLanguage = QtGui.QLineEdit()
        self.BookPages = QtGui.QLineEdit()
        self.BookIsRead = QtGui.QCheckBox("Okundu")
        self.BookExcerpt = QtGui.QTextEdit()
        self.BookCover = QtGui.QLabel()
        self.BookCover.setFixedSize(200,300)
        self.BookCover.setAlignment(QtCore.Qt.AlignHCenter)
        self.BookCoverPath = ""

        LayoutButton = QtGui.QHBoxLayout()
        self.ButtonOk = QtGui.QPushButton("Kaydet")
        self.ButtonOk.setAutoDefault(False)
        self.ButtonOk.setIcon(QtGui.QIcon(":icons/ok.ico"))
        self.ButtonOk.clicked.connect(self.TriggeredOK)
        self.ButtonCancel = QtGui.QPushButton("Iptal")
        self.ButtonCancel.setAutoDefault(False)
        self.ButtonCancel.setIcon(QtGui.QIcon(":icons/delete.ico"))
        self.ButtonCancel.clicked.connect(self.TriggeredCancel)
        LayoutButton.addStretch()
        LayoutButton.addWidget(self.ButtonCancel)
        LayoutButton.addWidget(self.ButtonOk)

        LayoutBook.addWidget(QtGui.QLabel(u"Kitap:"),0,0,QtCore.Qt.AlignRight)
        LayoutBook.addWidget(self.BookTitle,0,1,1,5)
        LayoutBook.addWidget(QtGui.QLabel(u"Yazar:"),1,0,QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        LayoutBook.addWidget(self.BookWriters,1,1,1,3)
        LayoutBook.addWidget(QtGui.QLabel(u"Yayınevi:"),2,0,QtCore.Qt.AlignRight)
        LayoutBook.addWidget(self.BookPublisher,2,1,1,3)
        LayoutBook.addWidget(QtGui.QLabel(u"Kategori:"),3,0,QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        LayoutBook.addWidget(self.BookCategories,3,1,1,3)
        LayoutBook.addWidget(QtGui.QLabel(u"Seri:"),4,0,QtCore.Qt.AlignRight)
        LayoutBook.addWidget(self.BookSeriesName,4,1)
        LayoutBook.addWidget(QtGui.QLabel(u"No:"),4,2,QtCore.Qt.AlignRight)
        LayoutBook.addWidget(self.BookSeriesNo,4,3)
        LayoutBook.addWidget(QtGui.QLabel(u"Dil:"),5,0,QtCore.Qt.AlignRight)
        LayoutBook.addWidget(self.BookLanguage,5,1)
        LayoutBook.addWidget(QtGui.QLabel(u"Sayfa:"),5,2,QtCore.Qt.AlignRight)
        LayoutBook.addWidget(self.BookPages,5,3)
        LayoutBook.addWidget(self.BookIsRead,5,4,QtCore.Qt.AlignHCenter)
        LayoutBook.addWidget(QtGui.QLabel(u"Konu:"),6,0,QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        LayoutBook.addWidget(self.BookExcerpt,6,1,1,5)
        LayoutBook.addWidget(self.BookCover,1,4,4,1,QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        LayoutBook.addLayout(LayoutButton,7,1,1,5)
        LayoutBook.setRowStretch(6,1)

        return WidgetBook

    def UpdateSearchButtonStatus(self,Text=""):
        if Text:
            self.SearchButton.setDisabled(False)
        else:
            self.SearchButton.setDisabled(True)

    def SetProgressBar(self,minimum,maximum,value):
        self.SearchProgress.setMinimum(minimum)
        self.SearchProgress.setMaximum(maximum)
        self.SearchProgress.setValue(value)

    def SearchBook(self):
        if self.SearchButton.isEnabled():
            self.SearchButton.setDisabled(True)
            self.SearchStatus.setText(u"Aranıyor...")
            self.Searcher.SetUp(self.SearchType.currentIndex(),
                                unicode(self.SearchQuery.text()).encode("iso-8859-9"))
            self.Searcher.searchCompleted.connect(self.AddSearchedBooks)
            self.Searcher.progressUpdated.connect(self.SetProgressBar)
            self.Searcher.start()

    def AddSearchedBooks(self,BookList):
        self.Searcher.wait()
        self.SearchList.clear()
        self.SearchStatus.setText(u"%d kitap bulundu." % len(BookList))
        for aBook in BookList:
            BookItem = QtGui.QListWidgetItem(aBook["title"].decode("utf-8"),self.SearchList)
            BookItem.setToolTip("Yazar: "+
                                aBook["writer"].decode("utf-8")+
                                u"\nYayınevi: "+
                                aBook["publisher"].decode("utf-8")+u"\nurl:"+aBook["url"])
            BookItem.setData(QtCore.Qt.UserRole,aBook["url"])
        self.SearchButton.setDisabled(False)


    def DownloadBookInfo(self, Book):
        self.Downloader.SetUp(Book.data(QtCore.Qt.UserRole))
        self.Downloader.downloadCompleted.connect(self.DownloadToRecord)
        self.Downloader.start()

    def DownloadToRecord(self,Info):
        self.BookCoverPath = Info["image_path"]
        self.Book.setValue(1,Info["title"].decode("utf-8"))
        self.Book.setValue(2,Info["writers"].decode("utf-8"))
        self.Book.setValue(3,Info["publisher"].decode("utf-8"))
        self.Book.setValue(4,Info["categories"].decode("utf-8"))
        self.Book.setValue(5,"")
        self.Book.setValue(6,"")
        self.Book.setValue(7,Info["language"].decode("utf-8"))
        self.Book.setValue(8,Info["pages"].decode("utf-8"))
        self.Book.setValue(9,"0")
        self.Book.setValue(10,Info["excerpt"].decode("utf-8"))
        self.Book.setValue(11,"")
        self.RecordToWidget()
        

    def RecordToWidget(self):
        self.BookTitle.setText(self.Book.value(1))
        self.BookWriters.Clear()
        for aWriter in self.Book.value(2).split("|"):
            self.BookWriters.AddItem(aWriter)
        self.BookPublisher.setText(self.Book.value(3))
        self.BookCategories.Clear()
        for aCategory in self.Book.value(4).split("|"):
            self.BookCategories.AddItem(aCategory)
        self.BookSeriesName.setText(self.Book.value(5))
        self.BookSeriesNo.setText(str(self.Book.value(6)))
        self.BookLanguage.setText(self.Book.value(7))
        self.BookPages.setText(str(self.Book.value(8)))
        self.BookIsRead.setChecked(self.Book.value(9)=="1")
        self.BookExcerpt.setPlainText(self.Book.value(10))
        if self.BookCoverPath:
            self.BookCover.setPixmap(QtGui.QPixmap(self.BookCoverPath).scaled(200,300,QtCore.Qt.KeepAspectRatio))
        
    def WidgetToRecord(self):
        self.Book.setValue(1,self.BookTitle.text())
        self.Book.setValue(2,"|".join(self.BookWriters.GetItems()))
        self.Book.setValue(3,self.BookPublisher.text())
        self.Book.setValue(4,"|".join(self.BookCategories.GetItems()))
        self.Book.setValue(5,self.BookSeriesName.text())
        self.Book.setValue(6,self.BookSeriesNo.text())
        self.Book.setValue(7,self.BookLanguage.text())
        self.Book.setValue(8,self.BookPages.text())
        self.Book.setValue(9,"1" if self.BookIsRead.isChecked() else "0")
        self.Book.setValue(10,self.BookExcerpt.toPlainText())
        self.Book.setValue(11,"")

    def TriggeredOK(self):
        self.WidgetToRecord()
        self.accept()

    def TriggeredCancel(self):
        self.Searcher.terminate()
        self.Searcher.wait()
        self.Downloader.terminate()
        self.Downloader.wait()
        self.reject()
