# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			 	 : Hotlink plugin
Description          : Triggers actions on single click
Date                 : 24/Jun/11 
copyright            : (C) 2011 by AEAG
email                : xavier.culos@eau-adour-garonne.fr 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 
"""
from __future__ import unicode_literals
# Import the PyQt and QGIS libraries
import os
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
from PyQt4 import QtCore, QtGui, QtWebKit

# Initialize Qt resources from file resources.py
import resources

from HotlinkMT import HotlinkMT
from ui_browser import Ui_browser


holinkhdialog = None

class Hotlink: 
    """Hotlink - main class
    """
    
    def __init__(self, iface):
        """Plugin Initialization
        
        @param iface Interface QGis
        """
        
        # Save reference to the QGIS interface
        self.iface = iface
        self.toolBar = None
        self.act_hotlink = None
        self.__mapTool = None
        self.__oldMapTool = None
        self.canvas = self.iface.mapCanvas()
        self.active = False
        
        locale = QSettings().value("locale/userLocale")
        myLocale = locale[0:2]
        
        localePath = QFileInfo(os.path.realpath(__file__)).path()+"/i18n/Hotlink_" + myLocale + ".qm"
        
        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)
        
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def initGui(self):  
        self.act_hotlink = QAction(QIcon(":plugins/Hotlink/hotlink.png"),  ("Hotlink"),  self.iface.mainWindow())
        self.act_hotlink.setCheckable(True)
        # Activate on button pressed
        self.act_hotlink.triggered.connect(self.do_hotlink)

        try:
            from aeag import aeag
            self.toolBar = aeag.aeagToolbarAdd(self.act_hotlink)
        except:
            self.toolBar = self.iface.pluginToolBar()
            self.toolBar.addAction(self.act_hotlink)
            self.iface.addPluginToMenu("&Hotlink", self.act_hotlink)
    
    def unload(self):
        """Remove action
        """
        try:
            from aeag import aeag
            self.toolBar = aeag.aeagToolbarRemove(self.toolBar, self.act_hotlink)
        except:
            self.toolBar.removeAction(self.act_hotlink)
            self.iface.removePluginMenu("&Hotlink", self.act_hotlink)

    def do_hotlink(self): 
        """Activate/Deactivate plugin
        """
        
        self.active = not self.active
        
        if not self.active:
            self.deactivate()
            return
        
        # tool init (HotlinkMT)
        self.__oldMapTool = self.canvas.mapTool()
        self.canvas.unsetMapTool(self.canvas.mapTool())
        self.__mapTool = HotlinkMT(self)
        self.canvas.setMapTool(self.__mapTool)
        self.canvas.setCursor(QCursor(Qt.ArrowCursor))
        self.canvas.setFocus(Qt.OtherFocusReason)
            
        # others plugisn deactivation
        self.canvas.mapToolSet.connect(self.deactivate)
    
    def deactivate(self):
        """Plugin deactivation
        """
        
        self.active = False
        
        self.canvas.mapToolSet.disconnect(self.deactivate)
        self.act_hotlink.setChecked(False)
        self.canvas.unsetMapTool(self.__mapTool)
        self.canvas.setMapTool(self.__oldMapTool)
        self.canvas.setToolTip("")
        
        del self.__mapTool

    @staticmethod
    def doOpenUrl(url):
        holinkhdialog = QDialog()
        holinkhdialog.setModal(True)
        holinkhdialog.ui = Ui_browser()
        holinkhdialog.ui.setupUi(holinkhdialog)
        holinkhdialog.ui.helpContent.setUrl(QUrl(url))
        holinkhdialog.ui.helpContent.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateExternalLinks) # Handle link clicks by yourself
        holinkhdialog.ui.helpContent.linkClicked.connect(doLink)
        holinkhdialog.ui.helpContent.page().currentFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOn)
        holinkhdialog.show()
        result = holinkhdialog.exec_()
        del holinkhdialog
        
def doLink( url ):
    if url.host() == "" :
        holinkhdialog.ui.helpContent.page().currentFrame().load(url)
    else:
        QDesktopServices.openUrl( url )
