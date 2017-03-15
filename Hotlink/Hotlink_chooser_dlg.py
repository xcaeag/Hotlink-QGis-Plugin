from .ui_Hotlink_chooser_dlg import Ui_Dialog
from PyQt5.QtWidgets import QDialog

class ChooserDlg(QDialog, Ui_Dialog):
    """GUI allows the user to choose the action to be triggered (if any)
    """

    def __init__(self, tool, featuresFound, x, y):
        """GUI Initialization 
        
        @param tool HotlinkMT object
        @param featuresFound An array of actions to be proposed
        @param x List position (s)
        @param y List position (y)
        """
        
        QDialog.__init__(self, None)
        self.setupUi(self)

        self.tool = tool
        self.featuresFound = featuresFound

        self.populateActions()
        self.x = x
        self.y = y

        self.comboBox.currentIndexChanged.connect(self.onChoose)

    def populateActions(self):
        """Populate 
        """
        self.comboBox.clear()
        for tab in self.featuresFound:
            self.comboBox.addItem(tab["actionName"], tab)

    def onChoose(self):
        """Triggered by the choice of an action from the list
        """
        self.tool.onChoose(self.comboBox.currentIndex());
        
    def go(self):
        self.comboBox.move(self.x, self.y)
        self.comboBox.showPopup()