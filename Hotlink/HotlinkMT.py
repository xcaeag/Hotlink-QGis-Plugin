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
        self.plugin = plugin
        self.featuresFound = []
        self.ixFeature = 0
        self.__pos = None
        self.chooserDlg = None
        self.request = QgsFeatureRequest()
        self.request.setFlags(QgsFeatureRequest.Flags(QgsFeatureRequest.NoGeometry | QgsFeatureRequest.ExactIntersect))
        
    def canvasPressEvent(self, event):
        pass

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
                self.plugin.canvas.setCursor(QCursor(Qt.WhatsThisCursor))

                # build a list of tuples Name / feature / layer / id for construction of the tool tip, the interface of choice
                if saveFeatures:
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
                            self.featuresFound.append( {"actionName":"    "+actionName, "feature":feat, "layer":layer, "idxAction":idxAction} )
                            
                    try:
                        if layer.displayField() and feat.attribute(layer.displayField()):
                            tooltip.append(layer.name() + " - " + feat.attribute(layer.displayField()))
                        else:
                            tooltip.append(layer.name())
                    except:
                        tooltip.append(layer.name())

                # display
                self.plugin.canvas.setToolTip('\n'.join(tooltip))

            else:
                # without objects, restore the cursor ...
                if saveFeatures:
                    self.featuresFound = []
                    
                self.plugin.canvas.setCursor(QCursor(Qt.ArrowCursor))
                self.plugin.canvas.setToolTip("")
        except:
            pass

    def canvasMoveEvent(self,event):
        """On mouse movement, we identify the underlying objects
        """
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
        #QgsMessageLog.logMessage("Nb "+str(len(self.featuresFound)), 'Extensions')
        
        if len(self.featuresFound) == 2:
            layer = self.featuresFound[1]["layer"]
            idx = self.featuresFound[1]["idxAction"]
            feature = self.featuresFound[1]["feature"]
            
            self.doAction(layer, idx, feature)
            
        else:
            # to choose the action to trigger
            canvasPos = self.plugin.canvas.mapToGlobal(QPoint(0,0))
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
            layer.actions().doActionFeature(idx, feature)
        
    def onChoose(self, idx):
        """Do action
        """
        tab = self.featuresFound[idx]
        self.doAction(tab["layer"], tab["idxAction"], tab["feature"])

    def _getFeatures(self):
        """Identify objects under the mouse, having actions
        """
        features = []
        
        transform = self.plugin.canvas.getCoordinateTransform()
        ll = transform.toMapCoordinates( self.__pos.x()-3, self.__pos.y()+3 )
        ur = transform.toMapCoordinates( self.__pos.x()+3, self.__pos.y()-3)
        selectRect =  QgsRectangle (ll.x(), ll.y(), ur.x(), ur.y())
        rectGeom = QgsGeometry.fromRect(selectRect)

        for layer in self.plugin.canvas.layers():
            # treat only vector layers having actions
            if layer.type() == QgsMapLayer.VectorLayer and layer.actions().size() > 0:                
                # selection (bbox intersections)
                self.request.setFilterRect(selectRect)
                for feature in layer.getFeatures(self.request):
                    features.append({"layer":layer, "feature":feature})
            
        return features