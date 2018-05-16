
from __future__ import print_function, division
import numpy as np, os, time, sys
from imgtrans import *

if sys.platform == 'win32':
    timer = time.clock
else:
    timer = time.time


def bench( f, a ):
    start = timer()
    f(a)
    return (timer()-start)*1e3

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
