import os
import shutil
from functools import partial
from natsort import natsorted

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QIcon

from main.boo_anot_qt import Ui_ImageViewer
from main.processor_window import ProcessorWindow
from main.utils import list_files, open_npy_image, replace_extension_with_txt, BASE_CLASS_MAPPING

MAIN_BASE_PATH = os.path.dirname(os.path.abspath(__file__))


class BooWindow(QtWidgets.QMainWindow, Ui_ImageViewer):
    def __init__(self, *args, obj=None, **kwargs):
        super(BooWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        icon = QIcon('logo.png')
        self.setWindowIcon(icon)
        self.data_folder = None
        self.label_folder = None

        self.file_paths: dict
        self.current_image = None
        self.same_folder = False
        self.npy = False

        self.actionOpen_Data_Folder.triggered.connect(
            partial(self.open_file_selection_dialog, data=True)
        )
        self.actionOpen_Label_Folder.triggered.connect(
            partial(self.open_file_selection_dialog, data=False)
        )
        self.actionSame_Data_and_Label_Folder.triggered.connect(
            self.reverse_label_data_folder_state
        )
        self.actionOpen_NPY_files.triggered.connect(
            self.reverse_npy_data_state
        )
        self.actionMove_images_to_labels.triggered.connect(
            self.move_images_to_labels
        )
        self.actionAdd_number_to_each_filename_end.triggered.connect(
            self.add_integer_to_filenames
        )
        self.actionOpen_Data_Processor.triggered.connect(
            self.open_data_processor
        )
        self.actionAdd_Label_To_Filename.triggered.connect(
            self.add_labels_to_filenames
        )

        self.item_list.itemDoubleClicked.connect(self.open_image)
        self.search.textChanged.connect(self.search_and_scroll)

        self.next_image_btn.clicked.connect(partial(self.open_next_image, 1))
        self.prev_image_btn.clicked.connect(partial(self.open_next_image, -1))
        self.delete_label_btn.clicked.connect(self.delete_label)

        self.menuBar.setNativeMenuBar(False)

        self.setFocusPolicy(Qt.StrongFocus)


    def add_integer_to_filenames(self):
        """
        Traverse through whole directory, add to each file name
        an underscore and given integer

        Args:
            directory: The directory path
        """
        integer, ok_pressed = QtWidgets.QInputDialog.getInt(None, "Enter Integer", "Please enter an integer:", value=0)
        for root, dirs, files in os.walk(self.data_folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                base_name, extension = os.path.splitext(file_name)
                new_file_name = f"{integer}__{base_name}{extension}"
                os.rename(file_path, os.path.join(root, new_file_name))
                print(f"Renamed '{file_name}' to '{new_file_name}'")
        self.load_image_in_list()


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
        self.item_list.clear()
        self.file_paths = list_files(self.data_folder, self.same_folder, npy=self.npy)
        self.item_list.addItems(natsorted(self.file_paths.keys()))


    def get_label(self, item: QtWidgets.QListWidgetItem=None):
        """
        Retrieve the label associated with a given item.

        Args:
            item: The item for which to retrieve the label.

        Returns str:
            The label corresponding to the provided item, or None if the label file does not exist.
        """
        label_file = self.get_label_file_name(item)
        if os.path.exists(label_file):
            with open(label_file, 'r') as fd:
                return fd.read()
        return None


    def add_labels_to_filenames(self):
        """
        Add labels to filenames based on a predefined mapping and rename the files accordingly.
        """
        for item in self.iter_over_item_list():
            label = self.get_label(item)
            if label in BASE_CLASS_MAPPING:
                label_name = BASE_CLASS_MAPPING[label]
            else:
                print('Error found in data: ', label)
                continue
            base_name = item.text()
            label_file_name = replace_extension_with_txt(base_name)
            new_filename = f'{label_name}__{base_name}'
            new_label_file_name = f'{label_name}__{label_file_name}'
            os.rename(
                os.path.join(self.data_folder, base_name),
                os.path.join(self.data_folder, new_filename)
            )
            os.rename(
                os.path.join(self.label_folder, label_file_name),
                os.path.join(self.label_folder, new_label_file_name)
            )
        self.load_image_in_list()


    def iter_over_item_list(self):
        """
        Iterate over the item list.

        Yields:
            Each item in the item list.
        """
        for i in range(self.item_list.count()):
            yield self.item_list.item(i)


    def open_image(self, item):
        """
        Open the selected image and display it in the image label.

        Args:
            item: The QListWidgetItem representing the selected image.
        """
        if self.label_folder is None:
            self.label_folder = self.data_folder
        image_path = self.file_paths[item.text()]
        if self.npy:
            temp_pixmap = open_npy_image(image_path)
        else:
            temp_pixmap = QPixmap(image_path)
        if not temp_pixmap.isNull():
            self.pixmap = temp_pixmap.scaled(
                self.image_label.size(), aspectRatioMode=Qt.KeepAspectRatio
            )
            self.image_label.setPixmap(self.pixmap)
            self.current_image = item
            label = self.get_label()
            if label is not None:
                self.current_label.setText(f'Current label - #{label}')
            else:
                self.current_label.setText('None')
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
        Search for images in the list widget based on the text entered in the
        search box and scroll to the first match.
        """
        items = self.item_list.findItems(
            self.search.text(), Qt.MatchStartsWith
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
        Also, keyboard arrows can switch loaded images.

        Args:
            event: The key press event.
        """
        key = event.key()
        if key in (Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5):
            self.set_label(str(key - Qt.Key_0))
        elif event.key() == Qt.Key_Left:
            self.open_next_image(-1)
        elif event.key() == Qt.Key_Right:
            self.open_next_image()
        else:
            super().keyPressEvent(event)


    def set_label(self, label_id: str):
        """
        Set a label for the current image.

        Args:
            label_id: A str representing the label ID.
        """
        image_full_path = self.file_paths[self.current_image.text()]
        label_file = self.get_label_file_name()
        if self.current_image is None:
            print('No image given')
            return
        try:
            with open(label_file, 'w') as file:
                file.write(label_id)
            print(f'# Labeled {image_full_path} --- {label_id}')
            self.open_next_image()
        except Exception as e:
            print(f"Error occurred while creating text file: {e}")


    def get_label_file_name(self, item=None) -> str:
        """Generate label file name from base_directory_name + image_name + .txt"""
        if item is None:
            item = self.current_image
        label_file = os.path.join(
            self.label_folder,
            replace_extension_with_txt(item.text())
        )
        return label_file


    def delete_label(self):
        """Delete the label of the current image."""
        try:
            label_file_path = self.get_label_file_name()
            if os.path.isfile(label_file_path):
                os.remove(label_file_path)
            self.open_image(self.current_image)
        except:
            pass


    def reverse_label_data_folder_state(self) -> None:
        """Reverses state of using same folder for images and labels"""
        self.same_folder = not self.same_folder

    def reverse_npy_data_state(self) -> None:
        """Reverses state of npy files loading flag"""
        self.npy = not self.npy


    def open_data_processor(self) -> None:
        """Open data processor window"""
        self.data_processor = ProcessorWindow()
        self.data_processor.show()
        self.data_processor.data_folder = self.data_folder
        self.data_processor.load_image_in_list()


    def move_images_to_labels(self) -> None:
        """Iterate from label files in label_folder and move corresponding images to that directory"""
        if self.same_folder:
            print('You need to specify different paths for data and labels')
            return
        if self.label_folder is None:
            print('No labels found')
            return
        label_folder_content = os.listdir(self.label_folder)
        label_files = []
        for file_name in label_folder_content:
            if file_name.endswith('.txt'):
                label_files.append(file_name)
        reply = QtWidgets.QMessageBox.question(None,
            'File transfer',
            f'Do you want to move {len(label_files)} images to {self.label_folder}?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )
        if reply == QtWidgets.QMessageBox.No:
            return
        image_data = list_files(
            self.data_folder,
            self.same_folder,
            remove_extensions=True,
            npy=self.npy
        )
        for file_name in label_files:
            file_base_name = os.path.splitext(file_name)[0]
            if file_base_name in image_data:
                current_path = image_data[file_base_name]
                ext = os.path.splitext(current_path)[1]
                new_path = os.path.join(self.label_folder, f'{file_base_name}{ext}')
                print(f'{current_path} >>> {new_path}')
                shutil.copy(current_path, new_path)
