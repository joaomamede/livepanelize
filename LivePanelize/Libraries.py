import pims
import numpy as np
import dask
import dask.array
import warnings
import cupy as cp
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
    # BioformatsReader(filename, meta=True, java_memory='512m', read_mode='auto', series=0)
    # reader = pims.bioformats.BioformatsReader(fn,meta=False,java_memory='2048m')
    # reader.iter_axes = iterator  # 't' is the default already
    # reader.bundle_axes = bundler
    # print(reader)

    # reader.default_coords['c'] = ch
    # return reader
    print(fn)
    return pims.TiffStack_tifffile(fn)
    # return pims.open(fn)


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
    # print(pims_reader._filename)
    #The input "i" is a slice????
    # print("pims",i)
    return arrayfunc(pims_reader[i])


def time_stack(fn,ch=0, iterator='t',bundler='cyx',arraytype="numpy",**kwargs):
    if arraytype == "numpy":
        arrayfunc = np.asanyarray
    elif arraytype == "cupy":   # pragma: no cover
        import cupy
        arrayfunc = cupy.asanyarray

    # type(test)
    #you have to get the reader outside of here
    reader = initialize_reader(fn,
            ch=ch,iterator=iterator,bundler=bundler
            )

    shape = (len(reader),) + reader.frame_shape
    # shape = (3,143,2044,2048)
    dtype = np.dtype(reader.pixel_type)
    # print('Shapy',shape)


    a = []
    # print(type(a))
    for i in range(shape[0]):
        # print("loopy",i)
        a.append( dask.array.from_delayed(
            dask.delayed(_read_frame)(reader,i, arrayfunc=arrayfunc),
            shape[1:],
            dtype,
            meta=arrayfunc([])
        ))
    # print("out of loop")
    a = dask.array.stack(a)
    # a = a.reshape(143,3,2044, 2048)
    return a

def stitch(filelist,nrows=5,ncolumns=5,progression='snake'):
    import dask.array
    import dask
    pannel = []
    for i in range(ncolumns):
        if progression == 'straight':
            pannel.append(dask.array.concatenate(
                [time_stack(filename,bundler='cyx') for filename in filelist[i*nrows:i*nrows+nrows]]
            , axis=2)
            )
        elif progression == 'snake':
            #0 false any other # True
            if (i+1) % 2:
                print(i,'odd',filelist[i*nrows:i*nrows+nrows])
                pannel.append(dask.array.concatenate(
                    [time_stack(filename,bundler='cyx') for filename in filelist[i*nrows:i*nrows+nrows]]
                , axis=2)
                )
            else:
                print('even',np.flip(filelist[i*nrows:i*nrows+nrows]))
                pannel.append(dask.array.concatenate(
                    [time_stack(filename,bundler='cyx') for filename in np.flip(filelist[i*nrows:i*nrows+nrows])]
                , axis=2)
                )
    return dask.array.concatenate(pannel, axis=1)


# vmin=np.percentile(imgs[0],0.1),
# vmax=np.percentile(imgs[0],99.9)
def convert16to8bits(x,display_min=1000,display_max=65000):
    import cupy as cp
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
