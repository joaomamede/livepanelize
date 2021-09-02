from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
import pandas as pd
import tkinter as tk
import os
import re
import sys
# %gui qt

def launch_napari():
    import pims
    import numpy as np
    import dask
    import dask.array
    import warnings
    import cupy as cp
    import glob
    __author__ = """João Mamede"""
    __email__ = "jmamede@rush.edu"
    import Libraries

    filelist = glob.glob(folder_path.get() + "/*.ome.tiff")
    filelist.sort()
    all = Libraries.stitch(filelist,6,6,'snake')
    all8 = all.map_blocks(Libraries.convert16to8bits)
    all8
    #can't reshape I don't know why, resclicing was the only way I found
    green = all8[:-3:3]
    red = all8[1:-2:3]
    blue = all8[2:-1:3]
    green.shape

    #DETAIL IS HERE!!!!
    rgb = dask.array.stack([red,blue,green],axis=0)
    rgb
    rgb = rgb.compute()

    rgb.shape

    import napari

    rgb[2,2].shape
    # napari.view_image(all[:,0,:,:,:])


    # rmin = np.percentile(rgb[2,2].compute(),0.1)
    # rmax = np.percentile(rgb[2,2].compute(),99.5)
    # gmin = np.percentile(rgb[0,2].compute(),0.1)
    # gmax = np.percentile(rgb[0,2].compute(),99.5)
    # bmin = np.percentile(rgb[1,2].compute(),0.1)
    # bmax = np.percentile(rgb[1,2].compute(),99.5)

    rmin = np.percentile(rgb[2,2],0.1)
    rmax = np.percentile(rgb[2,2],99.5)
    gmin = np.percentile(rgb[0,2],0.1)
    gmax = np.percentile(rgb[0,2],99.5)
    bmin = np.percentile(rgb[1,2],0.1)
    bmax = np.percentile(rgb[1,2],99.5)


    with napari.gui_qt():
        v = napari.Viewer(show=True)
               # vmin=np.percentile(imgs[0],0.1),
               # vmax=np.percentile(imgs[0],99.9)
        v.add_image(rgb[2,:],
                    # rgb=True,
                    contrast_limits=[rmin,rmax],
                    blending='additive',
                    colormap='green',
                    name='HIV-iGFP',#, is_pyramid=False
                         )
        v.add_image(rgb[0,:], contrast_limits=[gmin,gmax],
                blending='additive',
                colormap='red',
                name='CA-mRuby3',#, is_pyramid=False
                     )
        v.add_image(rgb[1,:], contrast_limits=[bmin,bmax],
                blending='additive',
                colormap='blue',
                name='Nucspot650',#, is_pyramid=False
                     )


from tkinter import filedialog

from tkinter.scrolledtext import ScrolledText

import pandas as pd

import tkinter as tk

import os

import re

import sys

################ FUNCTIONS ################

def save_to_file(wordlist):
    """Save list to CSV format and save CSV to script directory"""
    script_directory = os.path.dirname(sys.argv[0]) # Path where script is being run from
    df = pd.DataFrame(data={"Results": wordlist})
    df.to_csv(script_directory+"/mycsv.csv", sep=",", index=False, line_terminator='\n')

def print_to_textbox(wordlist):
    """Print all lines in wordlist to textbox"""
    for lines in wordlist:
        text_box.insert("end", "\n"+lines)
    if len(wordlist) == 0:
        text_box.insert("1.0", "\nNothing To Display")

def browse_button():
    """Button will open a window for directory selection"""
    global folder_path
    selected_directory = filedialog.askdirectory()
    folder_path.set(selected_directory)

def search_files():
    """Search all files in specified directory"""
    folderPath = folder_path.get()
    searchString = string_entry.get()
    text_box.delete("1.0", tk.END)

    # Set word case option on/off.
    if var1.get() == 1:
        IGNOREWORDCASE = True
    else:
        IGNOREWORDCASE = False

    # List to store all lines where string is found.
    wordlist = []

    # Loop through all files and search for string, line by line.
    for (path, directories, files) in os.walk(folderPath, topdown=True):
        for file in files:
            filepath = os.path.join(path, file)

            try:

                with open(filepath, 'r') as currentfile:
                        for lineNum, line in enumerate(currentfile, 1):
                            line = line.strip()
                            match = re.search(searchString, line, re.IGNORECASE) if IGNOREWORDCASE else re.search(searchString, line)
                            if match:
                                word = f"Word '{searchString}' in '{file}' on line {lineNum}: {line}"
                                wordlist.append(word)

            except IOError as ex:
                words = f"Error; {file}; {ex}"
                wordlist.insert(0, words)

            except EnvironmentError as ex:
                words = f"Error; {file}; {ex}"
                wordlist.insert(0, words)

            except OSError as ex:
                words = f"Error; {file}; {ex}"
                wordlist.insert(0, words)

            except UnicodeDecodeError as ex:
                words = f"Error; {file}; {ex}"
                wordlist.insert(0, words)

            except:
                words = f"Error; {file}"
                wordlist.insert(0, words)

    # Print all lines to text box.
    print_to_textbox(wordlist)

    # Save to file.
    save_to_file(wordlist)

################ TKINTER SCRIPT ################

# Setup Window.
window = tk.Tk()
window.geometry("900x500")
window.title("String Search")

# Button to select directory.
select_directory = tk.Button(window, text = "Select Directory", command=browse_button)
select_directory.pack()

# Label to store chosen directory.
folder_path = tk.StringVar()
directory_label = tk.Label(window, textvariable = folder_path, bg="#D3D3D3", width=70)
directory_label.pack()

# Entry to type search string.
string_entry = tk.Entry(window, bg="#D3D3D3")
string_entry.pack()

# Check button to turn ignore case on/off.
var1 = tk.IntVar()
stringCase_select = tk.Checkbutton(window, text='Ignore Case',variable=var1, onvalue=1, offvalue=0)
stringCase_select.pack()

var_on_the_fly = tk.IntVar()
stringCase_select = tk.Checkbutton(window, text='Tick for on-the-fly',variable=var_on_the_fly, onvalue=1, offvalue=0)
stringCase_select.pack()

# Button to run main script.
go_button = tk.Button(window, text="Search and Verify Files", command=search_files)
go_button.pack()

# Button to run main script.
panel_button = tk.Button(window, text="Run Napari w/ Files", command=launch_napari)
panel_button.pack()

# Button to quit the app.
quit_button = tk.Button(window, text = "Quit", command=window.quit)
quit_button.pack()

# Text box to display output of main text.
text_box = ScrolledText(width=110, borderwidth=2, relief="sunken", padx=20)
text_box.pack()

# Button to clear the text box display.
clear_button = tk.Button(window, text = "Clear", command = lambda: text_box.delete("1.0", tk.END))
clear_button.pack()

# Run an event loop.
window.mainloop()
