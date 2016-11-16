import os
import sys
from modules import conf


def init_mask_io_format(**kwargs):
    """
    initiates and returns a dictionary
    mask instance of ROI-IO format.

    The following keys in the dictionary represent:
    COM : A list of Center Of Mass of each 2-d image slice.
    frame_idx : A list of frame(time) indices.
    slice_idx : A list of slicie(z) indices.
    endocardial_mask : A list of 2-d numpy binary mask.
    box_mask : A list of numpy box-shaped binary mask
    cine_data : A list of 2-d original image slice

    Returns
    -------
    data : A dictionary instance of ROI-IO format.
    """
    data = {
        "COM": [],
        "frame_idx": [],
        "slice_idx": [],
        "slice_idx": [],
        "endocardial_mask": [],
        "box_mask": [],
        "cine_data": [],
        "subject_idx": []}

    return data


def load_cine_from_directory(cinedir):
    """
    Integrates 2-dimensional dicom slices from cine directory
    into 4-dimensional numpy array.

    Parameters
    ----------
    cinedir : Working directory where the slices are located.

    Returns
    -------
    cine_img : 4-dimensional integrated numpy array.
    """
    import dicom
    import numpy as np

    os.chdir(cinedir)
    session_files = os.listdir()

    zslice = 0
    cine_series = []

    for f in session_files:
        if("DS" in f): continue
        if len(f) <= 3:
            cine_series.append(f)
            zslice += 1

    zcount = 0
    print("loading cine data", end="")
    mod = int((zslice/5)+0.5)

    for i in range(0, zslice):
        cwdir = cinedir + cine_series[i]
        os.chdir(cwdir)
        session_files = os.listdir()

        if(i % (mod) == 0):
            print(".", end="", flush=True)

        tcount = 0
        for f in session_files:
            if("DS" in f): continue
            ds = dicom.read_file(f)
            if zcount == 0 and tcount == 0:
                pixelDims = (int(ds.Rows),
                        int(ds.Columns), int(30), int(zslice))
                cine_img = np.zeros(pixelDims, dtype=ds.pixel_array.dtype)

            cine_img[:, :, tcount, zcount] = ds.pixel_array
            tcount += 1
        zcount += 1

    print(" complete")
    print("data dimension: ", end="")
    print(cine_img.shape)

    return cine_img


def get_directory(**kwargs):
    """
    Wrapper function for PyQt4.QtGui.QFileDialog.getExistingDirectory().
    Returns the absolute directory of the chosen directory.

    Parameters
    ----------
    None

    Returns
    -------
    filename : string of absolute directory.
    """
    from PyQt4 import QtGui

    filename = str(QtGui.QFileDialog.getExistingDirectory())

    return filename


def get_file_path(**kwargs):
    """
    Wrapper function for PyQt4.QtGui.QFileDialog.getOpenFileName().
    Retreives name and directory of file to be opened.

    Parameters
    ----------
    (optional)
    initialdir : Initial directory displayed in file dialog.
    Defaults to /data directory.

    filetypes : Sequence of (label, pattern) tuples. Use '*' as the pattern
    to indicate all files. Defaults to ('numpy files', '.npy').

    Returns
    -------
    filename : 1-dimensional string of
    absolute directory + name of the selected file.
    """
    from PyQt4 import QtGui

    filename = QtGui.QFileDialog.getOpenFileName()

    return filename


def get_file_paths(**kwargs):
    """
    Wrapper function for PyQt4.QtGui.QFileDialog.getOpenFileNames().
    Retreives name and directory of file to be opened.

    Parameters
    ----------
    (optional)
    initialdir : Initial directory displayed in file dialog.
    Defaults to /data directory.

    filetypes : Sequence of (label, pattern) tuples. Use '*' as the pattern
    to indicate all files. Defaults to ('numpy files', '.npy').

    Returns
    -------
    filename : 2-dimensional string of
    absolute directory + name of the selected file.
    """

    from PyQt4 import QtGui

    filename = QtGui.QFileDialog.getOpenFileNames()

    return filename


def save_file_dialog(**kwargs):
    """
    Wrapper function for PyQt4.QtGui.QFileDialog.getSaveFileName()
    Retreives name and directory of file to be saved.

    Parameters
    ----------
    (optional)
    initialdir : Initial directory displayed in file dialog.
    Defaults to /data directory.

    defaultextension : Extension of the file to be saved.
    Defaults to '.npy'

    Returns
    -------
    filename : 1-dimensional string of
    absolute directory + name of the file to be saved.
    """

    from PyQt4 import QtGui

    filename = QtGui.QFileDialog.getSaveFileName()

    return filename


def retreive_filename(path):
    """
    Truncates absolute file directory and returns file name.

    Parameters
    ----------
    path : 1-dimensional string containing absolute directory of a file,
    in /<dir>/<filename>.<foramt> format.

    Returns
    -------
    filename : <filename> portion of the given file directory.
    """

    token = path.split('/')
    filename = token[-1].split('.')[0]

    return filename

if __name__ == "__main__":
    pass
