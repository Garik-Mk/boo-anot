# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main\processor.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_processor(object):
    def setupUi(self, processor):
        processor.setObjectName("processor")
        processor.resize(1253, 600)
        self.centralwidget = QtWidgets.QWidget(processor)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.item_list = QtWidgets.QListWidget(self.groupBox_3)
        self.item_list.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.item_list.setObjectName("item_list")
        self.verticalLayout_2.addWidget(self.item_list)
        self.line_3 = QtWidgets.QFrame(self.groupBox_3)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_2.addWidget(self.line_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.select_all = QtWidgets.QPushButton(self.groupBox_3)
        self.select_all.setObjectName("select_all")
        self.horizontalLayout.addWidget(self.select_all)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_6.addWidget(self.groupBox_3)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.imageFrame = QtWidgets.QWidget(self.groupBox)
        self.imageFrame.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.imageFrame.setObjectName("imageFrame")
        self.boundingbox = QtWidgets.QLabel(self.imageFrame)
        self.boundingbox.setGeometry(QtCore.QRect(240, 220, 47, 13))
        self.boundingbox.setText("")
        self.boundingbox.setObjectName("boundingbox")
        self.verticalLayout.addWidget(self.imageFrame)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.scale_plus = QtWidgets.QPushButton(self.groupBox)
        self.scale_plus.setObjectName("scale_plus")
        self.horizontalLayout_5.addWidget(self.scale_plus)
        self.scale_minus = QtWidgets.QPushButton(self.groupBox)
        self.scale_minus.setObjectName("scale_minus")
        self.horizontalLayout_5.addWidget(self.scale_minus)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_5.addWidget(self.label)
        self.images_per_frame_spin_box = QtWidgets.QSpinBox(self.groupBox)
        self.images_per_frame_spin_box.setMinimum(1)
        self.images_per_frame_spin_box.setMaximum(32)
        self.images_per_frame_spin_box.setProperty("value", 1)
        self.images_per_frame_spin_box.setObjectName("images_per_frame_spin_box")
        self.horizontalLayout_5.addWidget(self.images_per_frame_spin_box)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout.setStretch(0, 1)
        self.horizontalLayout_6.addWidget(self.groupBox)
        self.toolMenu = QtWidgets.QGroupBox(self.centralwidget)
        self.toolMenu.setObjectName("toolMenu")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.toolMenu)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.fill_mode = QtWidgets.QHBoxLayout()
        self.fill_mode.setObjectName("fill_mode")
        self.label_4 = QtWidgets.QLabel(self.toolMenu)
        self.label_4.setObjectName("label_4")
        self.fill_mode.addWidget(self.label_4)
        self.fill_mode_box = QtWidgets.QComboBox(self.toolMenu)
        self.fill_mode_box.setObjectName("fill_mode_box")
        self.fill_mode_box.addItem("")
        self.fill_mode_box.addItem("")
        self.fill_mode_box.addItem("")
        self.fill_mode.addWidget(self.fill_mode_box)
        self.verticalLayout_3.addLayout(self.fill_mode)
        self.groupBox_4 = QtWidgets.QGroupBox(self.toolMenu)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.groupBox_4)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox_4)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.currentX = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.currentX.setDecimals(4)
        self.currentX.setMinimum(-1.0)
        self.currentX.setMaximum(1.0)
        self.currentX.setSingleStep(0.001)
        self.currentX.setObjectName("currentX")
        self.gridLayout.addWidget(self.currentX, 0, 1, 1, 1)
        self.currentY = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.currentY.setDecimals(4)
        self.currentY.setMinimum(-1.0)
        self.currentY.setMaximum(1.0)
        self.currentY.setSingleStep(0.001)
        self.currentY.setObjectName("currentY")
        self.gridLayout.addWidget(self.currentY, 1, 1, 1, 1)
        self.verticalLayout_3.addWidget(self.groupBox_4)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_5 = QtWidgets.QLabel(self.toolMenu)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_4.addWidget(self.label_5)
        self.spinBox_2 = QtWidgets.QSpinBox(self.toolMenu)
        self.spinBox_2.setObjectName("spinBox_2")
        self.horizontalLayout_4.addWidget(self.spinBox_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.line = QtWidgets.QFrame(self.toolMenu)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.filler_image = QtWidgets.QLabel(self.toolMenu)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filler_image.sizePolicy().hasHeightForWidth())
        self.filler_image.setSizePolicy(sizePolicy)
        self.filler_image.setMinimumSize(QtCore.QSize(0, 140))
        self.filler_image.setAlignment(QtCore.Qt.AlignCenter)
        self.filler_image.setObjectName("filler_image")
        self.verticalLayout_3.addWidget(self.filler_image)
        self.filler_image_label = QtWidgets.QLabel(self.toolMenu)
        self.filler_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.filler_image_label.setObjectName("filler_image_label")
        self.verticalLayout_3.addWidget(self.filler_image_label)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.addFill = QtWidgets.QPushButton(self.toolMenu)
        self.addFill.setObjectName("addFill")
        self.verticalLayout_3.addWidget(self.addFill)
        self.removeFill = QtWidgets.QPushButton(self.toolMenu)
        self.removeFill.setObjectName("removeFill")
        self.verticalLayout_3.addWidget(self.removeFill)
        self.line_2 = QtWidgets.QFrame(self.toolMenu)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_3.addWidget(self.line_2)
        self.processSelectedData = QtWidgets.QPushButton(self.toolMenu)
        self.processSelectedData.setObjectName("processSelectedData")
        self.verticalLayout_3.addWidget(self.processSelectedData)
        self.temporal_checkbox = QtWidgets.QCheckBox(self.toolMenu)
        self.temporal_checkbox.setObjectName("temporal_checkbox")
        self.verticalLayout_3.addWidget(self.temporal_checkbox)
        self.checkBox = QtWidgets.QCheckBox(self.toolMenu)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_3.addWidget(self.checkBox)
        self.horizontalLayout_6.addWidget(self.toolMenu)
        self.horizontalLayout_6.setStretch(1, 1)
        processor.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(processor)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1253, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        processor.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(processor)
        self.statusbar.setObjectName("statusbar")
        processor.setStatusBar(self.statusbar)
        self.actionOpen_Data = QtWidgets.QAction(processor)
        self.actionOpen_Data.setObjectName("actionOpen_Data")
        self.actionOpen_Filler_Image = QtWidgets.QAction(processor)
        self.actionOpen_Filler_Image.setObjectName("actionOpen_Filler_Image")
        self.actionChange_Save_Path = QtWidgets.QAction(processor)
        self.actionChange_Save_Path.setObjectName("actionChange_Save_Path")
        self.actionAuto_process = QtWidgets.QAction(processor)
        self.actionAuto_process.setObjectName("actionAuto_process")
        self.menuFile.addAction(self.actionOpen_Data)
        self.menuFile.addAction(self.actionOpen_Filler_Image)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionChange_Save_Path)
        self.menuEdit.addAction(self.actionAuto_process)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.retranslateUi(processor)
        QtCore.QMetaObject.connectSlotsByName(processor)

    def retranslateUi(self, processor):
        _translate = QtCore.QCoreApplication.translate
        processor.setWindowTitle(_translate("processor", "MainWindow"))
        self.groupBox_3.setTitle(_translate("processor", "Dataset"))
        self.select_all.setText(_translate("processor", "Select All"))
        self.groupBox.setTitle(_translate("processor", "Preview"))
        self.scale_plus.setText(_translate("processor", "+"))
        self.scale_minus.setText(_translate("processor", "-"))
        self.label.setText(_translate("processor", "Images Per Frame"))
        self.toolMenu.setTitle(_translate("processor", "Tools"))
        self.label_4.setText(_translate("processor", "Fill mode"))
        self.fill_mode_box.setItemText(0, _translate("processor", "Empty"))
        self.fill_mode_box.setItemText(1, _translate("processor", "Fill With Image"))
        self.fill_mode_box.setItemText(2, _translate("processor", "Fill Random"))
        self.groupBox_4.setTitle(_translate("processor", "Shift"))
        self.label_2.setText(_translate("processor", "X"))
        self.label_3.setText(_translate("processor", "Y"))
        self.label_5.setText(_translate("processor", "Depth level"))
        self.filler_image.setText(_translate("processor", "Filler image"))
        self.filler_image_label.setText(_translate("processor", "Image used for filling"))
        self.addFill.setText(_translate("processor", "Add Fill"))
        self.removeFill.setText(_translate("processor", "Remove Fill"))
        self.processSelectedData.setText(_translate("processor", "Process Selected Data"))
        self.temporal_checkbox.setText(_translate("processor", "Temporal"))
        self.checkBox.setText(_translate("processor", "Frames intersection"))
        self.menuFile.setTitle(_translate("processor", "File"))
        self.menuEdit.setTitle(_translate("processor", "Edit"))
        self.actionOpen_Data.setText(_translate("processor", "Open Data"))
        self.actionOpen_Filler_Image.setText(_translate("processor", "Open Filler Image"))
        self.actionChange_Save_Path.setText(_translate("processor", "Change Save Path"))
        self.actionAuto_process.setText(_translate("processor", "Auto process"))
