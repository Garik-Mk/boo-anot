import os

def run_build():
    window_path = os.path.join('ui', 'main_window.ui')
    exe_path = os.path.join('ui', 'boo_anot_qt.py')
    os.system(f'pyuic5 {window_path} -o {exe_path}')

if __name__ == '__main__':
    run_build()