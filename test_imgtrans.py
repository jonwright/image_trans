
from __future__ import print_function, division

import sys, time, os
import numpy as np, math
from imgtrans import *
from PIL import Image

if sys.platform == 'win32':
    timer = time.clock
else:
    timer = time.time

bvalues = []
btitles = []

def testLUT():
    from pylab import plot, show, legend, savefig, figure
    figure()
    setLUT( 90, 30000, LINEAR )
    plot( [ord(LUT[i]) for i in range(pow(2,16))], "-", label="LINEAR")
    setLUT( 90, 30000, LOG )
    plot( [ord(LUT[i]) for i in range(pow(2,16))], "-", label="LOG")
    setLUT( 90, 30000,  SQRT )
    plot( [ord(LUT[i]) for i in range(pow(2,16))], "-", label="SQRT")
    plot( [_logLUT(i,0) for i in range(pow(2,16))], "-", label="logLUT")
    legend(loc='lower right')
    show()
    savefig("lut.png")
    print("Wrote lut.png")

def il2(x):
    return int(np.floor(np.log2(x)))

def l2(x):
    """ in range 0,255 """
    n = il2(x)
    if n >= 4:
        return (n<<4) + ((x - (1<<n))>>(n-4))
    else:
        return (n<<4) + ((x - (1<<n))<<(4-n))

    

def test_log2s():
    def log2(x):
        return math.log(x) / math.log(2)
    for i in range(1,pow(2,16)):
        i1 = _log2s( i )
        i2 = math.floor( log2( i ) )
        i3 = l2( i )
        assert i1 == i2, (i,i1,i2, log2(i))
    print("uint8loguint16 OK")

def pylogLUT(i):
    check = _logLUT(i,0)
    if i < 64:
        return i
    if i < 128:
        return i//2 + 32
    t = i - 64
    n = il2(t)
    t = t - (1 << n)
    if ( n >= 4 ):
        v = (n * 16) + (t >> (n-4))
        return v
    else:
        v = ( n * 16) + (t << (4-n)) 
    return v

def testlogLUT():
    for i in range((1<<16)):
        check = _logLUT(i,0)
        py = pylogLUT(i)
    print("_logLUT in c matches to logLUT in python")
    

    
    
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
    sm = img.astype(np.int64).sum()
    sm2 = (img.astype(np.int64)*img).sum()
    mn = img.min()
    mx = img.max()
    return sm,sm2,mx,mn

def _bench( f, *args ):
    start = timer()
    ret = f( *args )
    end = timer()
    return (end-start)*1e3,ret

def bench( msg, f, *args ):
    global btitles, bvalues
    ts = []
    for j in range(10):
        t,r = _bench(f, *args)
        ts.append(t)
    btitles.append("%15s"%msg)
    #   "01234567890123
    if hasattr(r, '__len__'):
        
        if len(r)==2:
            cmprs = r[-1]
        else:
            cmprs = r
        bvalues.append("%6.2f-%6.2fms out:%d in:%d %.2f %%"%(
            np.min(ts),np.max(ts),len(cmprs),args[0].nbytes,
            100*len(cmprs)/args[0].nbytes))
    else:
        bvalues.append("%6.2f-%6.2fms "%(np.min(ts),np.max(ts)))
    return r

def testim1():
    np.random.seed(42)
    a = np.random.random_integers(0,pow(2,16),size=2048*2048).astype( np.uint16 )
    a.shape = 2048,2048
    return a

def testim2():
    c = 2048*2048/65535
    a = (np.arange(0,2048*2048,dtype=np.int64) / c).astype(np.uint16)
    a.shape = 2048,2048
    return a

def test_rebins( im ):
    global numpy_LUT
    # compare speeds:
    numpy_LUT = np.array( [ord(LUT[i]) for i in range(pow(2,16))], np.uint8 )
    
    r2 = np.zeros( (im.shape[0]//2,im.shape[1]//2), np.uint8)
    r3 = np.zeros( (im.shape[0]//3,im.shape[1]//3), np.uint8)
    r4 = np.zeros( (im.shape[0]//4,im.shape[1]//4), np.uint8)
    n2 = np.zeros( (im.shape[0]//2,im.shape[1]//2), np.uint8)
    n3 = np.zeros( (im.shape[0]//3,im.shape[1]//3), np.uint8)
    n4 = np.zeros( (im.shape[0]//4,im.shape[1]//4), np.uint8)
    
    s0=bench( 'C sum', imgsum, im )
    s1=bench( 'Numpy sum', im.astype(np.int64).sum )
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
    
    bench( '  toGif4', to_gif_string, r4 )
    bench( '  tojpeg4', to_jpeg_string, r4 )
    bench( '  topng4', to_png_string, r4 )
    
    assert (r2 == n2).all()
    assert (r3 == n3).all()
    assert (r4 == n4).all()
    
    assert (decompress( o2 ) == r2 ).all()
    assert (decompress( o3 ) == r3 ).all()
    assert (decompress( o4 ) == r4 ).all()
    
    total = im.nbytes
    if 1:
        from pylab import imshow, show, subplot, title, colorbar, savefig
        import pylab
        pylab.figure()
        pylab.spectral()
        subplot(221)
        imshow( im, aspect='equal' )
#        title( )
        subplot(222)
        imshow( r2, aspect='equal')
        subplot(223)
        imshow( r3, aspect='equal' )
        subplot(224)
        imshow( r4, aspect='equal'  )
        savefig("pics.png")
        print("write pics.png")
        show()

if __name__=="__main__":
    setLUT( 90, 60000, LOG )
    testlogLUT()
    if len( sys.argv) > 1:
        import fabio
        im = fabio.open( sys.argv[1] ).data.astype( np.uint16 )
        test_rebins (im )
    else:
        test_log2s()    

        # for a compare of speed
        numpy_LUT = np.array( [ord(LUT[i]) for i in range(pow(2,16))],
                              np.uint8 )
        test_rebins( testim1() )
        test_rebins( testim2() )
        testLUT()
        
    for t,v in zip(btitles, bvalues):
        print(t,v)



