import os
from functools import partial
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QIcon
from ui.boo_anot_qt import Ui_ImageViewer



def list_files(directory: str) -> dict:
    dir_dict = {}
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}  # Add more extensions if needed
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in image_extensions:
                dir_dict[file] = (os.path.join(root, file))
    return dir_dict


class BooWindow(QtWidgets.QMainWindow, Ui_ImageViewer):
    def __init__(self, *args, obj=None, **kwargs):
        super(BooWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        icon = QIcon('logo.png')
        self.setWindowIcon(icon)
        self.data_folder: str
        self.label_folder: str

        self.file_paths: dict
        self.current_image: QtWidgets.QListWidgetItem

        self.actionOpen_Folder.triggered.connect(partial(self.open_file_selection_dialog, data=True))
        self.actionOpen_Labels_Folder.triggered.connect(partial(self.open_file_selection_dialog, data=False))

        self.item_list.itemDoubleClicked.connect(self.open_image)
        self.search.textChanged.connect(self.search_and_scroll)

        self.next_image.clicked.connect(partial(self.open_next_image, 1))
        self.prev_image.clicked.connect(partial(self.open_next_image, -1))


    @pyqtSlot()
    def open_file_selection_dialog(self, data: bool) -> None:
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Open File",
            "${HOME}"
        )
        if data:
            self.data_folder = fname
            self.load_image_in_list()
        else:
            self.label_folder = fname


    def load_image_in_list(self) -> None:
        self.file_paths = list_files(self.data_folder)
        self.item_list.addItems(self.file_paths.keys())


    def open_image(self, item):
        image_path = self.file_paths[item.text()]
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(self.image_label.size(), aspectRatioMode=Qt.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)
            self.current_image = item
        else:
            self.image_label.setText("Failed to load image")


    def open_next_image(self, step=1):
        current = self.item_list.currentItem()
        idx = self.item_list.indexFromItem(current)
        row = idx.row()
        next_index = self.item_list.model().index(row + step, 0)
        next_item = self.item_list.itemFromIndex(next_index)
        if next_item:
            self.item_list.setCurrentItem(next_item)
            self.open_image(next_item)


    def search_and_scroll(self):
        items = self.item_list.findItems(self.search.text(), Qt.MatchContains)
        if items:
            item = items[0]
            self.item_list.setCurrentItem(item)
            self.item_list.scrollToItem(item)