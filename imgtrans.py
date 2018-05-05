
from __future__ import print_function , division


from ctypes import c_int, c_void_p, c_char, cdll, c_uint64, c_uint16
from ctypes import POINTER, byref
import numpy as np, zlib

_imgtrans = cdll.LoadLibrary("./_imgtrans.so")
_imgtrans = cdll.LoadLibrary("./_imgtrans_omp.so")

setLUT = _imgtrans.setLUT
setLUT.argtypes = [ c_int, c_int, c_int ]

_rebin2 = _imgtrans.rebin2
_rebin2.argtypes = [ c_void_p, c_int, c_int, c_void_p ]

_rebin3 = _imgtrans.rebin3
_rebin3.argtypes = [ c_void_p, c_int, c_int, c_void_p ]

_rebin4 = _imgtrans.rebin4
_rebin4.argtypes = [ c_void_p, c_int, c_int, c_void_p ]

_imgsum = _imgtrans.imgsum
_imgsum.argtypes = [ c_void_p, c_int ]
_imgsum.restype = c_uint64

_imgstats = _imgtrans.imgstats
_imgstats.argtypes = [ c_void_p, c_int,
                       POINTER(c_uint64),
                       POINTER(c_uint64),
                       POINTER(c_uint16),
                       POINTER(c_uint16) ]

LUT = ( c_char*65536 ).in_dll( _imgtrans, "LUT" )

def rebin2(img, out):
    assert out.shape[0] == img.shape[0]//2
    assert out.shape[1] == img.shape[1]//2
    assert img.dtype == np.uint16
    assert out.dtype == np.uint8
    _rebin2(img.ctypes.data, img.shape[0], img.shape[1], out.ctypes.data)

def rebin3(img, out):
    assert out.shape[0] == img.shape[0]//3
    assert out.shape[1] == img.shape[1]//3
    assert img.dtype == np.uint16
    assert out.dtype == np.uint8
    _rebin3(img.ctypes.data, img.shape[0], img.shape[1], out.ctypes.data)

def rebin4(img, out):
    assert out.shape[0] == img.shape[0]//4
    assert out.shape[1] == img.shape[1]//4
    assert img.dtype == np.uint16
    assert out.dtype == np.uint8
    _rebin4(img.ctypes.data, img.shape[0], img.shape[1], out.ctypes.data)

def imgsum(img):
    assert img.dtype == np.uint16
    return _imgsum( img.ctypes.data, len(img.flat) )

def imgstats(img):
    assert img.dtype == np.uint16
    sm = c_uint64(0)
    sm2 = c_uint64(0)
    mx = c_uint16(0)
    mn = c_uint16(0)
    _imgstats( img.ctypes.data, len(img.flat),
               byref( sm ),byref( sm2 ),byref( mx ),byref( mn ))
    return sm.value,sm2.value,mx.value,mn.value
    


LINEAR = 0
LOG = 1
SQRT = 2

# initialise a default mapping for a Frelon camera at ID11
setLUT( 90, 60000, LOG )

def compress( a ):
    return a.shape,zlib.compress( a.tostring(), 1 )

def decompress( o ):
    return np.fromstring( zlib.decompress( o[1] ), np.uint8 ).reshape( o[0] )

__all__ = ["setLUT", "LINEAR", "LOG", "SQRT", "rebin2", "rebin3", "rebin4",
           "LUT", 'imgsum', "imgstats", 'compress', 'decompress' ]


