#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 10.11.2011

import os
import sys

import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

from PyQt4 import QtGui, QtCore
from mainwindow import MainWindow

if __name__ == '__main__':
    if not os.path.exists("covers"):
        os.makedirs("covers")
    myApp = QtGui.QApplication(sys.argv)
    Translator = QtCore.QTranslator()
    Translator.load("abibliophile_tr.qm")
    myApp.installTranslator(Translator)
    myApp.setStyle(QtGui.QStyleFactory.create("cleanlooks"))

    myBibliophile = MainWindow()
    myBibliophile.show()
    
    myApp.exec_()
