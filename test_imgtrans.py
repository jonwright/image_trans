
from __future__ import print_function, division

import sys, time, os
import numpy as np
from imgtrans import *

def testLUT():
    from pylab import plot, show, legend, savefig
    setLUT( 90, 60000, LINEAR )
    plot( [ord(LUT[i]) for i in range(pow(2,16))], "-", label="LINEAR")
    setLUT( 90, 60000, LOG )
    plot( [ord(LUT[i]) for i in range(pow(2,16))], "-", label="LOG")
    setLUT( 90, 60000,  SQRT )
    plot( [ord(LUT[i]) for i in range(pow(2,16))], "-", label="SQRT")
    legend(loc='lower right')
    savefig("lut.png")
    print("Wrote lut.png")
    


def numpy_rebin( img, out, N ):
    # reshape to rebin
    global numpy_LUT
    d0 = (img.shape[0]//N)*N
    d1 = (img.shape[1]//N)*N
    tmp = img[:d0,:d1].astype( np.int32 )
    tmp.shape = d0//N, N, d1//N, N
    binned = tmp.sum(axis=3).sum(axis=1) // (N*N)
    out.flat[:] = numpy_LUT[ binned.ravel() ]

def numpy_stats(img):
    sm = img.sum()
    sm2 = (img.astype(int)*img).sum()
    mn = img.min()
    mx = img.max()
    return sm,sm2,mx,mn

def _bench( f, *args ):
    start = time.time()
    ret = f( *args )
    end = time.time()
    return (end-start)*1e3,ret


btitles = []
bvalues = []
def bench( msg, f, *args ):
    global btitles, bvalues
    ts = []
    for j in range(10):
        t,r = _bench(f, *args)
        ts.append(t)
    btitles.append("%15s"%msg)
    #   "01234567890123
    bvalues.append("%6.2f-%6.2fms "%(np.min(ts),np.max(ts)))
    return r


def testim1():
    np.random.seed(42)
    a = np.random.random_integers(0,pow(2,16),size=2048*2048).astype( np.uint16 )
    a.shape = 2048,2048
    return a

def test_rebins( ):
    global numpy_LUT
    # compare speeds:
    numpy_LUT = np.array( [ord(LUT[i]) for i in range(pow(2,16))], np.uint8 )
    im = testim1()
    r2 = np.zeros( (im.shape[0]//2,im.shape[1]//2), np.uint8)
    r3 = np.zeros( (im.shape[0]//3,im.shape[1]//3), np.uint8)
    r4 = np.zeros( (im.shape[0]//4,im.shape[1]//4), np.uint8)
    n2 = np.zeros( (im.shape[0]//2,im.shape[1]//2), np.uint8)
    n3 = np.zeros( (im.shape[0]//3,im.shape[1]//3), np.uint8)
    n4 = np.zeros( (im.shape[0]//4,im.shape[1]//4), np.uint8)

    s0=bench( 'C sum', imgsum, im )
    s1=bench( 'Numpy sum', im.sum )
    s2=bench( 'C sum', imgsum, im )
    assert s0==s1==s2,(s0,s1,s2)
    
    stats =bench( 'C stats', imgstats, im )
    nstats=bench('numpy stats' ,numpy_stats,im)
    assert (stats == nstats),(stats,nstats)

    bench( '  C rebin2', rebin2, im, r2 )
    bench( '  Numpy b2', numpy_rebin, im, n2, 2 ) 
    o2= bench( '  Compress2', compress,  r2 )
    bench( '  C rebin3', rebin3, im, r3 )
    bench( '  Numpy b3', numpy_rebin, im, n3, 3 ) 
    o3= bench( '  Compress3', compress,  r3 )
    bench( '  C rebin4', rebin4, im, r4 )
    bench( '  Numpy b4', numpy_rebin, im, n4, 4 ) 
    o4= bench( '  Compress4', compress,  r4 )

    assert (r2 == n2).all()
    assert (r3 == n3).all()
    assert (r4 == n4).all()
    
    assert (decompress( o2 ) == r2 ).all()
    assert (decompress( o3 ) == r3 ).all()
    assert (decompress( o4 ) == r4 ).all()

    # print report
    global bvalues, btitles
    for t,v in zip(btitles, bvalues):
        print(t,v)
    
    total = im.nbytes
    if 0:
        from pylab import imshow, show, subplot, title, colorbar, savefig
        import pylab
        pylab.spectral()
        subplot(221)
        imshow( im, aspect='equal' )
        title( fname )
        subplot(222)
        imshow( r2, aspect='equal')
        subplot(223)
        imshow( r3, aspect='equal' )
        subplot(224)
        imshow( r4, aspect='equal'  )
        savefig("pics.png")
        print("write pics.png")

if __name__=="__main__":

    
    setLUT( 90, 60000, LOG )
    # for a compare of speed
    numpy_LUT = np.array( [ord(LUT[i]) for i in range(pow(2,16))],
                          np.uint8 )
    test_rebins( )
    testLUT()
