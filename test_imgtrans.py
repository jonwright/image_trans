

import sys, fabio, time
import numpy as np
from imgtrans import *

def numpy_rebin( img, out, N ):
    # reshape to rebin
    global numpy_LUT
    d0 = (img.shape[0]//N)*N
    d1 = (img.shape[1]//N)*N
    tmp = img[:d0,:d1].astype( np.int32 )
    tmp.shape = d0//N, N, d1//N, N
    binned = tmp.sum(axis=3).sum(axis=1) // (N*N)
    out.flat[:] = numpy_LUT[ binned.ravel() ]

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

# compare speeds:
numpy_LUT = np.array( [ord(LUT[i]) for i in range(pow(2,16))], np.uint8 )

def bench( msg, f, *args ):
    start = time.time()
    ret = f( *args )
    end = time.time()
    print( msg + " %.2f ms"%((end-start)*1e3) )
    return ret
    
def showrebins(fname):

    from pylab import imshow, show, subplot, title, colorbar
    import pylab
    global numpy_LUT
    # compare speeds:
    numpy_LUT = np.array( [ord(LUT[i]) for i in range(pow(2,16))], np.uint8 )

    im = fabio.open( fname )
    r2 = np.zeros( (im.data.shape[0]//2,im.data.shape[1]//2), np.uint8)
    r3 = np.zeros( (im.data.shape[0]//3,im.data.shape[1]//3), np.uint8)
    r4 = np.zeros( (im.data.shape[0]//4,im.data.shape[1]//4), np.uint8)
    n2 = np.zeros( (im.data.shape[0]//2,im.data.shape[1]//2), np.uint8)
    n3 = np.zeros( (im.data.shape[0]//3,im.data.shape[1]//3), np.uint8)
    n4 = np.zeros( (im.data.shape[0]//4,im.data.shape[1]//4), np.uint8)

    print( fname )
    bench( '  C rebin2', rebin2, im.data, r2 )
    bench( '  Numpy b2', numpy_rebin, im.data, n2, 2 ) 
    o2 = bench( '  Compress2', compress,  r2 )
    bench( '  C rebin3', rebin3, im.data, r3 )
    bench( '  Numpy b3', numpy_rebin, im.data, n3, 3 ) 
    o3 = bench( '  Compress3', compress,  r3 )
    bench( '  C rebin4', rebin4, im.data, r4 )
    bench( '  Numpy b4', numpy_rebin, im.data, n4, 4 ) 
    o4 = bench( '  Compress4', compress,  r4 )

    assert (r2 == n2).all()
    assert (r3 == n3).all()
    assert (r4 == n4).all()
    
    
    assert (decompress( o2 ) == r2 ).all()
    assert (decompress( o3 ) == r3 ).all()
    assert (decompress( o4 ) == r4 ).all()

    
    total = im.data.nbytes

    pylab.spectral()

    subplot(221)
    imshow( im.data, aspect='equal' )
    title( fname )
    subplot(222)
    imshow( r2, aspect='equal')
    subplot(223)
    imshow( r3, aspect='equal' )
    subplot(224)
    imshow( r4, aspect='equal'  )
    show()


        
if __name__=="__main__":


    if len(sys.argv)>1:
        files = sys.argv[1:]
        setLUT( 90, 60000, LOG )
        # for a compare of speed
        numpy_LUT = np.array( [ord(LUT[i]) for i in range(pow(2,16))],
                              np.uint8 )
        for fname in files:
            showrebins( fname )
    else:
        testLUT()

    

