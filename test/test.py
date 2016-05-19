import matplotlib
import sys
import numpy
import tkinter as tk
from tkinter import filedialog

#with open('a.txt', 'w') as f:
#    f.write('asdsfafsdsad')


sys.path.append ('../utils')
sys.path.append ('../modules')
sys.path.append ('../data/cine')

from conf import config_test
import img2mask

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilenames(filetypes=[('text files', '.txt')])

print (len(file_path))


#img = numpy.load('cinedata_1.npy')
#img2mask(img[:,:,1,1])
#config_test()
