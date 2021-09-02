import pims
import numpy as np
import dask
import dask.array
import warnings
import cupy as cp
import glob
__author__ = """João Mamede"""
__email__ = "jmamede@rush.edu"
import sys
sys.path.insert(0,'/home/jmamede/scripts/LivePanelize')
import Libraries

filelist = glob.glob('/home/jmamede/Data/CaRuby3/20210128MDM/*tiff')
filelist.sort()

# all = []
filelist

all = Libraries.stitch(filelist,6,6)
all8 = all.map_blocks(Libraries.convert16to8bits)
all8
#can't reshape I don't know why, resclicing was the only way I found
#fortime
green = all8[:-3:3]
red = all8[1:-2:3]
blue = all8[2:-1:3]
green.shape

# (1, 35, 520, 692, 1)
# green = [dask.array.moveaxis(green, 0, -1)]
# green.shape
# green.reshape(5120,5120,119)
# rgb = dask.array.stack([red,blue,green],axis=0)
# rgb = rgb.reshape(3,6144,6144)
rgb = all8


all8[0]


# rgb = dask.array.stack([red,blue,green],axis=0)
rgb = rgb.compute()

def export():
    plt.imshow(rgb[1,3,:2044,:2048])
    import tifffile as tf
    with tf.TiffWriter("/home/jmamede/Data/test.tiff",
                        bigtiff=True,
                        imagej=False,) as tif:
        for time in range(rgb.shape[1]):
             tif.save(rgb[:,time,:,:].compute(),
                    compress= 3,
                    photometric='minisblack',
                    metadata= None,
                    contiguous=False,
                )
    tif.close()

import napari
%gui qt
rgb
# napari.view_image(all[:,0,:,:,:])
from naparimovie import Movie
v = napari.Viewer(show=True)
       # vmin=np.percentile(imgs[0],0.1),
       # vmax=np.percentile(imgs[0],99.9)
v.add_image(rgb[0,...],
            # rgb=True,
            contrast_limits=[0,255],
            blending='additive',
            colormap='green',
            name='tetMoon-gp41GFP',#, is_pyramid=False
                 )
v.add_image(rgb[1,...], contrast_limits=[0,255],
        blending='additive',
        colormap='red',
        name='IN-mRuby3',#, is_pyramid=False
             )
v.add_image(rgb[2,...], contrast_limits=[0,255],
        blending='additive',
        colormap='blue',
        name='Nucspot650',#, is_pyramid=False
             )



movie = Movie(myviewer=v)
v.show()
movie.inter_steps = 15
movie.make_movie(name='/tmp/test.mp4',resolution = 300, fps=20)
