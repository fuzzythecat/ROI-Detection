def get_file_path(**kwargs):
    """
    Wrapper function for tkinter.filedialog askopenfilename. Retreives
    name and directory of file to be opened.

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

    from tkinter import Tk
    from tkinter.filedialog import askopenfilename
    import conf

    options = {}
    options["initialdir"] = kwargs.pop("initialdir", conf.dir_data)
    options["filetypes"] = kwargs.pop("filetypes", ('numpy files', '.npy'))

    root = Tk()
    root.withdraw()

    filename = askopenfilename(**options)

    return filename


def get_file_paths(**kwargs):
    """
    Wrapper function for tkinter.filedialog askopenfilenames. Retreives
    names and directories of files to be opened.

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

    from tkinter import Tk
    from tkinter.filedialog import askopenfilenames
    import conf

    options = {}
    options["initialdir"] = kwargs.pop("initialdir", conf.dir_data)
    options["filetypes"] = kwargs.pop("filetypes", [("numpy files", ".npy")])

    root = Tk()
    root.withdraw()

    filename = askopenfilenames(**options)

    return filename


def save_file_dialog(**kwargs):
    """
    Wrapper function for tkinter.filedialog asksaveasfilename. Retreives
    name and directory of file to be saved.

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

    import conf
    from tkinter.filedialog import asksaveasfilename

    options = {}
    options["initialdir"] = kwargs.pop("initialdir", conf.dir_data)
    options["defaultextension"] = kwargs.pop("defaultextension", ".npy")

    filename = asksaveasfilename(**options)

    # asksaveasfilename returns 'None' if dialog closed with 'cancel'
    if filename is None:
        return

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

    retreive_filename("/dir/filenameishere.npy")
