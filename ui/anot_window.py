
from PyQt5 import QtWidgets
from ui.boo_anot_qt import Ui_ImageViewer


class BooWindow(QtWidgets.QMainWindow, Ui_ImageViewer):
    def __init__(self, *args, obj=None, **kwargs):
        super(BooWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)