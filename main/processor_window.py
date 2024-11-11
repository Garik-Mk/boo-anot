import os
import cv2
import numpy as np
from functools import partial
from PyQt5 import QtWidgets, QtCore, QtGui
from natsort import natsorted

from main.processor_qt import Ui_processor
from main.utils import list_files, ImageWrapper, paste_images, paste_images_seperately, shuffle_pixmap
from main.quilt import synthesize_texture
from tqdm import tqdm

PROCESSOR_PATH = os.path.dirname(os.path.abspath(__file__))


class ProcessorWindow(QtWidgets.QMainWindow, Ui_processor):
    def __init__(self, *args, obj=None, **kwargs):
        super(ProcessorWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # =================================== MEMBERS ===================================
        self.data_folder = None
        self.data: list
        self.images = []
        self.images_data = {}
        self.base_poses = {}
        self.objects_list = []
        self.selected_label = None
        self.images_loaded = False
        self.filler_image_path = None
        self.selected_fill_mode = None
        self.filler_pixmap = None
        self.base_sizes = []
        self.filler_base_size: None
        self.save_path = PROCESSOR_PATH
        self.temp_background_save_file_path = os.path.join(PROCESSOR_PATH, "temp.bmp")
        self.scale = 1.0
        self.same_folder = False
        self.move_vertical_size = 0
        self.move_horizontal_size = 0
        self.filler_crop_size = 0.3
        self.hided_label = None
        self.index_to_show = 0
        self.is_bg_filled = False
        self.video_seq_len = None
        self.selected_parent = None
        self.data_to_delete = []
        # self.frames, self.frames_copy = self.group_seq_frames(self.data)

        # =================================== SIGNAL HANDLING ===================================

        self.actionOpen_Data.triggered.connect(
            self.open_folder_selection_dialog
        )
        self.actionOpen_Filler_Image.triggered.connect(
            self.open_file_selection_dialog
        )
        self.actionChange_Save_Path.triggered.connect(
            partial(self.open_folder_selection_dialog, True)
        )
        self.actionSame_Label_And_Data_folder.triggered.connect(
            self.reverse_label_data_folder_state
        )

        self.images_per_frame_spin_box.valueChanged.connect(
            self.images_per_frame_update
        )
        self.currentX.valueChanged.connect(
            self.apply_x_offset
        )
        self.currentY.valueChanged.connect(
            self.apply_y_offset
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
        self.processSelectedData.clicked.connect(
            self.process_selected_data
        )
        self.scale_plus.clicked.connect(
            self.scale_up
        )
        self.scale_minus.clicked.connect(
            self.scale_down
        )
        self.select_all.clicked.connect(
            self.select_all_items
        )
        self.item_list.itemDoubleClicked.connect(
            self.open_image_sequence
        )
        self.verticalSlider.valueChanged.connect(
            self.move_vertical
        )
        self.horizontalSlider.valueChanged.connect(
            self.move_horizontal
        )

        # self.processVideoData.stateChanged.connect(
        #     self.process_videodata
        # )

        self.nextButton.clicked.connect(
            self.add_index
        )

        self.prevButton.clicked.connect(
            self.subtract_index
        )
        self.treeWidget.itemDoubleClicked.connect(
            self.open_image_sequence
        )
        
        self.SaveAllVideoData.clicked.connect(
            self.save_video_data_helper
        )

        self.imageFrame.installEventFilter(self)

        # =================================== INIT FUNCTIONS ===================================
        self.images_per_frame_update()
        self.set_images_poses()
        self.boundingbox.setStyleSheet('border: 1px solid blue;')
        self.get_current_bounding_box()
        self.boundingbox.show()
        self.fillmode_select()


    # =================================== METHODS ===================================


    def move_vertical(self, value):
        self.move_vertical_size = value
        self.apply_data()


    def move_horizontal(self, value):
        self.move_horizontal_size = value
        self.apply_data()


    def process_single_image_from_frame(self) -> None:
        if self.boundingbox.pixmap() is None or not self.images_loaded:
            return
        coords, bb_x, bb_y = self.calculate_coords()

        self.save_background(bb_x)

        result_image = paste_images(self.temp_background_save_file_path, self.objects_list, coords)
        cv2.imwrite(os.path.join(PROCESSOR_PATH, 'result_image.bmp'), result_image)

        self.remove_saved_background()


    def reverse_label_data_folder_state(self) -> None:
        """Reverses state of using same folder for images and labels"""
        self.same_folder = not self.same_folder


    def process_selected_data(self) -> None:
        if not self.autoApplyOffsetsCheckbox.isChecked():
            coords, bb_x, bb_y = self.calculate_coords()
            self.save_background(bb_x)
        
        for i, item in enumerate(self.item_list.selectedItems()):
            current_index = self.item_list.row(item) if not self.SaveVideoData.isChecked() else self.selected_parent
            next_items = []
            file_list = []
            if not self.processVideoData.isChecked():
                for j in range(current_index, min(
                                            current_index + (self.images_per_frame_spin_box.value()),
                                            self.item_list.count()
                                            )):
                    index = self.data.index(self.item_list.item(j).text())
                    next_items.append(
                        self.file_paths[self.data[index]]
                    )
                    file_list.append(self.data[index])
            
            elif self.processVideoData.isChecked() and self.selected_parent:
                next_items = []
                file_list = []
                for j in range(self.selected_parent.childCount()):
                    index = self.data.index(self.selected_parent.child(j).text(0))
                    next_items.append(
                        self.file_paths[self.data[index]]
                    )
                    file_list.append(self.data[index])
            if self.autoApplyOffsetsCheckbox.isChecked():
                ret = self.auto_apply_offsets(file_list)
                if ret < 0:
                    return
                self.fill_label_with_pixmap()
                coords, bb_x, bb_y = self.calculate_coords()
                self.save_background(bb_x)
            if self.savedata.isChecked():
                result_image = paste_images(self.temp_background_save_file_path, next_items, coords)
                cv2.imwrite(os.path.join(self.save_path, self.generate_image_name(next_items)), result_image)
            if self.autoApplyOffsetsCheckbox.isChecked():
                self.remove_saved_background()
        
        self.remove_saved_background()
        if self.processVideoData.isChecked():
            self.frames, self.frames_copy = self.group_seq_frames(self.data)
            self.frames = self.normalize_vid_lenght(self.frames)
            self.hide_item_list()
            self.process_videodata()
            self.output.append(f'Not enough instances of {self.boundingbox.pixmap().size() * (self.base_sizes[0][0] / self.images[0].size().width())} object\n')


    def generate_image_name(self, data) -> str:
        result_name = ''
        result_name += os.path.split(data[0])[1].split('.')[0]
        result_name += f'__l{len(data)}'
        return result_name + '.bmp'



    def save_background(self, bb_x) -> None:
        copied_pixmap = self.boundingbox.pixmap().copy()
        copied_pixmap = copied_pixmap.scaledToWidth(bb_x)
        copied_pixmap.save(self.temp_background_save_file_path, "BMP")
        

    def remove_saved_background(self) -> None:
        if os.path.exists(self.temp_background_save_file_path):
            os.remove(self.temp_background_save_file_path)


    def calculate_coords(self) -> list:
        coords_x, coords_y = [], []
        for i, item in enumerate(self.images_data):
            # Calculate x
            x_offset = round(
                (item.pos().x() - self.base_poses[item][0])
                / (item.size().width()
                    / self.base_sizes[i][0])
            )
            width = self.base_sizes[i][0]
            pos_x = width * i
            pos_x += x_offset
            coords_x.append(pos_x)

            # Calcualte y
            y_offset = round(
                (item.pos().y() - self.base_poses[item][1])
                / (item.size().height()
                    / self.base_sizes[i][1])
            )
            # print((item.pos().y() - self.base_poses[item][1]))
            pos_y = 0
            pos_y += y_offset
            coords_y.append(pos_y)

        min_y = min(coords_y)
        coords_y = [num - min_y for num in coords_y]
        bb_x = max(coords_x) + self.base_sizes[0][0]
        bb_y = max(coords_y) + self.base_sizes[0][1]
        return list(zip(coords_x, coords_y)), bb_x, bb_y


    def auto_apply_offsets(self, sequence: list) -> None:
        self.output.append(f'{str(sequence)}\n')
        for i, item in enumerate(sequence):
            offsets_vector = []
            base_trackID = None
            last_tick = None
            for file_name in sequence:
                self.output.append(f'Processing {file_name}\n')
                # self.output.append(f'Processing  {self.selected_parent.text(0)}\n')
                new_trackID, distance, tick = self.extract_data_from_name(file_name)
                # print(f'new_trackID: {new_trackID}, distance: {distance}, tick: {tick}')
                if base_trackID is None:
                    base_trackID = new_trackID
                elif new_trackID != base_trackID:
                    self.output.append(f'Not enough instances of {base_trackID} object\n')
                    self.statusBar().showMessage(f'Not enough instances of {base_trackID} object', 5000)
                    return -1
                if last_tick is None:
                    last_tick = tick
                    # print(f"last tick has updated to {last_tick}")
                elif abs(tick - last_tick) > 5:
                    self.output.append(f'Difference between neighbour ticks: {abs(tick - last_tick)}\n')
                    self.statusBar().showMessage(f'Difference between neighbour ticks: {abs(tick - last_tick)}', 5000)
                    return -2
                else:
                    last_tick = tick
                offsets_vector.append(distance)
            self.output.append(f'base: {offsets_vector}\n')
            min_distance = min(offsets_vector)
            max_distance = max(offsets_vector)
            for i, elem in enumerate(offsets_vector):
                offsets_vector[i] = elem - min_distance

            for i, elem in enumerate(offsets_vector):                
                offsets_vector[i] = elem * self.offset_coef_spin_box.value() if elem * self.offset_coef_spin_box.value() < 1 else 1


            # for i, elem in enumerate(offsets_vector):
            #     if offsets_vector[i] > 1:
            #         offsets_vector[i] = 1
            self.output.append(f'offsets: {offsets_vector}\n')
            for index, _object in enumerate(self.images_data):
                try:
                    self.images_data[_object].y = -offsets_vector[index]
                except IndexError:
                    self.statusBar().showMessage('Not enough images to process', 5000)
                    self.output.append(f'\nNot enough images to process\n')
                    self.images_data[_object].y = 0
            self.apply_data()
        return 0



    def extract_data_from_name(self, file_name: str) -> float:
        """
        Providen filename with format: label_datasetID_trackID_tick_d{distance}.bmp

        Extracts distance, trackID and tick from filename

        Returns trackID: str
                distance: float
                tick: int
        """
        base_name, _ = os.path.splitext(file_name)
        trackID = base_name.split('__')[2]
        distance = float(base_name.split('n')[-1].split('m')[0].replace('_', ''))
        tick = int(base_name.split('__')[3].split('_')[0])
        return trackID, distance, tick


    def autofillShuffle(self, quilt=False) -> None:
        """
        Generate auto filling pixmap, croping top and bottom partes of opened images

        For each image, top part of size self.filler_crop_size is cropped,
        and applied to background to fill the top part and make secure, that
        there is no empty space. Same is done with the bottom part.
        """
        real_width_bg, real_height_bg = int(self.boundingbox.width()), int(self.boundingbox.height())
        real_width_pixmap, real_height_pixmap = self.base_sizes[0]
        scaled_width_pixmap, scaled_height_pixmap = self.images[0].size().width(), self.images[0].size().height()
        scale_factor = real_width_pixmap / scaled_width_pixmap
        scaled_width_bg, scaled_height_bg = round(real_width_bg / scale_factor), round(real_height_bg / scale_factor)
        if quilt:
            # sample_image = cv2.imread(r"C:\Users\Uzer\Desktop\negative\negative\06-06-2022 negative\6.bmp")
            sample_image = cv2.imread(self.objects_list[0])
            texture = sample_image[:, :8]
            # sample_bottom = sample_image[-3:, :]
            # texture = cv2.vconcat([sample_top, sample_bottom])
            # print(texture.shape)
            cv2.imwrite('texture.jpeg', texture)
            output_shape = (real_height_bg, real_width_bg, 3)
            block_size = 3
            overlap = 1
            synth_bg = synthesize_texture(texture, output_shape, block_size, overlap)
            cv2.imwrite(self.temp_background_save_file_path, synth_bg)
            # self.temp_background_save_file_path = 'Synthezied_BG.jpeg'
            image = QtGui.QImage(self.temp_background_save_file_path)
            texture = QtGui.QImage('texture.jpeg')
            self.filler_pixmap = QtGui.QPixmap(6, 20)
            self.filler_pixmap.convertFromImage(texture)
            self.filler_image.setPixmap(self.filler_pixmap)
            
        else:
            image = QtGui.QImage(scaled_width_bg, scaled_height_bg, QtGui.QImage.Format.Format_ARGB32)
            painter = QtGui.QPainter(image)
            center_line_y = scaled_height_bg // 2
            crop_pixels_count = round(real_height_pixmap * self.filler_crop_size)
            for index, each_pixmap in enumerate(self.images):
                croped_pixmap_top = each_pixmap.pixmap().copy(
                    QtCore.QRect(0, 0, scaled_width_pixmap, round(crop_pixels_count * scale_factor))
                )
                croped_pixmap_bottom = each_pixmap.pixmap().copy(
                    QtCore.QRect(0, scaled_height_pixmap - round(crop_pixels_count * scale_factor), scaled_width_pixmap, scaled_height_pixmap)
                )
                croped_pixmap_top_downscaled = croped_pixmap_top.scaledToWidth(real_width_pixmap)
                croped_pixmap_bottom_downscaled = croped_pixmap_bottom.scaledToWidth(real_width_pixmap)
                start_point_x = index * real_width_pixmap
                processed_top = shuffle_pixmap(croped_pixmap_top_downscaled)
                processed_bottom = shuffle_pixmap(croped_pixmap_bottom_downscaled)
                for y in range(center_line_y, 0 - crop_pixels_count, -crop_pixels_count):
                    painter.drawPixmap(start_point_x, y, processed_top)
                for y in range(center_line_y, scaled_height_bg, crop_pixels_count):
                    painter.drawPixmap(start_point_x, y, processed_bottom)
            del painter
        bg_pixmap = QtGui.QPixmap.fromImage(image)
        bg_pixmap = bg_pixmap.scaledToWidth(scaled_width_bg)
        bg_pixmap = bg_pixmap.scaledToHeight(scaled_height_bg)
        self.boundingbox.setPixmap(bg_pixmap)
    
    def process_videodata(self):
        # self.remove_pixmap()
        self.update_sizes_and_bases()
        self.fill_label_with_pixmap()
        if self.processVideoData.isChecked():
            self.SaveVideoData.setEnabled(True)
            self.prevButton.setEnabled(True)
            self.nextButton.setEnabled(True)
            self.make_data_tree()
            # if not self.is_bg_filled:
            #     self.process_selected_data()
            if self.SaveVideoData.isChecked():
                self.save_video_data(self.selected_parent)
                
            for ind ,label in enumerate(self.images):
                if ind != self.index_to_show:
                    label.hide()
                else:
                    label.show()
        else:
            self.SaveVideoData.setEnabled(False)
            for label in self.images:
                label.show()
    
    def save_video_data(self, parent_item):  
        child_count = parent_item.childCount()  
        image_paths = []
        coords, bb_x, _ = self.calculate_coords()
        self.save_background(bb_x)
        for i in range(child_count):
            child_item = parent_item.child(i)
            image_paths.append(self.file_paths[child_item.text(0)])
            # print(f"    Child: {self.file_paths[child_item.text(0)]}")
        # cv2.imwrite('havayi_ardyunq.jpeg',paste_images_seperately(self.temp_background_save_file_path, image_paths, coords)) 
        paste_images_seperately(self.temp_background_save_file_path, image_paths, coords, self.selected_parent)  
         
    def save_video_data_helper(self):
        root = self.treeWidget.invisibleRootItem()  
        child_count = root.childCount()
        self.SaveVideoData.setCheckState(QtCore.Qt.Checked)

        for i in tqdm(range(child_count)):
            self.selected_parent = root.child(i)
            self.open_image_sequence(self.selected_parent)
            self.process_selected_data()

    def subtract_index(self):
        if self.index_to_show > 0:
            self.index_to_show -= 1
            # self.process_videodata()  
            for ind ,label in enumerate(self.images):
                if ind != self.index_to_show:
                    label.hide()
                else:
                    label.show()
    def add_index(self):
        if self.index_to_show < len(self.objects_list):
            self.index_to_show += 1
            # self.process_videodata()
            for ind ,label in enumerate(self.images):
                if ind != self.index_to_show:
                    label.hide()
                else:
                    label.show()


    def group_seq_frames(self, files):
        """Grouping Sequential Frames To Make Video"""

        frames = {}
        frames_copy = {}

        for file in files:
            info = file.split('__')
            my_tup = (info[1], info[2], info[3])
            # print(info[1], info[2], info[3])
            # print(f'file name is {file}   splited list is {file.split('__')} and    my tuple is {my_tup}')

            if frames.get(my_tup): 
                frames[my_tup].append(file)     #PROCESSOR_PATH + '\\' + 
                frames_copy[my_tup].append(file)        #PROCESSOR_PATH + '\\' + 
            else:
                frames[my_tup] = [file]     #PROCESSOR_PATH + '\\' + 
                frames_copy[my_tup] = [file]        #PROCESSOR_PATH + '\\' + 

        
        return frames, frames_copy

    
    def cut_video(self, video, norm_size = 8, min_size = 8 ):
        main_num = len(video) // norm_size
        extra = int((len(video) % norm_size) >= min_size)
        num_of_cuts = main_num + extra
        cuted_videos = [[]]
        counter = 0
        for i in range(num_of_cuts) if not extra else range(num_of_cuts - 1):
            while counter % norm_size != 0 or counter == 0:
                cuted_videos[0].append(video[counter])
                counter += 1
            # counter = min(len(video) - 1, counter)
            if counter == len(video):
                break
            cuted_videos.insert(0, [video[counter]])
            counter += 1
        # cuted_videos.pop(0)
        if extra:
            cuted_videos[0] = video[-(len(video) % norm_size):]
        elif not extra and len(video) % norm_size != 0:
            cuted_videos.pop(0)
        # print(f"cuted videos:   {cuted_videos}")
        return cuted_videos

    def normalize_vid_lenght(self,  frames):
        for key, value in frames.items():
            if len(value) < 8:
                del self.frames_copy[key]
            # elif len(value) > 6 and len(value) < 15:
            #     pass
            else:
                cuted_videos = self.cut_video(frames[key])
                del self.frames_copy[key]
                for i in range(len(cuted_videos)):
                    self.frames_copy[key + (str(i),)] = cuted_videos[i]
        # frames = self.frames_copy
        return self.frames_copy
    
    def hide_item_list(self):
        self.item_list.hide()

    def make_data_tree(self):
        for key, value in self.frames.items():
            tree_element = QtWidgets.QTreeWidgetItem([str(key)])
            self.treeWidget.addTopLevelItem(tree_element)
            self.extracts_items_from_list(tree_element, value)
        self.treeWidget.setEnabled(True)
    
    def extracts_items_from_list(self, parent, branch_childs: list):
        for elem in branch_childs:
            child = QtWidgets.QTreeWidgetItem([str(elem)])
            parent.addChild(child)


    def len_of_video_frame(self, item):
        # print(self.video_seq_len)
        # print(f'len of frames works in line 479 {item}')
        if type(item) == QtWidgets.QTreeWidgetItem and not item.parent():
            self.video_seq_len = item.childCount()
        elif type(item) == QtWidgets.QTreeWidgetItem and item.parent():
            self.video_seq_len = item.parent().childCount()
        # print(self.video_seq_len)

    # def fill_images_with_tree_childs(self, item):
    #     l = item.childCount()
    #     self.images.clear()
    #     start_ind = self.data.index(item.child(0).text(0))
    #     for i in range(start_ind, start_ind + l):
    #         self.
            
        

    def fill_label_with_pixmap(self) -> None:
        """
        Fill the bounding box label with a scaled pixmap.

        If the filler_pixmap is None, the function returns without
        performing any action.
        The function scales the filler pixmap to match the width of the
        first image in the images list.
        Then, it creates a QImage with the dimensions of the bounding box and
        paints the scaled filler pixmap repeatedly across the image.
        Finally, it sets the QImage as the pixmap for the bounding
        box label.
        """
        self.fillmode_select()
        if self.selected_fill_mode == 'Auto (Shuffle)':
            self.autofillShuffle(quilt=False)
            return
        if self.selected_fill_mode == 'Auto (Quilt)':
            self.autofillShuffle(quilt=True)
            self.is_bg_filled = True
            return
        if self.filler_pixmap is None:
            return        
        if self.selected_fill_mode == 'Extracted Noise':
            filler_width = self.filler_pixmap.size().width()
            image_real_width = self.base_sizes[0][0]
            image_scaled_width = self.images[0].size().width()
            real_scale = (image_scaled_width / image_real_width) * filler_width
            filler = self.filler_pixmap.scaledToWidth(int(real_scale))
        else:
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


    def generate_empty_filler(self) -> None:
        """
        Generate an empty filler pixmap filled with black color.

        If images are not loaded, creates a filler pixmap with a default width of 10 pixels and height of 30 pixels.
        If images are loaded, creates a filler pixmap with the same dimensions as the first loaded image.
        Fills the pixmap with black color and sets it as the pixmap for the filler_image QLabel.

        """
        if self.images_loaded == False:
            return
        else:
            width = self.images[0].size().width()
            height = self.images[0].size().height()
        # print(f'height is {height} widhth is {width}')
        self.filler_pixmap = QtGui.QPixmap(width, height)
        self.filler_pixmap.fill(QtGui.QColor("black"))
        self.filler_image.setPixmap(self.filler_pixmap)


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
    def open_folder_selection_dialog(self, save=False) -> None:
        """
        Open a file selection dialog to choose the data folder.
        """
        fname = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Open Fodler",
            "${HOME}"
        )
        if fname:
            if save:
                self.save_path = fname
            else:
                self.data_folder = fname
                self.load_image_in_list()


    def open_file_selection_dialog(self) -> None:
        """
        Open a file selection dialog to choose a single file.
        """
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Filler File",
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
            self.filler_base_size = (temp_pixmap.size().width(), temp_pixmap.size().height())
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
        if self.selected_fill_mode is None:
            self.filler_image.hide()
            self.filler_image_label.hide()
        elif self.selected_fill_mode == 'Fill With Image' or self.selected_fill_mode == 'Extracted Noise':
            self.filler_image.show()
            self.filler_image_label.show()
        elif self.selected_fill_mode == 'Empty':
            self.generate_empty_filler()
            self.filler_image.show()
            self.filler_image_label.show()
        elif self.selected_fill_mode == 'Auto (Quilt)':
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
        self.file_paths = list_files(self.data_folder, self.same_folder)
        self.data = natsorted(self.file_paths.keys())
        self.item_list.addItems(self.data)



    def open_image_sequence(self, item, processing=False):
        """
        Open an image sequence starting from the specified item.

        Args:
            item: The item corresponding to the starting image in the sequence.
        """
        if self.processVideoData.isChecked() and type(item) == QtWidgets.QTreeWidgetItem and not item.parent():
            start_ind = self.data.index(item.child(0).text(0))    
        
        elif self.processVideoData.isChecked() and type(item) == QtWidgets.QTreeWidgetItem and item.parent():
            start_ind = self.data.index(item.parent().child(0).text(0))
            # print(f' What you need !!!{item.parent().child(0).text(0)}')    

        
        else:
            # print('Error handled !!!!')
            start_ind = self.data.index(item.text())
            
        # start_ind = self.data.index(item.text()) if not self.processVideoData.isChecked() else self.data.index(item.child(0).text(0))
        # print('I am in process images')
        if self.processVideoData.isChecked() and type(item) == QtWidgets.QTreeWidgetItem:
            if item.parent():
                self.selected_parent = item.parent()
            else:
                self.selected_parent  = item 
            self.len_of_video_frame(item)
            # print('Opening Image Sequance')
            self.update_sizes_and_bases() 
            self.images_per_frame_update()

        sequence_len = self.video_seq_len if self.processVideoData.isChecked()  and type(item) == QtWidgets.QTreeWidgetItem else len(self.images)
        self.objects_list = []
        for i in range(start_ind, start_ind + sequence_len):
            try:
                self.objects_list.append(self.file_paths[self.data[i]])
            except IndexError:
                self.statusBar().showMessage('Not enough images to process', 5000)
                self.output.append('There is not enough images\n')
        if not processing:
            # print(f'lenght of self.images is {len(self.images)}', end=' ')
            for i, image_path in enumerate(self.objects_list):
                temp_pixmap = QtGui.QPixmap(image_path)
                if not temp_pixmap.isNull():
                    # print(f'object is {self.objects_list[i]}')
                    self.images[i].setPixmap(temp_pixmap)
                    self.base_sizes.append(
                        (
                            temp_pixmap.size().width(),
                            temp_pixmap.size().height()
                        )
                    )
        self.images_loaded=True
        self.update_sizes_and_bases()
        self.fillmode_select()
        # self.process_selected_data()
        self.update_sizes_and_bases()
        # if self.processVideoData.isChecked():
        #     self.process_videodata()


    def update_sizes_and_bases(self):
        """
        Update sizes and positions of images within the imageFrame.

        If images are loaded, calculates and updates the sizes
        and positions of images within the imageFrame
        based on the available space and the number of images.
        """
        if not self.images_loaded:
            return
        image_frame_h = int(self.imageFrame.size().height() * self.scale)
        for i, label in enumerate(self.images):
            if not label.pixmap():
                continue
            old_base = self.base_poses[label]
            each_image_w = int(
                (self.imageFrame.size().width() / len(self.images)) * self.scale
            )
            resized_pixmap = label.pixmap().scaledToWidth(int(each_image_w))
            each_image_h = int(resized_pixmap.size().height()  * self.scale)

            if (image_frame_h - each_image_h) < 0:
                resized_pixmap = resized_pixmap.scaledToHeight(int(image_frame_h))
                each_image_h = int(resized_pixmap.size().height() * self.scale)

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


    def scale_up(self):
        self.scale += 0.01
        self.update_sizes_and_bases()

    def scale_down(self):
        self.scale -= 0.01
        self.update_sizes_and_bases()


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
        new_count = self.images_per_frame_spin_box.value() if not self.processVideoData.isChecked() else self.video_seq_len
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
                del self.images_data[label]
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
        if self.selected_label is None:
            return
        self.images_data[self.selected_label].x = self.currentX.value()
        self.apply_data()



    def apply_y_offset(self) -> None:
        """Apply x axis offset to selected image in the frame"""
        if self.selected_label is None:
            return
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
            new_pos_adjusted = QtCore.QPoint(
                new_pos.x() + self.move_horizontal_size,
                new_pos.y() + self.move_vertical_size
            )
            label.move(new_pos_adjusted)
            self.get_current_bounding_box()

    def select_all_items(self):
        self.item_list.selectAll()


# print(
#     item,
#     self.items_list[i],
#     self.images_data[item],
#     self.base_sizes[i],
#     self.base_poses[item],
#     (item.size().width(), item.size().height()),
#     (item.pos().x(), item.pos().y())
# )