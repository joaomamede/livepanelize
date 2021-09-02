from pims import FramesSequenceND
import numpy as np
import pims
f = '/home/jmamede/Data/tet/tetMoon20201127/D11tetMoon_opti0.5ruby24RV_250ul_VitC_PBN_spin16C_nucSPOT_3_v1_PRJ.ome.tiff'

a = pims.TiffStack_tifffile(f)
from pims import FramesSequence, Frame

class MyReader(FramesSequence):

    def __init__(self, filename):
        self.filename = filename
        self._len =  143
        self._dtype =  np.uint16
        self._frame_shape =  (2044,2048)
        self._init_axis('x', 2044)
        self._init_axis('y', 2048)
        self._init_axis('c', 3)
        self._init_axis('t', 143)
        self._init_axis('z', 1)
        # Do whatever setup you need to do to be able to quickly access
        # individual frames later.

    def get_frame(self, i):
        # Access the data you need and get it into a numpy array.
        # Then return a Frame like so:
        return Frame(my_numpy_array, frame_no=i)

     def __len__(self):
         return self._len

     @property
     def frame_shape(self):
         return self._frame_shape

     @property
     def pixel_type(self):
         return self._dtype
class IndexReturningReader(FramesSequenceND):
   @property
   def pixel_type(self):
       return np.uint8  # the pixel datatype

   def __init__(self, size_c, size_t, size_z):
       # first call the baseclass initialization
       super(IndexReturningReader, self).__init__()
       self._init_axis('x', 3)
       self._init_axis('y', 1)
       self._init_axis('c', size_c)
       self._init_axis('t', size_t)
       self._init_axis('z', size_z)
       # register the get_frame function
       self._register_get_frame(self.get_frame_func, 'yx')

   def get_frame_func(self, c, t, z):
       return np.array([[c, t, z]], dtype=np.uint8)


class TiffStack_tifffileJM(FramesSequenceND):
    """Read TIFF stacks (single files containing many images) into an
    iterable object that returns images as numpy arrays.

    This reader, based on tiffile.py, should read standard TIFF
    files and sundry derivatives of the format used in microscopy.

    Parameters
    ----------
    filename : string
    process_func : function, optional
        callable with signalture `proc_img = process_func(img)`,
        which will be applied to the data from each frame
    dtype : numpy datatype, optional
        Image arrays will be converted to this datatype.
    as_grey : boolean, optional
        Convert color images to greyscale. False by default.
        May not be used in conjection with process_func.

    Examples
    --------
    >>> video = TiffStack('many_images.tif')  # or .tiff
    >>> imshow(video[0]) # Show the first frame.
    >>> imshow(video[-1]) # Show the last frame.
    >>> imshow(video[1][0:10, 0:10]) # Show one corner of the second frame.

    >>> for frame in video[:]:
    ...    # Do something with every frame.

    >>> for frame in video[10:20]:
    ...    # Do something with frames 10-20.

    >>> for frame in video[[5, 7, 13]]:
    ...    # Do something with frames 5, 7, and 13.

    >>> frame_count = len(video) # Number of frames in video
    >>> frame_shape = video.frame_shape # Pixel dimensions of video

    Note
    ----
    This wraps tifffile.py. It should deal with a range of
    tiff files and sundry microscope related tiff derivatives.
    The obvious thing to do here is to extend tifffile.TiffFile;
    however that would over-ride our nice slicing sematics. The
    way that TiffFile deals with __getitem__ is to just pass it
    through to an underlying list.  Further, it return TiffPages,
    not arrays as we desire.

    See Also
    --------
    TiffStack_pil, TiffStack_libtiff, ImageSequence
    """
    @classmethod
    def class_exts(cls):
        # TODO extend this set to match reality
        return {'tif', 'tiff', 'lsm',
                'stk'} | super(TiffStack_tifffile, cls).class_exts()

    def __init__(self, filename, process_func=None, dtype=None,
                 as_grey=False):
        self._filename = filename
        record = tifffile.TiffFile(filename).series[0]
        if hasattr(record, 'pages'):
            self._tiff = record.pages
        else:
            self._tiff = record['pages']

        tmp = self._tiff[0]
        if dtype is None:
            self._dtype = tmp.dtype
        else:
            self._dtype = dtype

        self._im_sz = tmp.shape

        self._validate_process_func(process_func)
        self._as_grey(as_grey, process_func)

    def get_frame(self, j):
        t = self._tiff[j]
        data = t.asarray()
        return Frame(self.process_func(data).astype(self._dtype),
                      frame_no=j, metadata=self._read_metadata(t))

    def _read_metadata(self, tiff):
        """Read metadata for current frame and return as dict"""
        md = {}
        try:
            md["ImageDescription"] = (
                tiff.tags["image_description"].value.decode())
        except:
            pass
        try:
            dt = tiff.tags["datetime"].value.decode()
            md["DateTime"] = _tiff_datetime(dt)
        except:
            pass
        try:
            md["Software"] = tiff.tags["software"].value.decode()
        except:
            pass
        try:
            md["DocumentName"] = tiff.tags["document_name"].value.decode()
        except:
            pass
        return md

    @property
    def pixel_type(self):
        return self._dtype

    @property
    def frame_shape(self):
        return self._im_sz

    def __len__(self):
        return len(self._tiff)

    def __repr__(self):
        # May be overwritten by subclasses
        return """<Frames>
Source: {filename}
Length: {count} frames
Frame Shape: {frame_shape!r}
Pixel Datatype: {dtype}""".format(frame_shape=self.frame_shape,
                                  count=len(self),
                                  filename=self._filename,
                                  dtype=self.pixel_type)
