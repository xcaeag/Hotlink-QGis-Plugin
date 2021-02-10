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

# Import the PyQt and QGIS libraries
import os
from PyQt5.QtCore import Qt, QTranslator, QCoreApplication, QSettings, QFileInfo
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon, QCursor

from qgis.core import QgsExpressionFunction

# Initialize Qt resources from file resources.py
from . import resources

from .HotlinkMT import HotlinkMT

holinkhdialog = None


class ClickXFunction(QgsExpressionFunction):
    """
    Register click_x variable
    """

    def __init__(self, hotlink):
        QgsExpressionFunction.__init__(
            self,
            "$hotlink_x",
            0,
            "Python",
            self.tr(
                """<h1>$hotlink_x</h1>
Variable filled by hotlink plugin, when a click occured.<br/>
<h2>Return value</h2>
The X coordinate in current SRID
        """
            ),
        )
        self.hotlink = hotlink

    def tr(self, message):
        return QCoreApplication.translate("ClickXFunction", message)

    def func(self, values, feature, parent):
        return self.hotlink.clickX()


class ClickYFunction(QgsExpressionFunction):
    """
    Register click_y variable
    """

    def __init__(self, hotlink):
        QgsExpressionFunction.__init__(
            self,
            "$hotlink_y",
            0,
            "Python",
            self.tr(
                """<h1>$hotlink_y</h1>
Variable filled by hotlink plugin, when a click occured.<br/>
<h2>Return value</h2>
The Y coordinate in current SRID
        """
            ),
        )
        self.hotlink = hotlink

    def tr(self, message):
        return QCoreApplication.translate("ClickYFunction", message)

    def func(self, values, feature, parent):
        return self.hotlink.clickY()


class Hotlink:
    """Hotlink - main class"""

    def __init__(self, iface):
        """Plugin Initialization

        :param iface: Interface QGis
        """

        # Save reference to the QGIS interface
        self.iface = iface
        self.toolBar = None
        self.act_hotlink = None
        self.__mapTool = None
        self.__oldMapTool = None
        self.canvas = self.iface.mapCanvas()
        self.active = False
        self.optionShowTips = False
        self.read()

        locale = QSettings().value("locale/userLocale")
        myLocale = locale[0:2]

        localePath = (
            QFileInfo(os.path.realpath(__file__)).path()
            + "/i18n/Hotlink_"
            + myLocale
            + ".qm"
        )

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)
            QCoreApplication.installTranslator(self.translator)

    def clickX(self):
        try:
            return self.__mapTool.pos().x()
        except:
            return None

    def clickY(self):
        try:
            return self.__mapTool.pos().y()
        except:
            return None

    def store(self):
        s = QSettings()
        s.setValue("Hotlink/optionShowTips", (self.optionShowTips))

    def read(self):
        s = QSettings()
        try:
            self.optionShowTips = s.value("Hotlink/optionShowTips", (False), type=bool)
        except:
            pass

    def initGui(self):
        self.toolBar = self.iface.pluginToolBar()
        self.act_hotlink = QAction(
            QIcon(":plugins/Hotlink/hotlink.png"), "Hotlink", self.iface.mainWindow()
        )
        self.act_hotlink.setCheckable(True)
        self.toolBar.addAction(self.act_hotlink)
        # Activate on button pressed
        self.act_hotlink.triggered.connect(self.do_hotlink)

    def unload(self):
        """Remove action"""
        self.toolBar.removeAction(self.act_hotlink)

    def do_hotlink(self):
        """Activate/Deactivate plugin"""

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

        self.canvas.mapToolSet.connect(self.deactivate)

    def deactivate(self):
        """Plugin deactivation"""
        self.active = False

        self.canvas.mapToolSet.disconnect(self.deactivate)
        self.act_hotlink.setChecked(False)
        self.canvas.unsetMapTool(self.__mapTool)
        self.canvas.setMapTool(self.__oldMapTool)
        self.canvas.setToolTip("")

        del self.__mapTool
