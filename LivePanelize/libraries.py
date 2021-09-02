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
    # BioformatsReader(filename, meta=True, java_memory='512m', read_mode='auto', series=0)
    # reader = pims.bioformats.BioformatsReader(fn,meta=False,java_memory='2048m')
    # reader.iter_axes = iterator  # 't' is the default already
    # reader.bundle_axes = bundler
    # print(reader)

    # reader.default_coords['c'] = ch
    # return reader
    return pims.TiffStack_tifffile(fn)

def initialize_reader_bioformats(fn,iterator='t',bundler='cyx', ch = None, **kwargs):
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

    # reader = pims.bioformats.BioformatsReader(filename, meta=True, java_memory='512m', read_mode='auto', series=0)
    reader = pims.bioformats.BioformatsReader(fn,meta=False,java_memory='2048m')
    reader.iter_axes = iterator  # 't' is the default already
    reader.bundle_axes = bundler
    # print(reader)
    if ch not None:
        reader.default_coords['c'] = ch
    # return pims.TiffStack_tifffile(fn)
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
    #test
    # a = a.reshape((1,)+shape)
    return a
