import os
from functools import partial
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QIcon
from ui.boo_anot_qt import Ui_ImageViewer



def list_files(directory: str) -> dict:
    """
    List files with specified image extensions in the given directory.

    Args:
        directory: The directory path to search for image files.

    Returns:
        A dictionary containing file names as keys and their corresponding paths as values.
    """
    dir_dict = {}
    # Add more extensions if needed
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}  
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
        self.current_image = None

        self.actionOpen_Folder.triggered.connect(
            partial(self.open_file_selection_dialog, data=True)
        )
        self.actionOpen_Labels_Folder.triggered.connect(
            partial(self.open_file_selection_dialog, data=False)
        )

        self.item_list.itemDoubleClicked.connect(self.open_image)
        self.search.textChanged.connect(self.search_and_scroll)

        self.next_image.clicked.connect(partial(self.open_next_image, 1))
        self.prev_image.clicked.connect(partial(self.open_next_image, -1))

        self.setFocusPolicy(Qt.StrongFocus)


    @pyqtSlot()
    def open_file_selection_dialog(self, data: bool) -> None:
        """
        Open a file selection dialog to choose the data or labels folder.

        Args:
            data: If True, selects the data folder; otherwise, selects the labels folder.
        """
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
        """
        Load images from the data folder and populate them in the list widget.
        """
        self.file_paths = list_files(self.data_folder)
        self.item_list.addItems(self.file_paths.keys())


    def open_image(self, item):
        """
        Open the selected image and display it in the image label.

        Args:
            item: The QListWidgetItem representing the selected image.
        """
        image_path = self.file_paths[item.text()]
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(), aspectRatioMode=Qt.KeepAspectRatio
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.current_image = item
        else:
            self.image_label.setText("Failed to load image")


    def open_next_image(self, step=1):
        """
        Open the next or previous image based on the step value.

        Args:
            step: An integer indicating the step size for navigating through images.
        """
        current = self.item_list.currentItem()
        idx = self.item_list.indexFromItem(current)
        row = idx.row()
        next_index = self.item_list.model().index(row + step, 0)
        next_item = self.item_list.itemFromIndex(next_index)
        if next_item:
            self.item_list.setCurrentItem(next_item)
            self.open_image(next_item)


    def search_and_scroll(self):
        """
        Search for images in the list widget based on the text entered in the search box and scroll to the first match.
        """
        items = self.item_list.findItems(
            self.search.text(), Qt.MatchContains
        )
        if items:
            item = items[0]
            self.item_list.setCurrentItem(item)
            self.item_list.scrollToItem(item)


    def keyPressEvent(self, event):
        """
        Handle key press events.

        If the pressed key is 1, 2, 3, or 4, call the set_label method.
        Otherwise, call the base behavior of keyPressEvent.

        Args:
            event: The key press event.
        """
        key = event.key()
        if key in (Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4):
            self.set_label(key - Qt.Key_0)
        else:
            super().keyPressEvent(event)


    def set_label(self, label_id):
        """
        Set a label for the current image.

        Args:
            label_id: An integer representing the label ID.
        """
        if self.current_image is None:
            print('No image given')
            return
        print(
            f'{self.file_paths[self.current_image.text()]} - {label_id}'
        )
        self.open_next_image()
