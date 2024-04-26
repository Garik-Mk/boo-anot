from PyQt5 import QtWidgets, QtCore, QtGui
from main.processor_qt import Ui_processor
from natsort import natsorted
from functools import partial

from main.utils import list_files, ImageWrapper


class ProcessorWindow(QtWidgets.QMainWindow, Ui_processor):
    def __init__(self, *args, obj=None, **kwargs):
        super(ProcessorWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.data_folder = None
        self.data: list
        self.images = []
        self.images_data = {}
        self.base_poses = {}
        self.selected_label = None
        self.images_loaded = False
        self.filler_image_path = None

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
        self.actionOpen_Data.triggered.connect(
            self.open_folder_selection_dialog
        )
        self.filler_image.clicked.connect(
            self.open_file_selection_dialog
        )

        self.item_list.itemDoubleClicked.connect(self.open_image_sequence)
        self.boundingbox.setStyleSheet('border: 2px solid blue;')
        self.get_current_bounding_box()
        self.boundingbox.show()


    @QtCore.pyqtSlot()
    def open_folder_selection_dialog(self) -> None:
        """
        Open a file selection dialog to choose the data folder.
        """
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Open File",
            "${HOME}"
        )
        if fname:
            self.data_folder = fname
            self.load_image_in_list()


    def open_file_selection_dialog(self) -> None:
        """
        Open a file selection dialog to choose a single file.
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            "${HOME}",
            "All Files (*);;Text Files (*.txt)",  # Adjust file filter as needed
            options=options
        )
        if fname:
            self.filler_image_path = fname

    def mousePressEvent(self, event):
        if event.widget() == self.line_edit:
            print("Line edit clicked")
        super().mousePressEvent(event)


    def load_image_in_list(self) -> None:
        """
        Load images from the data folder and populate them in the list widget.
        """
        if self.data_folder is None:
            return
        self.item_list.clear()
        self.file_paths = list_files(self.data_folder)
        self.data = natsorted(self.file_paths.keys())
        self.item_list.addItems(self.data)


    def open_image_sequence(self, item):
        start_ind = self.data.index(item.text())
        items_list = []
        for i in range(start_ind, start_ind + len(self.images)):
            items_list.append(self.file_paths[self.data[i]])
        for i, image_path in enumerate(items_list):
            temp_pixmap = QtGui.QPixmap(image_path)
            if not temp_pixmap.isNull():
                self.images[i].setPixmap(temp_pixmap)
        self.images_loaded=True
        self.update_sizes_and_bases()


    def update_sizes_and_bases(self, downscale=1):
        if not self.images_loaded:
            return
        image_frame_h = self.imageFrame.size().height()
        for i, label in enumerate(self.images):
            if not label.pixmap():
                continue
            old_base = self.base_poses[label]
            each_image_w = int(
                (self.imageFrame.size().width() / len(self.images)) * downscale
            )
            resized_pixmap = label.pixmap().scaledToWidth(each_image_w)
            each_image_h = resized_pixmap.size().height()

            if (image_frame_h - each_image_h) < 0:
                resized_pixmap = resized_pixmap.scaledToHeight(image_frame_h * downscale)
                each_image_h = resized_pixmap.size().height()
            
            offset = len(self.images) * resized_pixmap.size().width()
            offset -= self.imageFrame.size().width()
            offset = abs(offset)
            offset /= self.imageFrame.size().width()
            offset /= 2
            if offset > 0.015:
                new_x = int(offset + (i + 1) * resized_pixmap.size().width())
            else:
                new_x = old_base[0]

            label.setFixedSize(resized_pixmap.size())
            new_base = (new_x, (image_frame_h - each_image_h) // 2)
            self.base_poses[label] = new_base
            label.setPixmap(resized_pixmap)
        self.apply_data()


    def get_current_bounding_box(self):
        x_list = []
        y_list = []
        for label in self.images:
            x_list.append(label.pos().x())
            y_list.append(label.pos().y())
        upper_left_x = min(x_list)
        upper_left_y = min(y_list)
        lower_right_x = max(x_list) + self.images[0].size().width()
        lower_right_y = max(y_list) + self.images[0].size().height()
        width = lower_right_x - upper_left_x
        height = lower_right_y - upper_left_y

        self.boundingbox.setGeometry(QtCore.QRect(upper_left_x, upper_left_y, width, height))



    def resizeEvent(self, event):
        """Override resizeEvent to handle window resize events"""
        super().resizeEvent(event)
        self.set_images_poses()
        self.update_sizes_and_bases()


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
                # new_label.mousePressEvent = lambda event, l=new_label: self.on_label_clicked(l)
                new_label.mousePressEvent = partial(self.on_label_clicked, new_label)
                self.images.append(new_label)
                self.images_data[new_label] = ImageWrapper(new_label)
                new_label.show()
        else:
            while len(self.images) != new_count:
                label = self.images[-1]
                del self.base_poses[label]
                label.hide()
                del self.images[-1]
        self.set_images_poses()
        self.update_sizes_and_bases()


    def set_images_poses(self):
        for i, label in enumerate(self.images):
            x_step = 1 / len(self.images)
            pos = self.move_label_percent(label, i*x_step, 0.5)
            self.base_poses[label] = pos
        self.apply_data()


    def move_label_percent(self, label: QtWidgets.QLabel, x_percent, y_percent) -> tuple[int]:
        x_pixel = int(x_percent * self.imageFrame.width())
        y_pixel = int(y_percent * self.imageFrame.height())
        label.move(x_pixel, y_pixel)
        return (x_pixel, y_pixel)


    def on_label_clicked(self, label: QtWidgets.QLabel, *args) -> None:
        """Outline clicked label and load it's data to ui"""
        if self.selected_label:
            self.selected_label.setStyleSheet('border: none; font: italic 30pt "Consolas";')
        self.selected_label = label
        self.selected_label.setStyleSheet('border: 2px solid red; font: italic 23pt "Consolas"; padding: 0px; margin: 0px;')
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
                int(self.images_data[label].x * self.imageFrame.width() + current_pos[0]),
                int(self.images_data[label].y * self.imageFrame.height() + current_pos[1])
            )
            if not self.images_loaded:
                if (new_pos.x() < 0 or new_pos.y() < 0) or\
                (new_pos.x() > self.imageFrame.size().width() or
                    new_pos.y() > self.imageFrame.size().height()):
                    continue
            else:
                if (new_pos.x() < 0 or new_pos.y() < 0) or\
                (new_pos.x() > self.imageFrame.size().width() or
                    new_pos.y() > self.imageFrame.size().height() or
                    label.size().height() + new_pos.y() > self.imageFrame.size().height()):
                    continue
            label.move(new_pos)
            self.get_current_bounding_box()
