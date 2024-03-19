
from functools import partial
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from ui.boo_anot_qt import Ui_ImageViewer


class BooWindow(QtWidgets.QMainWindow, Ui_ImageViewer):
    def __init__(self, *args, obj=None, **kwargs):
        super(BooWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.data_folder = ''
        self.label_folder = ''
        self.actionOpen_Folder.triggered.connect(partial(self.open_file_selection_dialog, data=True))
        self.actionOpen_Labels_Folder.triggered.connect(partial(self.open_file_selection_dialog, data=False))


    @pyqtSlot()
    def open_file_selection_dialog(self, data):
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Open File",
            "${HOME}"
        )
        if data:
            self.data_folder = fname
        else:
            self.label_folder = fname
        