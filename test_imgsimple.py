
from __future__ import print_function, division
import numpy as np
import unittest
import time
import img_simple

alltimes = []

class test_pick(unittest.TestCase):

    def setUp( self ):
        self.r = np.arange( 0, 256, 1 ).reshape(16,16)
        self.dotime = False

    def testpick( self ):
        for dt in [ np.int8,  np.int16,  np.int32,  np.int64,
                    np.uint8, np.uint16, np.uint32, np.uint64,
                    np.float32, np.float ]:
            for i in range(1,16):
                t = self.r.astype( dt )
                times= [ time.time(),] ## with malloc
                cpick = img_simple.pick( t, i )
                times.append( time.time() )
                t = self.r.astype( dt )
                npick = t[::i, ::i ].copy()
                times.append( time.time() )
                if cpick.shape != npick.shape or \
                   abs(cpick - npick).ravel().sum()>0 :
                    print( cpick )
                    print( npick )
                    print( cpick.shape, cpick.dtype, npick.shape, npick.dtype )
                    print( i )
                    self.assertEqual( 1, 0)
                else:
                    self.assertTrue( (cpick == npick ).all())
                if self.dotime:
                    ctime = (times[1]-times[0])*1e3
                    ntime = (times[2]-times[1])*1e3
                    alltimes.append(  " pick: %10s %-10d %-3d %6.2f %6.2f speedup: %5.1f "%(
                        t.dtype.name, t.nbytes, i, ctime, ntime, ntime/ctime ))

    def testlog2byte( self ):
        ar = self.r.astype( np.uint16 )
        start = time.time()
        l = img_simple.log2byte(ar, minval=0)
        ctime = (time.time()-start)*1e3
        start = time.time()
        l2 = img_simple.log2bytesimd(ar, minval=0)
        stime = (time.time()-start)*1e3
        self.assertEqual( (l==l2).all(), True)
        ###
        def il2(x): # integer log of x
            xv = np.where(x<1,1,x)
            return np.floor(np.log2(xv)).astype(np.int)
        def pylogLUT(i, debug=0): # lut function
            t = i - 64
            n = il2(t)
            t  = t - (1 << n)
            t  = (n * 16) + (t >> (n-4))
            t  = np.where( i < 64 , i,
                           np.where( i < 128, i//2 + 32, t ))
            return t
        ###
        start = time.time()
        x = pylogLUT( ar )
        ntime = (time.time()-start)*1e3
        if self.dotime:
            alltimes.append("log2byte     %s %d  %6.2f %6.2f speedup %6.2f"%(
                ar.dtype, ar.nbytes, ctime, ntime, ntime/ctime))
            alltimes.append("log2bytesimd %s %d  %6.2f %6.2f speedup %6.2f"%(
                ar.dtype, ar.nbytes, stime, ntime, ntime/stime))
        if not (x==l).all():
            sys.exit()
        
        self.assertEqual( (x==l).all() , True )
        assert l.dtype == np.uint8

        

    def testrebin( self ):
        for dt in [ np.int8,  np.int16,  np.int32,  np.int64,
                    np.uint8, np.uint16, np.uint32, np.uint64,
                    np.float32, np.float ]:
            for n in range(1,17):
                t = self.r.astype( dt )
                times= [ time.time(),] ## with malloc
                ns = [ i//n for i in t.shape]
                na = t[ :n*ns[0], :n*ns[1] ].astype( np.int64 )
                na.shape = [ ns[0], n, ns[1], n ]
                nrebin = (na.sum(axis=3).sum(axis=1)/n/n).astype( t.dtype )
                times.append( time.time() )
                crebin = np.empty_like( nrebin )
                times.append( time.time() )
                crebin = img_simple.rebin( t, n, out=crebin )
                times.append( time.time() ) 
                if crebin.shape != nrebin.shape or \
                   abs(crebin - nrebin).ravel().sum()>0 :
                    print("Source, rebin by",n)
                    print(t)
                    print("C says")
                    print( crebin )
                    print("numpy says")
                    print( nrebin)
                    print( crebin.shape, crebin.dtype, nrebin.shape, nrebin.dtype )
                    print( n )
                    import pylab
                    pylab.subplot(131)
                    pylab.imshow( crebin )
                    pylab.subplot(132)
                    pylab.imshow( nrebin )
                    pylab.subplot(133)
                    pylab.imshow( crebin-nrebin )
                    pylab.colorbar()
                    pylab.show()
                    
                    self.assertEqual( 1, 0)
                    #               sys.exit()
                else:
                    if dt in (np.float32, np.float):
                        
                        self.assertTrue( (abs(crebin - nrebin )<0.2).all())
                    else:
                        self.assertTrue( (crebin == nrebin ).all())
                if self.dotime:
                    global alltimes
                    ntime = (times[1]-times[0])*1e3
                    mtime = (times[2]-times[1])*1e3
                    ctime = (times[3]-times[2])*1e3
                    alltimes.append( "rebin: %10s %-10d %-3d %6.2f %6.2f speedup: %5.1f, malloc %6.2f "%(
                        t.dtype.name, t.nbytes, n , ctime, ntime, ntime/ctime, mtime ))
                    
class test_pick2(test_pick):
    def setUp( self ):
        self.r = np.arange( 0, 256, 1 ).reshape( 8,32)
        self.dotime = False

BIG = 2048
#BIG = 128
class test_pick1(test_pick):
    def setUp( self ):
        self.r = np.arange( 0, BIG*BIG, 1 ).reshape( BIG, BIG )
        self.inimage = self.r.astype(np.uint16)
        self.binned2x2 = np.empty( (BIG//2, BIG//2), np.uint16 )
        self.image2x2 = np.empty( (BIG//2, BIG//2), np.uint8 )
        self.binned4x4 = np.empty( (BIG//4, BIG//4), np.uint16 )
        self.image4x4 = np.empty( (BIG//4, BIG//4), np.uint8 )
        self.dotime = True

    def testbench( self ):
        for i in range(10):
            inimage = self.inimage
            binned2x2  = self.binned2x2
            binned4x4  = self.binned4x4
            image2x2 = self.image2x2
            image4x4 = self.image4x4
            start = time.time()
            binned2x2 = img_simple.rebin( inimage, 2, out=binned2x2 )
            image2x2  = img_simple.log2bytesimd( binned2x2, minval=64, out=image2x2 )
            ctime = (time.time()-start)*1e3
            alltimes.append( "binLUT2: %10s %-10d %.3f "%(
                inimage.dtype.name, inimage.nbytes, ctime ))

            start = time.time()
            binned4x4 = img_simple.rebin( inimage, 4, out=binned4x4 )
            image4x4  = img_simple.log2bytesimd( binned4x4, minval=64, out=image4x4 )
            ctime = (time.time()-start)*1e3
            alltimes.append( "binLUT4: %10s %-10d %.3f "%(
                inimage.dtype.name, inimage.nbytes, ctime ))
                             


            
if __name__=="__main__":
    try:
        unittest.main()
    except:
        pass
    finally:
        if BIG>512:
            print("Dtype,  bytes,  binning,  ctime, numpytime,  ratio,  time to alloc output") 
            for line in alltimes:
                print( line )
