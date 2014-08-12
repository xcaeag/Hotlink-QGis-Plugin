"""@package HotlinkMT
"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import re

from Hotlink_chooser_dlg import ChooserDlg

_fromUtf8 = lambda s: (s.decode("utf-8").encode("latin-1")) if s else s
_toUtf8 = lambda s: s.decode("latin-1").encode("utf-8") if s else s
    
class HotlinkMT(QgsMapTool):
    """Hotlink tool. It is this class that manages the mouse capture...
    """

    def __init__(self, plugin):
        """Tool initialization 
        """
        
        QgsMapTool.__init__(self, plugin.canvas)

        # specifics initializations
        self.plugin = plugin
        self.featuresFound = {}
        self.ixFeature = 0
        self.__pos = None
        self.chooserDlg = None

    def canvasPressEvent(self,event):
        pass

    def findUnderlyingObjects(self, event):
        """On mouse movement, we identify the underlying objects
        """
        
        if not self.plugin.active:
            return
        
        try:
            self.__pos = event.pos()
            
            # find objects
            features = self.__getFeatures()
    
            # if there are
            if (len(features) > 0):
                # adjust the cursor
                self.plugin.canvas.setCursor(QCursor(Qt.WhatsThisCursor))
    
                # build a list of tuples Name / feature / layer / id for construction of the tool tip, the interface of choice
                self.featuresFound = {}
                self.featuresFound[0] =  {"actionName":QtGui.QApplication.translate("aeag_search", "Choose...", None, QtGui.QApplication.UnicodeUTF8), "feature":None, "layer":None, "idxAction":None}
                idx = 1
                tooltip = ""
                for pk,featData in features.iteritems():
                    feat = featData["feature"]
                    layer = featData["layer"]
                    idxAction = 0
                    while idxAction < layer.actions().size():
                        action = layer.actions()[idxAction]
                        try:
                            if layer.displayField() and feat.attribute(layer.displayField()):
                                actionName = action.name() + " (" + feat.attribute(layer.displayField())+")"
                            else:
                                actionName = action.name()
                        except:
                            actionName = action.name()
                            
                        self.featuresFound[idx] =  {"actionName":"    "+actionName, "feature":feat, "layer":layer, "idxAction":idxAction}
                            
                        idxAction += 1
                        idx += 1
    
                    # tool tip
                    if tooltip != "":
                        tooltip += "\n"

                    try:
                        if layer.displayField() and feat.attribute(layer.displayField()):
                            tooltip += layer.name() + " - " + feat.attribute(layer.displayField())
                        else:
                            tooltip += layer.name() 
                    except:
                        tooltip += layer.name() 
    
                # display
                self.plugin.canvas.setToolTip(tooltip)
    
            else:
                # without objects, restore the cursor ...
                self.featuresFound = {}
                self.plugin.canvas.setCursor(QCursor(Qt.ArrowCursor))
                self.plugin.canvas.setToolTip("")
        except:
            pass

    def canvasMoveEvent(self,event):
        """On mouse movement, we identify the underlying objects
        """
        self.findUnderlyingObjects(event)
            
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

        self.findUnderlyingObjects(event)

        # if a single action (2 lines in the list)
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
        layer.actions().doActionFeature(idx, feature)
        
    def onChoose(self, idx):
        """Do action
        """
        tab = self.featuresFound[idx]
        layer = tab["layer"]
        self.doAction(layer, tab["idxAction"], tab["feature"])

    def __getFeatures(self):
        """Identify objects under the mouse, having actions
        """
        features = {}
        
        transform = self.plugin.canvas.getCoordinateTransform()
        ll = transform.toMapCoordinates( self.__pos.x()-4, self.__pos.y()+4 )
        ur = transform.toMapCoordinates( self.__pos.x()+4, self.__pos.y()-4)
        selectRect =  QgsRectangle (ll.x(), ll.y(), ur.x(), ur.y())
        rectGeom = QgsGeometry.fromRect(selectRect)

        idx = 0
        for layer in self.plugin.canvas.layers():
            # treat only vector layers having actions
            if layer.type() == QgsMapLayer.VectorLayer and layer.actions().size() > 0:
                provider = layer.dataProvider()
                allAttrs = provider.attributeIndexes()
                
                # selection (bbox intersections)
                request = QgsFeatureRequest().setFilterRect(selectRect)
                for feature in layer.getFeatures(request):
                    if feature.geometry().intersects(rectGeom):
                        features[idx] = {"layer":layer, "feature":feature}
                        idx += 1
            
        return features