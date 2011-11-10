#!/usr/bin/env python
# -.- coding: utf-8 -.-
# Author  : Deniz Turgut
# Created : 07.11.2011

from PyQt4 import QtGui, QtCore, QtNetwork

class Cover(QtGui.QLabel):
    def __init__(self, parent=None):
        super(Cover, self).__init__(parent=parent)
        self.labelText = self.tr("Left click to load cover...\n\nRight click to remove cover.")
        self.setText(self.labelText)
        self.setFixedSize(200,300)
        self.setStyleSheet("border: 1px solid; font: 14px Arial;")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.Manager = QtNetwork.QNetworkAccessManager(self)
        self.Manager.finished.connect(self._downloadFinished)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._open()
        elif event.button() == QtCore.Qt.RightButton:
            self._remove()

    def _open(self):
        CoverName = QtGui.QFileDialog.getOpenFileName(parent=self,
                                                        caption=self.tr("Select cover image..."),
                                                        filter=self.tr("Images (*.jpg)"))
        if CoverName: self.fromFile(CoverName)

    def _remove(self):
        self.setPixmap(QtGui.QPixmap())
        self.setText(self.labelText)

    def _loadFromData(self, data):
        p = QtGui.QPixmap()
        p.loadFromData(data,format="jpg")
        self.setPixmap(p.scaled(QtCore.QSize(200,300),QtCore.Qt.KeepAspectRatio))

    def fromFile(self, filename):
        CoverFile = QtCore.QFile(filename)
        if CoverFile.open(CoverFile.ReadOnly):
            self._loadFromData(CoverFile.readAll())
        CoverFile.close()

    def fromUrl(self, url):
        self.Manager.get(QtNetwork.QNetworkRequest(QtCore.QUrl(url)))

    def _downloadFinished(self, reply):
        self._loadFromData(reply.readAll())

    def toByteArray(self):
        ByteArray = QtCore.QByteArray()
        Buffer = QtCore.QBuffer(ByteArray)
        Buffer.open(Buffer.WriteOnly)
        Pixmap = self.pixmap()
        if Pixmap is not None:
            Pixmap.save(Buffer,format="jpg")
        return ByteArray
