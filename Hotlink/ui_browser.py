# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_atlashelp.ui'
#
# Created: Tue Jan 24 23:32:27 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui

class Ui_browser(object):
    def setupUi(self, featureInfo):
        featureInfo.setObjectName("Hotlink")
        featureInfo.resize(800, 650)
        self.verticalLayout = QtGui.QVBoxLayout(featureInfo)
        self.verticalLayout.setObjectName("verticalLayout")
        self.helpContent = QtWebKit.QWebView(featureInfo)
        self.helpContent.setObjectName("featureInfoContent")
        self.verticalLayout.addWidget(self.helpContent)
        self.buttonBox = QtGui.QDialogButtonBox(featureInfo)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(featureInfo)
        self.buttonBox.QObject.accepted.connect(featureInfo.accept)
        self.buttonBox.QObject.rejected.connect(featureInfo.reject)
        QtCore.QMetaObject.connectSlotsByName(featureInfo)

    def retranslateUi(self, w):
        w.setWindowTitle("Hotlink")
