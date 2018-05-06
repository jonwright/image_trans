
from __future__ import print_function, division
import numpy as np, os, time
from imgtrans import *

def bench( f, a ):
    start = time.time()
    f(a)
    return (time.time()-start)*1e3

def bench_omp():
    ar = (np.random.random(2048*2048)*65535).astype( np.uint16 )
    i = int(os.environ['OMP_NUM_THREADS'])
    tsu = [bench( imgsum  , ar ) for j in range(10)]
    tst = [bench( imgstats, ar ) for j in range(10)]
    print("%4d threads"%(i),
          "imgsum   min %.2f (%.2f)  mean %.2f   max %.2f ms"%(
              np.min(tsu),np.min(tsu)*i, np.mean(tsu), np.max(tsu) ),
          "imgstats min %.2f (%.2f)  mean %.2f   max %.2f ms"%(
              np.min(tst),np.min(tst)*i, np.mean(tst), np.max(tst) ) )
    

if __name__=="__main__":
    bench_omp()
