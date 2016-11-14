# -*- coding: utf-8 -*-

"""@package HotlinkMT
"""

from __future__ import unicode_literals
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import re

from Hotlink_chooser_dlg import ChooserDlg

class HotlinkMT(QgsMapTool):
    """Hotlink tool. It is this class that manages the mouse capture...
    """

    def __init__(self, plugin):
        """Tool initialization
        """
        QgsMapTool.__init__(self, plugin.canvas)

        # specifics initializations
        self.canvas = plugin.canvas
        self.plugin = plugin
        self.featuresFound = []
        self.uniqueFeaturesFound = []
        self.ixFeature = 0
        self.__pos = None
        self.chooserDlg = None
        self.request = QgsFeatureRequest()
        self.request.setFlags(QgsFeatureRequest.Flags(QgsFeatureRequest.NoGeometry | QgsFeatureRequest.ExactIntersect))

    def pos(self):
        try:
            return self.toMapCoordinates(self.__pos)
        except:
            return None
        
    def canvasPressEvent(self, event):
        pass

    def escape(self, t):
        """HTML-escape the text in `t`."""
        return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;").replace('"', "&quot;").replace(' ', "&nbsp;")

    def _layer_tooltip(self, layer, feat):
        df = layer.displayField()
        idx = layer.fieldNameIndex( df )
        if idx < 0:
            context = QgsExpressionContext()
            context.appendScope(QgsExpressionContextUtils.globalScope())
            context.appendScope(QgsExpressionContextUtils.projectScope())
            context.appendScope(QgsExpressionContextUtils.layerScope(layer))
            context.appendScope( QgsExpressionContextUtils.mapSettingsScope( self.canvas.mapSettings() ) )
            context.setFeature( feat )

            return QgsExpression.replaceExpressionText( df, context ).replace('\n', "<br/>")
        else:
            return self.escape(layer.name()) + "&nbsp;-&nbsp;" + self.escape(unicode(feat.attribute(df)))

        return tooltip

    def findUnderlyingObjects(self, event, saveFeatures):
        """On mouse movement, we identify the underlying objects
        """

        if not self.plugin.active:
            return

        try:
            self.__pos = event.pos()

            # find objects
            features = self._getFeatures()

            # if there are
            if features:
                #QgsMessageLog.logMessage(str(len(features))+" objets trouvés", 'Extensions')
                # adjust the cursor
                self.canvas.setCursor(QCursor(Qt.WhatsThisCursor))

                # build a list of tuples Name / feature / layer / id for construction of the tool tip, the interface of choice
                if saveFeatures:
                    self.uniqueFeaturesFound = []
                    self.featuresFound = [ {"actionName":QtGui.QApplication.translate("aeag_search", "Choose...", None, QtGui.QApplication.UnicodeUTF8), "feature":None, "layer":None, "idxAction":None} ]

                tooltip = []

                for featData in features:
                    feat = featData["feature"]
                    layer = featData["layer"]
                    for idxAction, action in ((idxAction, layer.actions()[idxAction]) for idxAction in range(layer.actions().size())):
                        try:
                            if layer.displayField() and feat.attribute(layer.displayField()):
                                actionName = '{0} ({1})'.format(action.name(), feat.attribute(layer.displayField()))
                            else:
                                actionName = action.name()
                        except:
                            actionName = action.name()

                        if saveFeatures:
                            try:
                                self.uniqueFeaturesFound.index({"actionName":"    "+actionName, "feature":feat.id(), "action":action.action() } )
                            except:
                                self.uniqueFeaturesFound.append( {"actionName":"    "+actionName, "feature":feat.id(), "action":action.action() } )
                                self.featuresFound.append( {"actionName":"    "+actionName, "feature":feat, "layer":layer, "idxAction":idxAction} )

                        tip = self._layer_tooltip(layer, feat)
                        try:
                            tooltip.index(tip)
                        except:
                            tooltip.append(tip)

                # display
                if (self.plugin.optionShowTips):
                    self.canvas.setToolTip('<p>'+'<br/>'.join(tooltip)+'</p>')

            else:
                # without objects, restore the cursor ...
                if saveFeatures:
                    self.uniqueFeaturesFound = []
                    self.featuresFound = []

                self.canvas.setCursor(QCursor(Qt.ArrowCursor))
                if (self.plugin.optionShowTips):
                    self.canvas.setToolTip("")
        except:
            pass

    def canvasMoveEvent(self,event):
        """On mouse movement, we identify the underlying objects
        """
        if (self.plugin.optionShowTips):
            self.findUnderlyingObjects(event, False)

    def canvasDoubleClickEvent(self, event):
        pass

    def canvasPressEvent(self, event):
        pass

    def keyPressEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):
        """On click, do action
        """
        if not self.plugin.active:
            return

        # left click only
        if event.button() not in (Qt.LeftButton, Qt.RightButton):
            return

        self.findUnderlyingObjects(event, True)

        # if a single action (2 lines in the list)
        if len(self.featuresFound) == 2:
            layer = self.featuresFound[1]["layer"]
            idx = self.featuresFound[1]["idxAction"]
            feature = self.featuresFound[1]["feature"]

            self.doAction(layer, idx, feature)

        else:
            # to choose the action to trigger
            canvasPos = self.canvas.mapToGlobal(QPoint(0,0))
            self.chooserDlg = ChooserDlg(self, self.featuresFound, canvasPos.x() + self.__pos.x(), canvasPos.y() + self.__pos.y())
            self.chooserDlg.go()

    def activate(self):
        pass

    def deactivate(self):
        pass

    def doAction(self, layer, idx, feature):
        if layer.actions().at(idx).action() == 'openFeatureForm':
            self.plugin.iface.openFeatureForm(layer, feature)
        else :
            ctxt = QgsExpressionContext()
            ctxt.appendScope(QgsExpressionContextUtils.globalScope())
            ctxt.appendScope(QgsExpressionContextUtils.projectScope())
            ctxt.appendScope(QgsExpressionContextUtils.mapSettingsScope(self.canvas.mapSettings()))
            # Add click_x and click_y to context
            p = self.toLayerCoordinates(layer, self.pos())
            myScope = QgsExpressionContextScope()
            myScope.addVariable(QgsExpressionContextScope.StaticVariable("click_x", p.x(), True))
            myScope.addVariable(QgsExpressionContextScope.StaticVariable("click_y", p.y(), True))
            ctxt.appendScope(myScope)

            layer.actions().doAction(idx, feature, ctxt)

    def onChoose(self, idx):
        """Do action
        """
        tab = self.featuresFound[idx]
        self.doAction(tab["layer"], tab["idxAction"], tab["feature"])

    def _getFeatures(self):
        """Identify objects under the mouse, having actions
        """
        searchRadius = self.searchRadiusMU(self.canvas)
        point = self.toMapCoordinates(self.__pos)

        features = []

        rect = QgsRectangle()
        rect.setXMinimum(point.x() - searchRadius)
        rect.setXMaximum(point.x() + searchRadius)
        rect.setYMinimum(point.y() - searchRadius)
        rect.setYMaximum(point.y() + searchRadius)
        for layer in self.canvas.layers():
            # treat only vector layers having actions
            if layer.type() == QgsMapLayer.VectorLayer and layer.actions().size() > 0:
                self.request.setFilterRect(self.toLayerCoordinates(layer, rect))
                for feature in layer.getFeatures(self.request):
                    features.append({"layer":layer, "feature":feature})

        return features
