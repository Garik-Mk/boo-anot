import sys
from PyQt5.QtWidgets import QMessageBox, QApplication
from updater import Updater
from main.anot_window import BooWindow
from main.quilt import synthesize_texture
from qt_material import apply_stylesheet

def check_for_updates():
    """
    Check for updates using the Updater class.

    If updates are available, it prompts the user with a dialog box asking if they want to update.
    If the user chooses to update, it runs the update sequence.
    """
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
    boo_anot_window = BooWindow()
    boo_anot_window.show()
    app.exec()
