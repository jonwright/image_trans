


import numpy as np
# https://en.wikipedia.org/wiki/De_Bruijn_sequence
def de_bruijn(k, n):
    """
    de Bruijn sequence for alphabet k
    and subsequences of length n.
    """
    try:
        # let's see if k can be cast to an integer;
        # if so, make our alphabet a list
        _ = int(k)
        alphabet = list(map(str, range(k)))

    except (ValueError, TypeError):
        alphabet = k
        k = len(k)

    a = [0] * k * n
    sequence = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                sequence.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)
    db(1, 1)
    return "".join(alphabet[i] for i in sequence)

s = de_bruijn(2,4)
h = int(s,2)



print "Sequence:",s,hex(int(s,2))
print format(h,"016b")


for i in range(12):
    print s[i:i+4]
for i in range(12,16):
    print s[i:]+s[:i-12]

def l2_deb( x ):
    v = x
    v = v | (v>>1)
    v = v | (v>>2)
    v = v | (v>>4)
    v = v | (v>>8)
    v = v ^ (v>>1)
    r = ((h*v)&(0xFFFF)) >> 12
    #print v,format(v,"016b"),r,x,format(x,"016b"), table[r]
    return r

table = np.zeros(16,np.int)
for i in range(16):
    table [ l2_deb( (1<<i) ) ] = i
print "table",table
print [(1<<i)  for i in range(16) ]

l2n = np.concatenate( ([0,], np.floor( np.log2( np.arange( 1, (1<<16) ) ) ).astype( int )))
for i in range(0,10):
    r = l2_deb(i)
#    print i, r, table[r], l2n[i]
    assert table[l2_deb(i)] == l2n[i],i
print "OK"
    
