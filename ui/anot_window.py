
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from ui.boo_anot_qt import Ui_ImageViewer


class BooWindow(QtWidgets.QMainWindow, Ui_ImageViewer):
    def __init__(self, *args, obj=None, **kwargs):
        super(BooWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
    
    @pyqtSlot()
    def open_file_selection_dialog(self):
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Open File",
            "${HOME}"
        )
        return fname