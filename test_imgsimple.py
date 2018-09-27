
from __future__ import print_function, division
import numpy as np
import unittest

import img_simple

class test_pick(unittest.TestCase):

    def setUp( self ):
        self.r = np.arange( 0, 256, 1 ).reshape(16,16)

    def testpick( self ):
        for dt in [ np.int8,  np.int16,  np.int32,  np.int64,
                    np.uint8, np.uint16, np.uint32, np.uint64,
                    np.float32, np.float ]:
            for i in range(1,16):
                t = self.r.astype( dt )
                cpick = img_simple.pick( t, i )
                npick = t[::i, ::i ]
                if cpick.shape != npick.shape or \
                   abs(cpick - npick).ravel().sum()>0 :
                    print( cpick )
                    print( npick )
                    print( cpick.shape, cpick.dtype, npick.shape, npick.dtype )
                    print( i )
                    self.assertEqual( 1, 0)
                else:
                    self.assertTrue( (cpick == npick ).all())


    def testrebin( self ):
        for dt in [ np.int8,  np.int16,  np.int32,  np.int64,
                    np.uint8, np.uint16, np.uint32, np.uint64,
                    np.float32, np.float ]:
            pass
        for n in range(1,16):
            t = self.r.astype( dt )
            crebin = img_simple.rebin( t, n )
            ns = [ i//n for i in t.shape]
            na = t[ :n*ns[0], :n*ns[1] ].astype( np.int64 )
            na.shape = [ ns[0], n, ns[1], n ]
            nrebin = (na.sum(axis=3).sum(axis=1)/n/n).astype( t.dtype )
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
                self.assertEqual( 1, 0)
#               sys.exit()
            else:
                self.assertTrue( (crebin == nrebin ).all())

class test_pick(test_pick):
    def setUp( self ):
        self.r = np.arange( 0, 256, 1 ).reshape( 8,32)

                    
if __name__=="__main__":
    unittest.main()
