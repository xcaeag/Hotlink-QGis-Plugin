# -*- coding: utf-8 -*-

"""@package HotlinkMT
"""

from PyQt5.QtCore import (Qt, QPoint)
from PyQt5.QtWidgets import (QApplication)
from PyQt5.QtGui import (QCursor)

from qgis.core import (QgsFeatureRequest, QgsExpressionContext, 
                       QgsExpressionContextUtils, QgsProject, QgsExpression, 
                       QgsRectangle, QgsMapLayer)
    
from qgis.gui import (QgsMapTool)

from .Hotlink_chooser_dlg import ChooserDlg

class HotlinkMT(QgsMapTool):
    """Hotlink tool. It is this class that manages the mouse capture...
    """

    def __init__(self, plugin):
        """Tool initialization
        """
        QgsMapTool.__init__(self, plugin.canvas)

        self.canvas = plugin.canvas
        self.plugin = plugin
        self.featuresFound = []
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

    def _layer_tooltip(self, layer, feat):
        try:
            df = layer.displayField()
            if df:
                return layer.name() + " - " + str(feat.attribute(df))
            else:
                context = QgsExpressionContext()
                context.appendScope(QgsExpressionContextUtils.globalScope())
                context.appendScope(QgsExpressionContextUtils.projectScope(QgsProject.instance()))
                context.appendScope(QgsExpressionContextUtils.layerScope(layer))
                context.appendScope(QgsExpressionContextUtils.mapSettingsScope( self.canvas.mapSettings() ) )
                context.setFeature( feat )
                
                x = QgsExpression(layer.displayExpression())
                x.prepare(context)
                return x.evaluate(context).replace('\n', "<br/>")
        except:
            return ""

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
                # adjust the cursor
                self.canvas.setCursor(QCursor(Qt.WhatsThisCursor))

                # build a list of tuples Name / feature / layer / id for construction of the tool tip, the interface of choice
                if saveFeatures:
                    self.featuresFound = [ {"actionName":QApplication.translate("aeag_search", "Choose...", None), "feature":None, "layer":None, "idxAction":None} ]

                tooltip = []

                for featData in features:
                    feat = featData["feature"]
                    layer = featData["layer"]
                    for action in layer.actions().actions():
                        tip = self._layer_tooltip(layer, feat)
                        
                        try:
                            actionName = '{0} ({1})'.format(action.name(), tip)
                        except:
                            actionName = action.name()

                        if saveFeatures:
                            self.featuresFound.append( {"actionName":"    "+actionName, "feature":feat, "layer":layer, "idxAction":action.id()} )

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
            id = self.featuresFound[1]["idxAction"]
            feature = self.featuresFound[1]["feature"]

            self.doAction(layer, id, feature)

        else:
            # to choose the action to trigger
            canvasPos = self.canvas.mapToGlobal(QPoint(0,0))
            self.chooserDlg = ChooserDlg(self, self.featuresFound, canvasPos.x() + self.__pos.x(), canvasPos.y() + self.__pos.y())
            self.chooserDlg.go()

    def activate(self):
        pass

    def deactivate(self):
        pass

    def doAction(self, layer, uid, feature):
        if layer.actions().action(uid).name() == 'openFeatureForm':
            self.plugin.iface.openFeatureForm(layer, feature)
        else :
            ctxt = QgsExpressionContext()
            ctxt.appendScope(QgsExpressionContextUtils.globalScope())
            ctxt.appendScope(QgsExpressionContextUtils.projectScope(QgsProject.instance()))
            ctxt.appendScope(QgsExpressionContextUtils.mapSettingsScope(self.canvas.mapSettings()))

            # Add click_x and click_y to context
            p = self.toLayerCoordinates(layer, self.pos())            
            QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(), 'click_x', p.x())
            QgsExpressionContextUtils.setProjectVariable(QgsProject.instance(), 'click_y', p.y())

            layer.actions().doAction(uid, feature, ctxt)

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
            if layer.type() == QgsMapLayer.VectorLayer and len(layer.actions().actions()) > 0:
                self.request.setFilterRect(self.toLayerCoordinates(layer, rect))
                for feature in layer.getFeatures(self.request):
                    features.append({"layer":layer, "feature":feature})

        return features
