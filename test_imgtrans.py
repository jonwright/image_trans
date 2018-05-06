

import sys, fabio, time, os
import numpy as np
from imgtrans import *
import matplotlib
matplotlib.use("Agg")
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
    
# compare speeds:
numpy_LUT = np.array( [ord(LUT[i]) for i in range(pow(2,16))], np.uint8 )

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


def bench( msg, f, *args ):
    ts = []
    for j in range(10):
        t,r = _bench(f, *args)
        ts.append(t)
    print( "%20s \t %.2f - %.2f ms"%(msg,np.min(ts),np.max(ts)) )
    return r
    
def showrebins(fname):

    from pylab import imshow, show, subplot, title, colorbar, savefig
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
    s0=bench( '  C sum', imgsum, im.data )
    s1=bench( '  Numpy sum', im.data.sum )
    s2=bench( '  C sum', imgsum, im.data )
    assert s0==s1==s2,(s0,s1,s2)
    stats=bench( '  C stats', imgstats, im.data )
    nstats=bench('  numpy stats' ,numpy_stats,im.data)
#    print(stats)
#    print(nstats)
    assert (stats == nstats),(stats,nstats)

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
    savefig("pics.png")
    print("write pics.png")

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

    

