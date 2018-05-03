
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

__all__ = [setLUT, LINEAR, LOG, SQRT, rebin2, rebin3, rebin4 ]

def testLUT():
    from pylab import plot, show, legend
    setLUT( 90, 60000, LINEAR )
    plot( [ord(LUT[i]) for i in range(pow(2,16))], "-", label="LINEAR")
    setLUT( 90, 60000, LOG )
    plot( [ord(LUT[i]) for i in range(pow(2,16))], "-", label="LOG")
    setLUT( 90, 60000,  SQRT )
    plot( [ord(LUT[i]) for i in range(pow(2,16))], "-", label="SQRT")
    legend(loc='lower right')
    show()

def compress( a ):
    return a.shape,zlib.compress( a.tostring(), 1 )

def decompress( o ):
    return np.fromstring( zlib.decompress( o[1] ), np.uint8 ).reshape( o[0] )

def showrebins(fname):
    import time
    im = fabio.open( fname )
    r2 = np.zeros( (im.data.shape[0]//2,im.data.shape[1]//2), np.uint8)
    r3 = np.zeros( (im.data.shape[0]//3,im.data.shape[1]//3), np.uint8)
    r4 = np.zeros( (im.data.shape[0]//4,im.data.shape[1]//4), np.uint8)
    start = time.time()
    rebin2( im.data, r2 )
    t2 = time.time()-start

    start = time.time()
    o2 = compress( r2 )
    z2 = time.time()-start

    start = time.time()
    rebin3( im.data, r3 )
    t3 = time.time()-start

    start = time.time()
    o3 = compress( r3 )
    z3 = time.time()-start
    
    start = time.time()
    rebin4( im.data, r4 )
    t4 = time.time()-start

    start = time.time()
    o4 = compress( r4 )
    z4 = time.time()-start

    assert (decompress( o2 ) == r2 ).all()
    assert (decompress( o3 ) == r3 ).all()
    assert (decompress( o4 ) == r4 ).all()

    print( fname  )
    total = im.data.nbytes
    print( "2x : %.3f ms zlib: %.2f ms size %d kB gain %.1f vs. 8 "%(
        1e3*t2, 1e3*z2, len(o2[1])//1024, total/len(o2[1])))
    print( "3x : %.3f ms zlib: %.2f ms size %d kB gain %.1f vs. 18"%(
        1e3*t3, 1e3*z3, len(o3[1])//1024, total/len(o3[1])))
    print( "4x : %.3f ms zlib: %.2f ms size %d kB gain %.1f vs. 32"%(
        1e3*t4, 1e3*z4, len(o4[1])//1024, total/len(o4[1])))

    from pylab import imshow, show, subplot, title
    import pylab
    pylab.spectral()

    subplot(221)
    imshow( im.data, aspect='equal' )
    title( fname )
    subplot(222)
    title( 'rebin2 %.2f ms'%(t2*1e3) )
    imshow( r2, aspect='equal')
    subplot(223)
    title( 'rebin3 %.2f ms'%(t3*1e3) )
    imshow( r3, aspect='equal' )
    subplot(224)
    title( 'rebin4 %.2f ms'%(t4*1e3) )
    imshow( r4, aspect='equal'  )
    show()
    
if __name__=="__main__":

    import sys, fabio
    if len(sys.argv)>1:
        files = sys.argv[1:]
        setLUT( 90, 60000, LOG )
        for fname in files:
            showrebins( fname )
    else:
        testLUT()

    
# gcc -shared -o _imgtrans.so -fPIC -O2 imgtrans.c 
