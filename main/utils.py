import os
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

UTILS_BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def list_files(directory: str, same_folder: bool=False, remove_extensions=False, npy=False) -> dict:
    """
    List files with specified image extensions in the given directory.

    Args:
        directory: The directory path to search for image files.
        same_folder: Are the labels and images in same folder

    Returns:
        A dictionary containing file names as keys and their
        corresponding paths as values.
    """
    dir_dict = {}
    # Add more extensions if needed
    if npy:
        image_extensions = {'.npy'}
    else:
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in image_extensions:
                if same_folder:
                    display_name = file
                else:
                    display_name = os.path.basename(root)\
                    + '__' + file
                if remove_extensions:
                    display_name = os.path.splitext(display_name)[0]
                dir_dict[display_name] = (os.path.join(root, file))
    return dir_dict


def replace_extension_with_txt(file_path: str) -> str:
    """
    Replace the extension of the given file with '.txt'.

    Args:
        file_path: The path of the file whose extension needs to be replaced.

    Returns:
        The file path with the extension replaced by '.txt'.
    """
    base_name, _ = os.path.splitext(file_path)
    return base_name + '.txt'


def magnitude(chirp, radar_data_type='RI'):
    """ Calculate magnitude of a chirp

    Args:
        chirp: np.array
            radar data of one chirp (w x h x 2) or (2 x w x h)

        radar_data_type: str
            current available types include 'RI', 'RISEP', 'AP', 'APSEP'

    Returns:
        Magnitude map for the input chirp (w x h)
    """
    c0, c1, c2 = chirp.shape
    if radar_data_type == 'RI' or radar_data_type == 'RISEP':
        if c0 == 2:
            chirp_abs = np.sqrt(chirp[0, :, :] ** 2 + chirp[1, :, :] ** 2)
        elif c2 == 2:
            chirp_abs = np.sqrt(chirp[:, :, 0] ** 2 + chirp[:, :, 1] ** 2)
        else:
            raise ValueError
    elif radar_data_type == 'AP' or radar_data_type == 'APSEP':
        if c0 == 2:
            chirp_abs = chirp[0, :, :]
        elif c2 == 2:
            chirp_abs = chirp[:, :, 0]
        else:
            raise ValueError
    else:
        raise ValueError
    return chirp_abs


def open_npy_image(npy_file_path):
    """Open given npy file as qpixmap object

    Args:
        npy_file_path: str
            Path to the file
    """
    tmp_file = os.path.join(UTILS_BASE_PATH, "temp.png")
    os.remove(tmp_file)
    numpy_array = np.load(npy_file_path)
    chirp_abs = magnitude(numpy_array)
    plt.imshow(chirp_abs, origin='lower')
    plt.colorbar()
    plt.savefig(tmp_file)
    plt.close()
    newpxmap = QPixmap(tmp_file)
    return newpxmap


class ImageWrapper():
    def __init__(self, qlabel: QLabel) -> None:
        self.qlabel = qlabel
        self.x = 0
        self.y = 0
        self.depth_level = 0
    

    def __repr__(self) -> str:
        return f'x: {self.x}, y: {self.y}, depth: {self.depth_level}'
