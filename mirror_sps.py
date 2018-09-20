


import sys, sps, time, numpy as np, imgtrans

# Connect to a spec shared array and "mirror" it as
# rebinned int8 via LUT


specversion , arrayname , binfactor , lut , minv, maxv = sys.argv
binfuncs = {
    "2": imgtrans.rebin2,
    "3": imgtrans.rebin3,
    "4": imgtrans.rebin4,
    }
bf = binfuncs[ binfactor ]

assert lut in ("LINEAR","LOG","SQRT")
if lut = "LINEAR":
    luti = imgtrans.LINEAR
if lut = "LOG":
    luti = imgtrans.LOG
if lut = "SQRT":
    luti = imgtrans.SQRT
minv = int(minv)
maxv = int(maxv)

imgtrans.setLUT( minv, maxv, luti )

inp = sps.sps_attach( specversion, arrayname )
out_np = np.zeros( ( inp.shape[0] / binfactor,
                     inp.shape[1] / binfactor ), np.uint8 )
bf( inp, out_np )
sps.sps_create( "mirror", "%s_%s_%d_%s"%(specversion, arrayname, binfactor, lut),
                out_np.shape[0], out_np.shape[1], np.uint8, sps.SPS_CHAR )

while 1:
    if sps.sps_isupdated( specversion, arrayname ):
        
        bf( inp, out_np )

