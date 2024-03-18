import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 400, 300)
        self.showFullScreen()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout to hold the label
        layout = QVBoxLayout(central_widget)

        # Load the image
        pixmap = QPixmap("download.jpeg")  # Replace "your_image.jpg" with the path to your image

        # Create a label and set the pixmap as its content
        label = QLabel()
        label.setPixmap(pixmap)

        # Add the label to the layout
        layout.addWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
