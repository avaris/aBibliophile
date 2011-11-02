# -.- coding: utf-8 -.-
# Author : Deniz Turgut
import os
import sys

import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui
from mainwindow import MainWindow

if __name__ == '__main__':
    if not os.path.exists("covers"):
        os.makedirs("covers")
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    myApp = QtGui.QApplication(sys.argv)

    myApp.setStyle(QtGui.QStyleFactory.create("cleanlooks"))

    myShelf = MainWindow()
    myShelf.show()
    
    myApp.exec_()
