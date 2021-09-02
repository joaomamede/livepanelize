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

# filelist = glob.glob('/home/jmamede/Data/CaRuby3/20210128MDM*tiff')
filelist = glob.glob('/run/media/jmamede/Joao/CAruby/20210406mdm-WOWO/*ome.tiff')
filelist.sort()

# all = []
filelist
all = Libraries.stitch(filelist,9,5)
all8 = all.map_blocks(Libraries.convert16to8bits)
all8 = all
#can't reshape I don't know why, resclicing was the only way I found
green = all8[:-3:3]
red = all8[1:-2:3]
blue = all8[2:-1:3]
green.shape

#DETAIL IS HERE!!!!
rgb = dask.array.stack([red,blue,green],axis=0)
rgb
rgb = rgb[:,:,...].compute()

rgb.shape

import napari
%gui qt
rgb[2,2].shape
# napari.view_image(all[:,0,:,:,:])


# rmin = np.percentile(rgb[2,2].compute(),0.1)
# rmax = np.percentile(rgb[2,2].compute(),99.5)
# gmin = np.percentile(rgb[0,2].compute(),0.1)
# gmax = np.percentile(rgb[0,2].compute(),99.5)
# bmin = np.percentile(rgb[1,2].compute(),0.1)
# bmax = np.percentile(rgb[1,2].compute(),99.5)
#
# rmin = np.percentile(rgb[2,2],0.5)
# rmax = np.percentile(rgb[2,2],99.9)
# gmin = np.percentile(rgb[0,2],0.5)
# gmax = np.percentile(rgb[0,2],99.9)
# bmin = np.percentile(rgb[1,2],0.5)
# bmax = np.percentile(rgb[1,2],99.9)

rmin = 1000
rmax = 15000
gmin = 1000
gmax = 15000
bmin = 1000
bmax = 30000


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
from napari_animation import AnimationWidget

animation_widget = AnimationWidget(viewer)
viewer.window.add_dock_widget(animation_widget, area='right')



from naparimovie import Movie
help(Movie)
movie = Movie(myviewer=v)
v.show()
movie.inter_steps = 15
movie.make_movie(name='/tmp/test.mp4',resolution = 300, fps=20)
