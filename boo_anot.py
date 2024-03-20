import sys
from PyQt5.QtWidgets import QMessageBox, QApplication
from upater import Updater
from ui.anot_window import BooWindow
from qt_material import apply_stylesheet

def check_for_updates():
    Updater.build_file_path = 'build.updater'
    if Updater.check_for_update():
         reply = QMessageBox.question(None, 'Update Dialog', 'Do you want to update?',
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
    else:
        return
    if reply == QMessageBox.Yes:
        Updater.run_update_sequence()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    check_for_updates()
    apply_stylesheet(app, theme='./color_theme.xml')
    boo_anot_window = BooWindow()
    boo_anot_window.show()
    app.exec()