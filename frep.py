
from __future__ import print_function, division
import imgtrans
import numpy as np
a=np.arange( (1<<16), dtype=np.uint16)
b=a.astype(np.float32)
e = np.right_shift(b.view(np.uint32),np.uint8(23))-127
f = np.right_shift(b.view(np.uint32),np.uint8(15))
g = np.reshape( np.frombuffer( f, dtype=np.uint8 ), (len(f), 4 ))
#l2h = e*16 + (g[:,0]/16)
#l2l = e*16 + (g[:,0])
e[0]=0
#for i in range(257):
#    print "%-4d %-4d %-4d %-4d"%(a[i],b[i],g[i,0],e[i]),e[i]*16

def pylogLUT(i, debug=0):
    if debug: print (i,end=" ")
    if i < 64:
        if debug:
            print("lt 64:i")
        return i
    if i < 128:
        if debug:
            print("lt 128:i",i//2 + 32)
        return i//2 + 32
    t = i - 64
    n = il2(t)
    t = t - (1 << n)
    if debug:
        print("log:")
        print("i-64",i-64,"n",n,"16n",16*n,"i-64-(1<<n)",t)
    if ( n >= 4 ):
        v = (n * 16) + (t >> (n-4))

    else:
        v = ( n * 16) + (t << (4-n))
    if debug:print("v",v)
    return v

def il2(x):
    if x == 0:
        return x
    return int(np.floor(np.log2(x)))

def l2(x):
    """ in range 0,255 """
    n = il2(x)
    if n >= 4:
        return (n<<4) + ((x - (1<<n))>>(n-4))
    else:
        return (n<<4) + ((x - (1<<n))<<(4-n))

import sys
if(len(sys.argv))>1:
   for i in sys.argv[1:]:
#       pylogLUT(int(i), debug=1)
       f = np.array([int(i)-64,], np.float32)
       print(i,"Float repr %08x"%(f.view(np.int32)))
   sys.exit()

from pylab import plot, show, xlim, semilogx, legend
a.shape
e.shape
plot( a, e*16 + (g[:,0]/16), "-" )
plot( a, e*16 + (g[:,0]/16), "-" )
plot( a[1:], [l2(v) for v in a[1:]],"-")

def flog(a,e,g):
    return np.where( a < 64, a,
                     np.where( a < 128, a/2 + 32,
                               e*16 + g[:,0]/16))

e = np.right_shift((b-64).view(np.uint32),np.uint8(23))-127
f = np.right_shift((b-64).view(np.uint32),np.uint8(15))
g = np.reshape( np.frombuffer( f, dtype=np.uint8 ), (len(f), 4 ))

c=flog(a,e,g)
plot( a, [pylogLUT(i) for i in a],"-")
plot( a, c,"-",label="logLUT from float")

for i in range(0,10000,31):
    print(i,pylogLUT(i),c[i])
              
xlim(1,(1<<16))
semilogx()
legend()
show()
