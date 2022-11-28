from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QToolBar, QAction, QFileDialog, QWidget, \
    QPushButton, QSpinBox, QDoubleSpinBox, QHBoxLayout

import cv2
import qimage2ndarray



class MainWindow(QMainWindow):
    pixmap = None
    pixmap_clean = None

    def __init__(self):
        super().__init__()

        self.file_pc = None
        self.window_filter = None

        self.setWindowTitle("Application")
        self.setMinimumSize(QSize(400, 300))

        toolbar = QToolBar('toolbar')
        self.addToolBar(toolbar)

        self.button_open = QAction('Открыть')
        self.button_open.triggered.connect(self.open_file)
        toolbar.addAction(self.button_open)

        self.button_save = QAction('Сохранить')
        self.button_save.triggered.connect(self.save_file)
        self.button_save.setDisabled(True)
        toolbar.addAction(self.button_save)

        self.layout_main = QVBoxLayout()

        self.picture = QLabel(' ')
        self.picture.setScaledContents(False)
        self.picture.setMinimumSize(1, 1)
        self.picture.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.picture.setAlignment(QtCore.Qt.AlignCenter)
        self.layout_main.addWidget(self.picture)

        self.layout_gui = QHBoxLayout()
        self.button_filter = QPushButton("Применить фильтр")
        self.button_filter.clicked.connect(self.slot_filter)

        self.init_parameters_gui()

        self.button_set_original = QPushButton("Исходное изображение")
        self.button_set_original.clicked.connect(self.slot_set_original)
        self.layout_gui.addWidget(self.button_filter)
        self.layout_gui.addLayout(self.layout_parameters)
        self.layout_gui.addWidget(self.button_set_original)

        self.layout_main.addLayout(self.layout_gui)

        self.main_container = QWidget()
        self.main_container.setLayout(self.layout_main)
        self.setCentralWidget(self.main_container)

    def init_parameters_gui(self):
        self.layout_parameters = QVBoxLayout()

        self.label_low_pass = QLabel("Нижний порог")

        self.spin_low_pass = QSpinBox()
        self.spin_low_pass.setMinimum(1)
        self.spin_low_pass.setMaximum(1000)
        self.spin_low_pass.setValue(100)

        self.label_high_pass = QLabel("Верхний порог")

        self.spin_high_pass = QSpinBox()
        self.spin_high_pass.setMinimum(1)
        self.spin_high_pass.setMaximum(1000)
        self.spin_high_pass.setValue(300)

        self.layout_parameters.addWidget(self.label_low_pass)
        self.layout_parameters.addWidget(self.spin_low_pass)
        self.layout_parameters.addWidget(self.label_high_pass)
        self.layout_parameters.addWidget(self.spin_high_pass)

    def open_file(self):
        file_name = QFileDialog.getOpenFileName(filter='(*.png *.jpg)')
        self.pixmap = QPixmap(file_name[0])
        self.pixmap_clean = QPixmap(file_name[0])

        self.button_save.setDisabled(False)

        self.picture.installEventFilter(self)
        self.resize_set_pixmap()

    def save_file(self):
        if self.pixmap is None:
            return
        name = QFileDialog.getSaveFileName(filter='(*.png *.jpg)')
        image = self.pixmap.toImage()
        image.save(name[0])

    def slot_filter(self):
        if self.pixmap is None:
            return

        # making high pass grater than low
        if self.spin_low_pass.value() >= self.spin_high_pass.value():
            self.spin_low_pass.setValue(self.spin_high_pass.value()-1)

        # pixmap to numpy array
        image = self.pixmap.toImage()
        image_array = qimage2ndarray.rgb_view(image)

        filtered = cv2.Canny(image_array, self.spin_low_pass.value(), self.spin_high_pass.value())

        # numpy array to pixmap
        filtered_q_image = qimage2ndarray.array2qimage(filtered)
        filtered_q_pixmap = QPixmap.fromImage(filtered_q_image)

        self.pixmap = filtered_q_pixmap
        self.resize_set_pixmap()

    def slot_set_original(self):
        if self.pixmap is None:
            return
        self.pixmap = self.pixmap_clean
        self.resize_set_pixmap()

    def resize_set_pixmap(self):
        self.picture.setPixmap(self.pixmap.scaled(
            self.picture.width(), self.picture.height(),
            QtCore.Qt.KeepAspectRatio))

    def eventFilter(self, widget, event):
        # for dynamic picture resizing
        if event.type() == QtCore.QEvent.Resize and widget is self.picture:
            self.resize_set_pixmap()
            return True
        return super(MainWindow, self).eventFilter(widget, event)
