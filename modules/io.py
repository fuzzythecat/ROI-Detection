import os
import sys
from modules import conf

def load_cine_from_directory(cinedir):
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

    for i in range(0, zslice):
        # print("cine series: %s" % cine_series[i])
        cwdir = cinedir + cine_series[i]
        os.chdir(cwdir)
        session_files = os.listdir()
        # print(session_files)

        if(i % (zslice/5) == 0):
            print(".", end="", flush=True)

        tcount = 0
        for f in session_files:
            if("DS" in f): continue
            ds = dicom.read_file(f)
            # print(ds.PatientName+ds.Rows+ds.Columns)
            if zcount == 0 and tcount == 0:
                pixelDims = (int(ds.Rows),
                        int(ds.Columns), int(30), int(zslice))
                cine_img = np.zeros(pixelDims, dtype=ds.pixel_array.dtype)

            cine_img[:, :, tcount, zcount] = ds.pixel_array
            tcount += 1
        zcount += 1

    print("\ndata dimension: ", end="")
    print(cine_img.shape)

    return cine_img


def get_directory(**kwargs):
    """
    Wrapper function for PyQt4.QtGui.QFileDialog.getExistingDirectory().
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
