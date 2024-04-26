from PyQt5 import QtWidgets, QtCore, QtGui
from main.processor_qt import Ui_processor
from natsort import natsorted
from functools import partial

from main.utils import list_files, ImageWrapper


class ProcessorWindow(QtWidgets.QMainWindow, Ui_processor):
    def __init__(self, *args, obj=None, **kwargs):
        super(ProcessorWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # =================================== MEMBORS ===================================
        self.data_folder = None
        self.data: list
        self.images = []
        self.images_data = {}
        self.base_poses = {}
        self.selected_label = None
        self.images_loaded = False
        self.filler_image_path = None
        self.selected_fill_mode = None
        
        # =================================== SIGNAL HANDLING ===================================
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
        self.actionOpen_Filler_Image.triggered.connect(
            self.open_file_selection_dialog
        )
        self.fill_mode_box.currentIndexChanged.connect(
            self.fillmode_select
        )
        self.addFill.clicked.connect(
            self.fill_label_with_pixmap
        )
        self.removeFill.clicked.connect(
            self.remove_pixmap
        )
        self.imageFrame.installEventFilter(self)

        # =================================== INIT FUNCTIONS ===================================
        self.images_per_frame_update()
        self.set_images_poses()
        self.item_list.itemDoubleClicked.connect(self.open_image_sequence)
        self.boundingbox.setStyleSheet('border: 2px solid blue;')
        self.get_current_bounding_box()
        self.boundingbox.show()
        self.fillmode_select()


    # =================================== METHODS ===================================


    def fill_label_with_pixmap(self) -> None:
        """
        Fill the bounding box label with a scaled pixmap.

        If the filler_image_path is None, the function returns without 
        performing any action.
        The function scales the filler pixmap to match the width of the 
        first image in the images list.
        Then, it creates a QImage with the dimensions of the bounding box and 
        paints the scaled filler pixmap repeatedly across the image.
        Finally, it sets the QImage as the pixmap for the bounding 
        box label.
        """
        if self.filler_image_path is None:
            return
        filler = self.filler_pixmap.scaledToWidth(self.images[0].size().width())
        width = int(self.boundingbox.width())
        height = int(self.boundingbox.height())
        image = QtGui.QImage(width, height, QtGui.QImage.Format.Format_ARGB32)
        painter = QtGui.QPainter(image)
        for x in range(0, width, filler.width()):
            for y in range(0, height, filler.height()):
                painter.drawPixmap(x, y, filler)
        del painter
        self.boundingbox.setPixmap(QtGui.QPixmap.fromImage(image))



    def remove_pixmap(self) -> None:
        """
        Remove the pixmap from the bounding box label.
        """
        self.boundingbox.clear()



    def eventFilter(self, obj, event) -> None:
        """
        Filter the event for the specified object.

        If the object is the imageFrame and the event type is ContextMenu,
        the function removes the border and styling of the selected label, if any.
        Returns True if the event is handled, otherwise, propagates the event to the superclass.

        Args:
            obj: The object to filter events for.
            event: The event to filter.
        """
        if obj == self.imageFrame and event.type() == event.ContextMenu:
            if self.selected_label:
                self.selected_label.setStyleSheet('border: none; font: italic 30pt "Consolas";')
                self.selected_label = None
        return super().eventFilter(obj, event)



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
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open File",
            "${HOME}",
            "All Files (*);;Text Files (*.txt)"
        )
        if fname:
            self.filler_image_path = fname
            self.update_filler_image()



    def update_filler_image(self):
        """
        Update the filler image displayed in the filler_image_label.

        Loads the filler image from the filler_image_path and scales 
        it to 30% of the width of the toolMenu.
        If the loaded pixmap is not null, sets it as the pixmap 
        for the filler_image_label.

        """
        temp_pixmap = QtGui.QPixmap(self.filler_image_path)
        if not temp_pixmap.isNull():
            new_width = self.toolMenu.size().width()
            temp_pixmap = temp_pixmap.scaledToWidth(int(new_width * 0.3))
            self.filler_pixmap = temp_pixmap
            self.filler_image.setPixmap(temp_pixmap)



    def fillmode_select(self, _=None):
        """
        Select the fill mode and update the visibility of filler_image and filler_image_label accordingly.

        Sets the selected fill mode based on the current 
        text of the fill_mode_box.
        If the selected fill mode is 'Empty', hides the 
        filler_image and filler_image_label.
        If the selected fill mode is 'Fill With Image', 
        shows the filler_image and filler_image_label.
        Otherwise, hides the filler_image and filler_image_label.

        Args:
            _: Unused argument.

        """
        self.selected_fill_mode = self.fill_mode_box.currentText()
        if self.selected_fill_mode is None or self.selected_fill_mode == 'Empty':
            self.filler_image.hide()
            self.filler_image_label.hide()
        elif self.selected_fill_mode == 'Fill With Image':
            self.filler_image.show()
            self.filler_image_label.show()
        else:
            self.filler_image.hide()
            self.filler_image_label.hide()



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
        """
        Open an image sequence starting from the specified item.

        Args:
            item: The item corresponding to the starting image in the sequence.
        """
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



    def update_sizes_and_bases(self):
        """
        Update sizes and positions of images within the imageFrame.

        If images are loaded, calculates and updates the sizes 
        and positions of images within the imageFrame
        based on the available space and the number of images.
        """
        if not self.images_loaded:
            return
        image_frame_h = self.imageFrame.size().height()
        for i, label in enumerate(self.images):
            if not label.pixmap():
                continue
            old_base = self.base_poses[label]
            each_image_w = int(
                (self.imageFrame.size().width() / len(self.images))
            )
            resized_pixmap = label.pixmap().scaledToWidth(int(each_image_w))
            each_image_h = resized_pixmap.size().height()

            if (image_frame_h - each_image_h) < 0:
                resized_pixmap = resized_pixmap.scaledToHeight(int(image_frame_h))
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
        """
        Calculate the bounding box around the current images.

        Determines the position and size of the bounding box encompassing all the currently displayed images
        and updates the boundingbox accordingly.
        """
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
        self.remove_pixmap()



    def set_images_poses(self):
        """
        Set the positions of images within the imageFrame.

        Calculates and sets the positions of images within the 
        imageFrame based on the percentage
        of the width and height of the imageFrame.

        """
        for i, label in enumerate(self.images):
            x_step = 1 / len(self.images)
            pos = self.move_label_percent(label, i*x_step, 0.5)
            self.base_poses[label] = pos
        self.apply_data()



    def move_label_percent(self, label: QtWidgets.QLabel, x_percent, y_percent) -> tuple[int]:
        """
        Move the label to the specified percentage position within the imageFrame.

        Args:
            label: The label to move.
            x_percent: The percentage of the width of the imageFrame.
            y_percent: The percentage of the height of the imageFrame.

        Returns:
            tuple: The new position of the label in pixels.
        """
        x_pixel = int(x_percent * self.imageFrame.width())
        y_pixel = int(y_percent * self.imageFrame.height())
        label.move(x_pixel, y_pixel)
        return (x_pixel, y_pixel)



    def on_label_clicked(self, label: QtWidgets.QLabel, *args) -> None:
        """Outline clicked label and load it's data to ui"""
        if self.selected_label:
            self.selected_label.setStyleSheet('border: none; font: \
                                              italic 30pt "Consolas";')
        self.selected_label = label
        self.selected_label.setStyleSheet('border: 2px solid red; font: italic 23pt \
                                          "Consolas"; padding: 0px; margin: 0px;')
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
        """
        Apply data to the UI and move labels to their positions.

        Loads data to the UI and adjusts the positions of labels based on the current imageFrame size
        and label positions stored in base_poses. If images are not loaded, labels are moved within
        the visible region of the imageFrame. If images are loaded, labels are moved within the visible
        region and their size is checked to ensure they fit within the imageFrame.
        """
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
