
#include "il2lut.h"

/* Compute the integer log2 * 16 
 *    Using log(x) = log( 2^n + (x-2^n) )
 *                 = n + log( 1 + y )
 *    log( 1 + y ) ~= y 
 *
 * Because log2(65536) = 16 and 16*16=255
 *
 * imin = value to subtract. Can overflow.
 *
 * imin -> 64  : steps of 1
 * 64   -> 128 : steps of 2
 * then 16.log2(x) 
 */

uint8_t logLUT( uint16_t , uint16_t );




inline
uint8_t logLUT( uint16_t x, uint16_t imin ){
  uint16_t t,s;
  uint8_t n;
  x -= imin;
  if (x & 0xFF80) {  //  x>128
    x -= 64;
    t = x;
    /* Computes log2(x) which is the position of the first binary 1
     * see various internet articles (fls in linux kernel for int32)
     * https://graphics.stanford.edu/~seander/bithacks.html#IntegerLog
     */
    if(0){ // OK to branch
      n = 0;
      if( t & 0xFF00 ){      // 1111 1111  0000 0000
	t >>= 8u ; n |= 8u;
      }
      if( t & 0x00F0 ){      // 0000 0000  1111 0000
	t >>= 4u ; n |= 4u;
      }
      if( t & 0x000C ){      // 0000 0000  0000 1100
	t >>= 2u ; n |= 2u;
      }
      if( t & 0x0002 ){      // 0000 0000  0000 0001
	t >>= 1u ; n |= 1u;
      }
    } else {
      n = (t > 0xFFFF) << 4; t >>= n;
      s = (t > 0xFF  ) << 3; t >>= s; n |= s;
      s = (t > 0xF   ) << 2; t >>= s; n |= s;
      s = (t > 0x3   ) << 1; t >>= s; n |= s;
      n |= (t >> 1);
    }
    /* Remainder x-2^n */
    t = x - (1u << n);
    /* if x >= 4 */
    if ( n | 4u ) {
      return (uint8_t) ( ( n << 4 ) + ( t  >> (n - 4) ) );
    } else {
      return (uint8_t) ( ( n << 4 ) + ( t  << (4 - n) ) );
    }
  }
  if (x & 0xFFC0) { //  x > 64, so div2 and add 32
    return  (x >> 1) + 32;
  }
  return x;
}


void LUT( const uint16_t * restrict in,
	  uint8_t * restrict out,
	  uint16_t imin,
	  int len ){
  int i;
  for( i=0 ; i < len ; i=i+4 ) {
    out[i     ] = logLUT( in[i     ], imin );
    out[i + 1 ] = logLUT( in[i + 1 ], imin );
    out[i + 2 ] = logLUT( in[i + 2 ], imin );
    out[i + 3 ] = logLUT( in[i + 3 ], imin );
  }
}
