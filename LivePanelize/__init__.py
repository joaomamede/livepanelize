
__author__ = """João Mamede"""
__email__ = "jmamede@rush.edu"

import pims
import numpy as np
import dask
import dask.array
import warnings

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
    # reader = pims.TiffStack_pil(fn)
    reader = pims.bioformats.BioformatsReader(fn)
    reader.iter_axes = iterator  # 't' is the default already
    reader.bundle_axes = bundler
    print(reader)
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
    dtype = np.dtype(reader.pixel_type)


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
    a = a.reshape(143, 3, 2044, 2048)
    print(a.shape)
    return a


##MAIN HERE
import glob

filelist = glob.glob('/home/jmamede/Data/tet/tetMoon20201127/*ome.tiff')
filelist.sort()
all = []


all = dask.array.concatenate(
    [time_stack(filename,bundler='cyx') for filename in filelist]
, axis=3)

all
all = test.reshape(143, 3,2044, 8192)
# for ch in range(3):
#
#     all.append(dask.array.concatenate(
#     [time_stack(filename,ch=ch) for filename in filelist]
#     , axis=3))
# all = dask.array.stack(all,axis=1)


all


all
import napari
%gui qt
# napari.view_image(all[:,0,:,:,:])
v = napari.Viewer(show=False)
v.add_image(all[:,0,:,:,], contrast_limits=[0,5000],
            blending='additive',
            colormap='green',
            name='tetMoon-gp41GFP',#, is_pyramid=False
                 )
v.add_image(all[:,1,:,:], contrast_limits=[0,5000],
        blending='additive',
        colormap='red',
        name='IN-mRuby3',#, is_pyramid=False
             )
v.add_image(all[:,2,:,:], contrast_limits=[0,5000],
        blending='additive',
        colormap='blue',
        name='Nucspot650',#, is_pyramid=False
             )
v.show()


help(dask.delayed)
