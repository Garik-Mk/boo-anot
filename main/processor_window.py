from PyQt5 import QtWidgets, QtCore
from main.processor_qt import Ui_processor
from natsort import natsorted

from main.utils import list_files, ImageWrapper


class ProcessorWindow(QtWidgets.QMainWindow, Ui_processor):
    def __init__(self, *args, obj=None, **kwargs):
        super(ProcessorWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.count = 5
        self.data_folder = None
        self.images = []
        self.images_data = {}
        self.base_poses = {}
        self.selected_label = None

        self.images_per_frame_update()
        self.set_images_poses()


        self.images_per_frame_spin_box.valueChanged.connect(
            self.images_per_frame_update
        )
        self.currentX.valueChanged.connect(
            self.apply_x_offset
        )
        self.currentY.valueChanged.connect(
            self.apply_y_offset
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


    def images_per_frame_update(self) -> None:
        """
        Create empty labels for new pixmaps to be loaded
        """
        new_count = self.images_per_frame_spin_box.value()
        count_current = len(self.images)
        if count_current == new_count:
            return
        if count_current < new_count:
            for new_label_id in range(count_current, new_count):
                new_label = QtWidgets.QLabel(self.imageFrame)
                new_label.setObjectName(f"image_{new_label_id+1}")
                new_label.setText(f"{new_label_id+1}")
                new_label.setStyleSheet('font: italic 30pt "Consolas";')
                new_label.mousePressEvent = lambda event, l=new_label: self.on_label_clicked(l)
                self.images.append(new_label)
                self.images_data[new_label] = ImageWrapper(new_label)
                new_label.show()
        else:
            while len(self.images) != new_count:
                label = self.images[-1]
                del self.base_poses[label]
                label.deleteLater()
                del self.images[-1]
        self.count = new_count
        self.set_images_poses()
        self.apply_data()


    def set_images_poses(self):
        for i, label in enumerate(self.images):
            x_step = 1 / self.count
            pos = self.move_label_percent(label, i*x_step, 0.5)
            self.base_poses[label] = pos


    def move_label_percent(self, label: QtWidgets.QLabel, x_percent, y_percent) -> tuple[int]:
        x_pixel = int(x_percent * self.imageFrame.width())
        y_pixel = int(y_percent * self.imageFrame.height())
        label.move(x_pixel, y_pixel)
        return (x_pixel, y_pixel)            


    def on_label_clicked(self, label: QtWidgets.QLabel) -> None:
        """Outline clicked label and load it's data to ui"""
        if self.selected_label:
            self.selected_label.setStyleSheet('border: none; font: italic 30pt "Consolas";')
        self.selected_label = label
        self.selected_label.setStyleSheet('border: 2px solid red; font: italic 30pt "Consolas";')
        self.currentX.setValue(self.images_data[self.selected_label].x)
        self.currentY.setValue(self.images_data[self.selected_label].y)


    def apply_x_offset(self) -> None:
        """Apply x axis offset to selected image in the frame"""
        self.images_data[self.selected_label].x = self.currentX.value()
        self.apply_data()


    def apply_y_offset(self) -> None:
        """Apply x axis offset to selected image in the frame"""
        self.images_data[self.selected_label].y = self.currentY.value()
        self.apply_data()


    def apply_data(self) -> None:
        """Load data to ui and move label to their positions"""
        for label in self.images:
            current_pos = self.base_poses[label]
            new_pos = QtCore.QPoint(
                self.images_data[label].x + current_pos[0],
                self.images_data[label].y + current_pos[1]
            )
            if (new_pos.x() < 0 or new_pos.y() < 0) or\
            (new_pos.x() > self.imageFrame.size().width() or
                new_pos.y() > self.imageFrame.size().height()):
                return
            label.move(new_pos)
