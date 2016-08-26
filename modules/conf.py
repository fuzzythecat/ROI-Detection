dir_data_cine = "../data/cine/"
dir_data_mask = "../data/mask/"
dir_data_patch = "../data/patch/"
dir_data_temp = "../data/_temp/"
dir_data = "../data/"

"""default time and z indices"""
default_t = 1
default_z = 7

"""slider options"""
slider_options = {}
slider_options["valinit"]   = 0
slider_options["closedmin"] = True
slider_options["closedmax"] = True
slider_options["dragging"]  = True

"""io load options"""
load_options = {}
load_options["initialdir"] = "~/Desktop/"
load_options["filetypes"]  = [("numpy files", ".npy")]
load_options["title"] = "load"


"""io save options"""
save_options = {}
save_options["initialdir"] = "~/Desktop/"
save_options["defaultextension"] = ".npy"
save_options["title"] = "save mask"


class MaskIoFormat(object):
    COM = None
    # list of Center of Mass coordinates
    # (y, x)

    frame_idx = None
    # list of frame(time) indices

    slice_idx = None
    # list of slice(z) indices

    endocardial_mask = None
    # list of numpy binary mask

    box_mask = None
    # list of numpy box-shapeed binary mask

    cine_data = None
    # list of 2d-original image slice

    def __init__(self):
        print("Initiating Data Save routine")
