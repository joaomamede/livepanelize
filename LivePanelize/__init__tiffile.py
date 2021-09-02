import pims
import numpy as np
import dask
import dask.array
import warnings
__author__ = """João Mamede"""
__email__ = "jmamede@rush.edu"

def initialize_reader(fn,iterator='t',bundler='cyx', ch =0, **kwargs):
    """
    Read File and returns a pims object while allowing to set iterator and
    frame shape output

    Parameters
    ----------
    fn : str
        A string with one or multiple filenames, read pims multireader
        for details.
    iterator: str
        slice to iterate, defaults to time 't'.
    bundler: str
        slice shape to output, defaults to 'yx'.
    ch:  int
        only output a one channel as default, defaults to 0.

    Returns
    -------
    array : pims.bioformats.BioformatsReader
        A pims reader to access the contents of all image files in
        the predefined channel
    """

    # reader = pims.open(fn)
    reader = pims.TiffStack_tifffile(fn)
    # BioformatsReader(filename, meta=True, java_memory='512m', read_mode='auto', series=0)
    # reader = pims.bioformats.BioformatsReader(fn,meta=False,java_memory='2048m')
    # reader.iter_axes = iterator  # 't' is the default already
    # reader.bundle_axes = bundler
    # print(reader)

    # reader.default_coords['c'] = ch
    return reader

def _read_frame(pims_reader,i, arrayfunc=np.asanyarray,**kwargs):
    """
    Read File and returns a pims object while allowing to set
    iterator and frame shape output.

    Parameters
    ----------
    pims_reader : object
        Pims reader object
    i: int
        the file coordinate to output as selected by the initializer
        iterator and default channel

    Returns
    -------
    array : pims.frame.Frame
        Array with the data in the reader current
        shape and default_coords.
    """
    print("Frame shape", arrayfunc(pims_reader[i]).shape )
    #The input "i" is a slice????
    return arrayfunc(pims_reader[i])


def time_stack(fn,nframes=1, ch=0, iterator='t',bundler='cyx',arraytype="numpy",**kwargs):
    if arraytype == "numpy":
        arrayfunc = np.asanyarray
    elif arraytype == "cupy":   # pragma: no cover
        import cupy
        arrayfunc = cupy.asanyarray

    # type(test)
    reader = initialize_reader(fn,
            ch=ch,iterator=iterator,bundler=bundler
            )

    shape = (len(reader),) + reader.frame_shape
    # shape = (3,143,2044,2048)
    dtype = np.dtype(reader.pixel_type)
    # print('Shapy',shape)

    if nframes == -1:
        nframes = shape[0]

    if nframes > shape[0]:
        warnings.warn(
            "`nframes` larger than number of frames in file."
            " Will truncate to number of frames in file.",
            RuntimeWarning
        )
    elif shape[0] % nframes != 0:
        warnings.warn(
            "`nframes` does not nicely divide number of frames in file."
            " Last chunk will contain the remainder.",
            RuntimeWarning
        )

    import itertools
    lower_iter, upper_iter = itertools.tee(itertools.chain(
        range(0, shape[0], nframes),
        [shape[0]]
    ))
    next(upper_iter)

    a = []
    # print(type(a))
    for i, j in zip(lower_iter, upper_iter):

        a.append( dask.array.from_delayed(
            dask.delayed(_read_frame)(reader,slice(i,j), arrayfunc=arrayfunc),
            (j - i,) + shape[1:],
            dtype,
            meta=arrayfunc([])
        ))

    a = dask.array.stack(a)
    # print(a.shape)
    # a = a.reshape(143,3,2044, 2048)
    return a


##MAIN HERE
import glob

filelist = glob.glob('/home/jmamede/Data/tet/tetMoon20201127/*ome.tiff')
filelist.sort()
# all = []
# filelist

row1 = dask.array.concatenate(
    [time_stack(filename,bundler='cyx') for filename in filelist[0:6]]
, axis=3)
row1 = row1.reshape(429,2044,2048*6)
row2 = dask.array.concatenate(
    [time_stack(filename,bundler='cyx') for filename in filelist[6:12]]
, axis=3)
row2 = row2.reshape(429,2044,2048*6)
row3= dask.array.concatenate(
    [time_stack(filename,bundler='cyx') for filename in filelist[12:18]]
, axis=3)
row3 = row3.reshape(429,2044,2048*6)
row4 = dask.array.concatenate(
    [time_stack(filename,bundler='cyx') for filename in filelist[18:24]]
    , axis=3)
row4 = row4.reshape(429,2044,2048*6)
row5 = dask.array.concatenate(
    [time_stack(filename,bundler='cyx') for filename in filelist[24:30]]
, axis=3)
row5 = row5.reshape(429,2044,2048*6)

all = dask.array.concatenate([row1,row2,row3,row4,row5], axis=1)
# all = dask.array.concatenate([row1,row2,row3,row4], axis=1)

all[0].compute()
# # all= row1
# import cupy as cp
# def cupy_to_numpy(x):
#     import cupy as cp
#     return cp.asnumpy(x)
#
# all = row1.map_blocks(cupy_to_numpy, meta=row1)
# # all= row1
# import cupy as cp
import cupy as cp
def convert16to8bits(x,display_min=100,display_max=500):
    # import cupy as cp
    def display(image, display_min, display_max): # copied from Bi Rico
    # Here I set copy=True in order to ensure the original image is not
    # modified. If you don't mind modifying the original image, you can
    # set copy=False or skip this step.
        # image = cp.array(image, copy=FalseTrue)
        image.clip(display_min, display_max, out=image)
        image -= display_min
        cp.floor_divide(image, (display_max - display_min + 1) / 256,
                        out=image, casting='unsafe')
        return image.astype(cp.uint8)

    lut = cp.arange(2**16, dtype='uint16')
    lut = display(lut, display_min, display_max)
    return cp.asnumpy(cp.take(lut, x))


shape_example = time_stack(filelist[0],bundler='cyx', nframes=)
shape_example[0].compute
all8 = all.map_blocks(convert16to8bits, meta=shape_example)

a = np.array((429,1,2044,2048))
green = all8[:-3:3].compute()
green.shape
red = all8[1:-2:3].compute()
red
blue = red = all8[2:-1:3].compute()

all8 = all

import napari
%gui qt

# napari.view_image(all[:,0,:,:,:])
from naparimovie import Movie
v = napari.Viewer(show=True)
v.add_image(all8[0:-3:3,:,:,], contrast_limits=[0,500],
            blending='additive',
            colormap='green',
            name='tetMoon-gp41GFP',#, is_pyramid=False
                 )
v.add_image(all8[1:-2:3,:,:], contrast_limits=[0,500],
        blending='additive',
        colormap='red',
        name='IN-mRuby3',#, is_pyramid=False
             )
v.add_image(all8[2:-1:3,:,:], contrast_limits=[0,1500],
        blending='additive',
        colormap='blue',
        name='Nucspot650',#, is_pyramid=False
             )



movie = Movie(myviewer=v)
v.show()
movie.inter_steps = 15
movie.make_movie(name='/tmp/test.mp4',resolution = 300, fps=20)
