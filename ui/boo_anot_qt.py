# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ImageViewer(object):
    def setupUi(self, ImageViewer):
        ImageViewer.setObjectName("ImageViewer")
        ImageViewer.resize(942, 600)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        ImageViewer.setFont(font)
        self.centralwidget = QtWidgets.QWidget(ImageViewer)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.item_list = QtWidgets.QListWidget(self.centralwidget)
        self.item_list.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.item_list.setLineWidth(1)
        self.item_list.setObjectName("item_list")
        self.verticalLayout.addWidget(self.item_list)
        self.search = QtWidgets.QLineEdit(self.centralwidget)
        self.search.setObjectName("search")
        self.verticalLayout.addWidget(self.search)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.prev_image_btn = QtWidgets.QPushButton(self.centralwidget)
        self.prev_image_btn.setObjectName("prev_image_btn")
        self.horizontalLayout.addWidget(self.prev_image_btn)
        self.next_image_btn = QtWidgets.QPushButton(self.centralwidget)
        self.next_image_btn.setObjectName("next_image_btn")
        self.horizontalLayout.addWidget(self.next_image_btn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_2.addWidget(self.line_2)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.delete_label_btn = QtWidgets.QPushButton(self.centralwidget)
        self.delete_label_btn.setObjectName("delete_label_btn")
        self.horizontalLayout_3.addWidget(self.delete_label_btn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout_3.addWidget(self.line_3)
        self.current_label = QtWidgets.QLabel(self.centralwidget)
        self.current_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.current_label.setObjectName("current_label")
        self.horizontalLayout_3.addWidget(self.current_label)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.zoom_area = QtWidgets.QVBoxLayout()
        self.zoom_area.setObjectName("zoom_area")
        self.image_label = QtWidgets.QLabel(self.centralwidget)
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setIndent(0)
        self.image_label.setObjectName("image_label")
        self.zoom_area.addWidget(self.image_label)
        self.verticalLayout_2.addLayout(self.zoom_area)
        self.verticalLayout_2.setStretch(2, 1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.setStretch(2, 1)
        ImageViewer.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(ImageViewer)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 942, 26))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuData = QtWidgets.QMenu(self.menuBar)
        self.menuData.setObjectName("menuData")
        ImageViewer.setMenuBar(self.menuBar)
        self.actionOpen_Folder = QtWidgets.QAction(ImageViewer)
        self.actionOpen_Folder.setObjectName("actionOpen_Folder")
        self.actionOpen_Labels_Folder = QtWidgets.QAction(ImageViewer)
        self.actionOpen_Labels_Folder.setObjectName("actionOpen_Labels_Folder")
        self.actionForce_Update = QtWidgets.QAction(ImageViewer)
        self.actionForce_Update.setObjectName("actionForce_Update")
        self.actionOpen_Data_Folder = QtWidgets.QAction(ImageViewer)
        self.actionOpen_Data_Folder.setObjectName("actionOpen_Data_Folder")
        self.actionOpen_Label_Folder = QtWidgets.QAction(ImageViewer)
        self.actionOpen_Label_Folder.setObjectName("actionOpen_Label_Folder")
        self.actionSame_Data_and_Label_Folder = QtWidgets.QAction(ImageViewer)
        self.actionSame_Data_and_Label_Folder.setCheckable(True)
        self.actionSame_Data_and_Label_Folder.setObjectName("actionSame_Data_and_Label_Folder")
        self.actionMove_images_to_labels = QtWidgets.QAction(ImageViewer)
        self.actionMove_images_to_labels.setObjectName("actionMove_images_to_labels")
        self.menuFile.addAction(self.actionOpen_Data_Folder)
        self.menuFile.addAction(self.actionOpen_Label_Folder)
        self.menuFile.addAction(self.actionSame_Data_and_Label_Folder)
        self.menuData.addAction(self.actionMove_images_to_labels)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuData.menuAction())

        self.retranslateUi(ImageViewer)
        QtCore.QMetaObject.connectSlotsByName(ImageViewer)

    def retranslateUi(self, ImageViewer):
        _translate = QtCore.QCoreApplication.translate
        ImageViewer.setWindowTitle(_translate("ImageViewer", "Boo Anot"))
        self.search.setPlaceholderText(_translate("ImageViewer", "Search..."))
        self.prev_image_btn.setText(_translate("ImageViewer", "Prev"))
        self.next_image_btn.setText(_translate("ImageViewer", "Next"))
        self.delete_label_btn.setText(_translate("ImageViewer", "Delete label"))
        self.label.setText(_translate("ImageViewer", "None - 0, Human -1, Car - 2, Other -3 "))
        self.current_label.setText(_translate("ImageViewer", "None"))
        self.image_label.setText(_translate("ImageViewer", "No image opened"))
        self.menuFile.setTitle(_translate("ImageViewer", "File"))
        self.menuData.setTitle(_translate("ImageViewer", "Data"))
        self.actionOpen_Folder.setText(_translate("ImageViewer", "Open Data Folder"))
        self.actionOpen_Labels_Folder.setText(_translate("ImageViewer", "Open Labels Folder"))
        self.actionForce_Update.setText(_translate("ImageViewer", "Force Update"))
        self.actionOpen_Data_Folder.setText(_translate("ImageViewer", "Open Data Folder"))
        self.actionOpen_Label_Folder.setText(_translate("ImageViewer", "Open Label Folder"))
        self.actionSame_Data_and_Label_Folder.setText(_translate("ImageViewer", "Same Data and Label Folder"))
        self.actionMove_images_to_labels.setText(_translate("ImageViewer", "Move images to labels"))
