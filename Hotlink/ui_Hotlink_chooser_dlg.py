# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Program Files\Quantum GIS Wroclaw\apps\qgis\python\plugins\Hotlink\Hotlink_chooser_dlg.ui'
#
# Created: Mon Jun 27 18:04:15 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from __future__ import unicode_literals
from PyQt4 import QtCore, QtGui

_fromUtf8 = lambda s: (s.decode("utf-8").encode("latin-1")) if s else s
_toUtf8 = lambda s: s.decode("latin-1").encode("utf-8") if s else s

class Ui_Dialog(object):

    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(241, 22)
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(0, 0, 241, 22))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))

        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("aeag_search", "Actions...", None, QtGui.QApplication.UnicodeUTF8))

