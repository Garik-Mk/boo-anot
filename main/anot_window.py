import os
import shutil
from functools import partial
import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QIcon, QImage
from main.boo_anot_qt import Ui_ImageViewer
from natsort import natsorted

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def list_files(directory: str, same_folder: bool=False, remove_extensions=False, npy=False) -> dict:
    """
    List files with specified image extensions in the given directory.

    Args:
        directory: The directory path to search for image files.
        same_folder: Are the labels and images in same folder

    Returns:
        A dictionary containing file names as keys and their
        corresponding paths as values.
    """
    dir_dict = {}
    # Add more extensions if needed
    if npy:
        image_extensions = {'.npy'}
    else:
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in image_extensions:
                if same_folder:
                    display_name = file
                else:
                    display_name = os.path.basename(root)\
                    + '__' + file
                if remove_extensions:
                    display_name = os.path.splitext(display_name)[0]
                dir_dict[display_name] = (os.path.join(root, file))
    return dir_dict


def replace_extension_with_txt(file_path: str) -> str:
    """
    Replace the extension of the given file with '.txt'.

    Args:
        file_path: The path of the file whose extension needs to be replaced.

    Returns:
        The file path with the extension replaced by '.txt'.
    """
    base_name, _ = os.path.splitext(file_path)
    return base_name + '.txt'


def magnitude(chirp, radar_data_type='RI'):
    """ Calculate magnitude of a chirp
    
    Args:
        chirp: np.array
            radar data of one chirp (w x h x 2) or (2 x w x h)
        
        radar_data_type: str
            current available types include 'RI', 'RISEP', 'AP', 'APSEP'
    
    Returns:
        Magnitude map for the input chirp (w x h)
    """
    c0, c1, c2 = chirp.shape
    if radar_data_type == 'RI' or radar_data_type == 'RISEP':
        if c0 == 2:
            chirp_abs = np.sqrt(chirp[0, :, :] ** 2 + chirp[1, :, :] ** 2)
        elif c2 == 2:
            chirp_abs = np.sqrt(chirp[:, :, 0] ** 2 + chirp[:, :, 1] ** 2)
        else:
            raise ValueError
    elif radar_data_type == 'AP' or radar_data_type == 'APSEP':
        if c0 == 2:
            chirp_abs = chirp[0, :, :]
        elif c2 == 2:
            chirp_abs = chirp[:, :, 0]
        else:
            raise ValueError
    else:
        raise ValueError
    return chirp_abs


def open_npy_image(npy_file_path):
    """Open given npy file as qpixmap object
    
    Args:
        npy_file_path: str
            Path to the file
    """
    tmp_file = os.path.join(BASE_PATH, "temp.png")
    os.remove(tmp_file)
    numpy_array = np.load(npy_file_path)
    chirp_abs = magnitude(numpy_array)
    plt.imshow(chirp_abs, origin='lower')
    plt.colorbar()
    plt.savefig(tmp_file)
    plt.close()
    newpxmap = QPixmap(tmp_file)
    return newpxmap


class BooWindow(QtWidgets.QMainWindow, Ui_ImageViewer):
    def __init__(self, *args, obj=None, **kwargs):
        super(BooWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        icon = QIcon('logo.png')
        self.setWindowIcon(icon)
        self.data_folder: str
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
                new_file_name = f"{base_name}_{integer}{extension}"
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
            label_file = self.get_label_file_name()
            if os.path.exists(label_file):
                with open(label_file, 'r') as fd:
                    label = fd.read()
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


    def get_label_file_name(self) -> str:
        """Generate label file name from base_directory_name + image_name + .txt"""
        label_file = os.path.join(
            self.label_folder,
            replace_extension_with_txt(self.current_image.text())
        )
        return label_file


    def delete_label(self):
        """Delete the label of the current image."""
        label_file_path = self.get_label_file_name()
        if os.path.isfile(label_file_path):
            os.remove(label_file_path)
        self.open_image(self.current_image)


    def reverse_label_data_folder_state(self) -> None:
        """Reverses state of using same folder for images and labels"""
        self.same_folder = not self.same_folder

    def reverse_npy_data_state(self) -> None:
        """Reverses state of npy files loading flag"""
        self.npy = not self.npy

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
