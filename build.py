import os

def run_build():
    os.system(r'pyuic5 ui\main_window.ui -o ui\boo_anot_qt.py')

if __name__ == '__main__':
    run_build()