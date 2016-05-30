def get_file_path(**kwargs):
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename as open_file
    import conf

    path = kwargs.pop("path", conf.dir_data_cine)

    root = Tk()
    root.withdraw()
    file_path = open_file(filetypes=[('numpy array', '.npy')], \
                          initialdir=path)

    return file_path

def get_file_paths(**kwargs):
    from tkinter import Tk
    from tkinter.filedialog import askopenfilenames as open_files
    import conf

    path = kwargs.pop("path", conf.dir_data_cine)

    root = Tk()
    root.withdraw()
    file_path = open_files(filetypes=[('numpy array', '.npy')], \
                           initialdir=path)

    return file_path

def save_file_dialog(**kwargs):
    import conf
    from tkinter.filedialog import asksaveasfilename as save_file

    path = kwargs.pop("path", conf.dir_data_mask)

    filename = save_file(defaultextension=".npy", initialdir=path)
    if filename is None:
        """save_file returns 'None' if dialog closed with 'cancel'"""
        return

    return filename

if __name__ == "__main__":

    save_file_dialog()


