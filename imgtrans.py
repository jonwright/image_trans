
from __future__ import print_function , division


from ctypes import c_int, c_void_p, c_char, cdll
import numpy as np, zlib

_imgtrans = cdll.LoadLibrary("./_imgtrans.so")

setLUT = _imgtrans.setLUT
setLUT.argtypes = [ c_int, c_int, c_int ]

_rebin2 = _imgtrans.rebin2
_rebin2.argtypes = [ c_void_p, c_int, c_int, c_void_p ]

_rebin3 = _imgtrans.rebin3
_rebin3.argtypes = [ c_void_p, c_int, c_int, c_void_p ]

_rebin4 = _imgtrans.rebin4
_rebin4.argtypes = [ c_void_p, c_int, c_int, c_void_p ]


LUT = ( c_char*65536 ).in_dll( _imgtrans, "LUT" )

def rebin2(img, out):
    assert out.shape[0] == img.shape[0]//2
    assert out.shape[1] == img.shape[1]//2
    _rebin2(img.ctypes.data, img.shape[0], img.shape[1], out.ctypes.data)

def rebin3(img, out):
    assert out.shape[0] == img.shape[0]//3
    assert out.shape[1] == img.shape[1]//3
    _rebin3(img.ctypes.data, img.shape[0], img.shape[1], out.ctypes.data)

def rebin4(img, out):
    assert out.shape[0] == img.shape[0]//4
    assert out.shape[1] == img.shape[1]//4
    _rebin4(img.ctypes.data, img.shape[0], img.shape[1], out.ctypes.data)
    
LINEAR = 0
LOG = 1
SQRT = 2

# initialise a default mapping for a Frelon camera at ID11
setLUT( 90, 60000, LOG )

def compress( a ):
    return a.shape,zlib.compress( a.tostring(), 1 )

def decompress( o ):
    return np.fromstring( zlib.decompress( o[1] ), np.uint8 ).reshape( o[0] )

__all__ = ["setLUT", "LINEAR", "LOG", "SQRT", "rebin2", "rebin3", "rebin4", "LUT",
           'compress', 'decompress' ]


