"""@package HotlinkMT
"""

from qgis.PyQt.QtCore import Qt, QPoint
from qgis.PyQt.QtGui import QCursor

from qgis.core import (
    QgsFeatureRequest,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsProject,
    QgsExpression,
    QgsRectangle,
    QgsMapLayer
)

from qgis.gui import QgsMapTool

from .ui.Hotlink_chooser_dlg import ChooserDlg


class HotlinkMT(QgsMapTool):
    """Hotlink tool. It is this class that manages the mouse capture..."""

    def __init__(self, plugin):
        """Tool initialization"""
        QgsMapTool.__init__(self, plugin.canvas)

        self.canvas = plugin.canvas
        self.plugin = plugin
        self.featuresFound = []
        self.ixFeature = 0
        self.__pos = None
        self.chooserDlg = None
        self.request = QgsFeatureRequest()
        self.request.setFlags(
            QgsFeatureRequest.Flags(
                QgsFeatureRequest.Flag.NoGeometry | QgsFeatureRequest.Flag.ExactIntersect
            )
        )

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
                return str(feat.attribute(df))
            else:
                context = QgsExpressionContext()
                context.appendScope(QgsExpressionContextUtils.globalScope())
                context.appendScope(
                    QgsExpressionContextUtils.projectScope(QgsProject.instance())
                )
                context.appendScope(QgsExpressionContextUtils.layerScope(layer))
                context.appendScope(
                    QgsExpressionContextUtils.mapSettingsScope(
                        self.canvas.mapSettings()
                    )
                )
                context.setFeature(feat)

                x = QgsExpression(layer.displayExpression())
                x.prepare(context)
                return x.evaluate(context).replace("\n", "<br/>")
        except:
            return ""

    def findUnderlyingObjects(self, event, saveFeatures):
        """On mouse movement, we identify the underlying objects"""

        if not self.plugin.active:
            return

        try:
            # find objects
            features = self._getFeatures()

            # if there are
            if features:
                # adjust the cursor
                self.canvas.setCursor(QCursor(Qt.CursorShape.WhatsThisCursor))

                # build a list of tuples Name / feature / layer / id for construction of the tool tip, the interface of choice
                if saveFeatures:
                    self.featuresFound = []

                tooltip = []

                for featData in features:
                    feat = featData["feature"]
                    layer = featData["layer"]
                    for action in layer.actions().actions():
                        tip = self._layer_tooltip(layer, feat)

                        try:
                            actionName = "{0} {1}".format(
                                action.shortTitle() or action.name(), tip
                            )
                        except:
                            actionName = action.name()

                        if saveFeatures:
                            self.featuresFound.append(
                                {
                                    "actionName": "" + actionName,
                                    "feature": feat,
                                    "layer": layer,
                                    "idxAction": action.id(),
                                    "icon": action.iconPath()
                                }
                            )

                        try:
                            tooltip.index(tip)
                        except:
                            tooltip.append(tip)

                # display
                if self.plugin.optionShowTips:
                    self.canvas.setToolTip("<p>" + "<br/>".join(tooltip) + "</p>")

            else:
                # without objects, restore the cursor ...
                if saveFeatures:
                    self.featuresFound = []

                self.canvas.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
                if self.plugin.optionShowTips:
                    self.canvas.setToolTip("")
        except:
            pass

    def canvasMoveEvent(self, event):
        """On mouse movement, we identify the underlying objects"""
        if self.plugin.optionShowTips:
            self.findUnderlyingObjects(event, False)

    def canvasReleaseEvent(self, event):
        """On click, do action"""
        if not self.plugin.active:
            return

        # left click only
        if event.button() not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            return

        self.__pos = event.pos()

        # Add click_x and click_y to context
        if self.pos():
            QgsExpressionContextUtils.setProjectVariable(
                QgsProject.instance(), "click_x", self.pos().x()
            )
            QgsExpressionContextUtils.setProjectVariable(
                QgsProject.instance(), "click_y", self.pos().y()
            )

        self.findUnderlyingObjects(event, True)

        # if a single action (2 lines in the list)
        if len(self.featuresFound) == 1:
            layer = self.featuresFound[0]["layer"]
            id = self.featuresFound[0]["idxAction"]
            feature = self.featuresFound[0]["feature"]

            self.doAction(layer, id, feature)

        else:
            # to choose the action to trigger
            canvasPos = self.canvas.mapToGlobal(QPoint(0, 0))
            self.chooserDlg = ChooserDlg(
                self,
                self.featuresFound,
                canvasPos.x() + self.__pos.x(),
                canvasPos.y() + self.__pos.y(),
            )
            self.chooserDlg.go()

    def activate(self):
        pass

    def deactivate(self):
        pass

    def doAction(self, layer, uid, feature):
        if layer.actions().action(uid).name() == "openFeatureForm":
            self.plugin.iface.openFeatureForm(layer, feature)
        else:
            ctxt = QgsExpressionContext()
            ctxt.appendScope(QgsExpressionContextUtils.globalScope())
            ctxt.appendScope(
                QgsExpressionContextUtils.projectScope(QgsProject.instance())
            )
            ctxt.appendScope(
                QgsExpressionContextUtils.mapSettingsScope(self.canvas.mapSettings())
            )

            layer.actions().doAction(uid, feature, ctxt)

    def onChoose(self, idx):
        """Do action"""
        tab = self.featuresFound[idx]
        self.doAction(tab["layer"], tab["idxAction"], tab["feature"])

    def _getFeatures(self):
        """Identify objects under the mouse, having actions"""
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
            if (
                layer.type() == QgsMapLayer.LayerType.VectorLayer
                and len(layer.actions().actions()) > 0
            ):
                layerRect = self.toLayerCoordinates(layer, rect)
                self.request.setFilterRect(layerRect)

                for feature in layer.getFeatures(
                    layerRect if (layer.dataProvider().name() == "WFS") else self.request
                ):
                    features.append({"layer": layer, "feature": feature})

        return features
