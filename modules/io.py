from modules import conf

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
