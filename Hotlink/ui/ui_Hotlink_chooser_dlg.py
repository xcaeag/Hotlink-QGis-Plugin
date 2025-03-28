# Form implementation generated from reading ui file
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from qgis.PyQt import uic
from qgis.PyQt import QtCore, QtWidgets

from Hotlink.__about__ import DIR_PLUGIN_ROOT

Dialog, _ = uic.loadUiType(str(DIR_PLUGIN_ROOT / "ui" / "Hotlink_chooser_dlg.ui"))


class Ui_Dialog(object):

    def setupUi(self, Dialog):
        Dialog.resize(261, 171)
        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setGeometry(QtCore.QRect(10, 10, 241, 22))
        self.choose = QtWidgets.QAction(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
