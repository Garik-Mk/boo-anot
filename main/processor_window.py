from PyQt5 import QtWidgets, QtCore
from main.processor_qt import Ui_processor
from natsort import natsorted

from main.utils import list_files

class ProcessorWindow(QtWidgets.QMainWindow, Ui_processor):
    def __init__(self, *args, obj=None, **kwargs):
        super(ProcessorWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.data_folder = None
        self.images = []
        self.images_per_frame_update()


        self.images_per_frame_spin_box.valueChanged.connect(
            self.images_per_frame_update
        )



    def load_image_in_list(self) -> None:
        """
        Load images from the data folder and populate them in the list widget.
        """
        if self.data_folder is None:
            return
        self.item_list.clear()
        self.file_paths = list_files(self.data_folder)
        self.item_list.addItems(natsorted(self.file_paths.keys()))


    def images_per_frame_update(self):
        new_count = self.images_per_frame_spin_box.value()
        if len(self.images) == new_count:
            return
        if len(self.images) < new_count:
            for new_label_id in range(len(self.images), new_count):
                new_label = QtWidgets.QLabel()
                new_label.setObjectName(f"image_{new_label_id+1}")
                new_label.setText(f"{new_label_id+1}")
                new_label.setAlignment(QtCore.Qt.AlignCenter)
                new_label.setStyleSheet('font: italic 48pt "Consolas";')
                self.imageFrame.addWidget(new_label)
                self.images.append(new_label)
        else:
            while len(self.images) != new_count:
                label = self.images[-1]
                label.deleteLater()
                del self.images[-1]
