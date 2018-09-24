
#include "il2lut.h"
#include <assert.h>

#include <stdio.h>
#include <stdlib.h>
#include <omp.h>


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





 
#define dbg(v)                                                 
/*
#define dbg(v)                                                 \
if(debug) {						       \
      printf("%-4s ",#v);                                      \
      for(int k=0;k<16;k++) printf(" %02x",(v).m128i_u8[k]);   \
      printf("\n     ");                                       \
      for(int k=0;k<16;k++) printf(" %-4d",(v).m128i_u8[k]);   \
      printf("\n     ");                                       \
      for(int k=0;k<8;k++) printf(" %-8d ",(v).m128i_u16[k]);  \
      printf("\n"); }
*/




static inline
uint8_t logLUT_branch( uint16_t x, uint16_t imin ){
  uint16_t t;
  uint8_t n;
  x -= imin;
  if (x & 0xFF80) {  //  x>128
    x -= 64;
    t = x;
    /* Computes log2(x) which is the position of the first binary 1
     * see various internet articles (fls in linux kernel for int32)
     * https://graphics.stanford.edu/~seander/bithacks.html#IntegerLog
     */
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


static inline
uint8_t logLUT_nobranch( uint16_t x, uint16_t imin ){
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
    n = (t > 0xFF  ) << 3; // n =   8       or 0
    t >>= n;               
    s = (t > 0xF   ) << 2; // s = t/4
    t >>= s;
    n |= s;
    s = (t > 0x3   ) << 1;
    t >>= s;
    n |= s;
    n |= (t >> 1);
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


void LUT_linear ( const uint16_t * restrict in,
		  uint8_t * restrict out,
		  uint16_t imin,
		  uint8_t shft,
		  int len ){
  int i;
  assert( is_aligned( in, 16 ));
  assert( is_aligned( out, 16 ));
  for( i=0; i<len ; i++)
     out[i] = (in[i] > imin) ? ((in[i]-imin) >> shft) : 0;
}

void LUT_linear_simd ( const uint16_t * restrict in,
			 uint8_t * restrict out,
			 uint16_t imin,
			 uint8_t shft,
			 int len ){
  int i;
  __m128i i0;
  assert( is_aligned(  in, 16));
  assert( is_aligned( out, 16));

  const __m128i vmin  = _mm_set1_epi16( imin ); 
  const __m128i mask0 = _mm_set_epi8(128, 128, 128, 128, 128, 128, 128, 128,
				       14, 12, 10, 8, 6, 4, 2, 0);
#pragma omp parallel for private(i0)
  for( i=0; i<len ; i=i+8){
    // Load 8 values
    i0 = _mm_stream_load_si128( (__m128i *) &(in[i]) );
    i0 = _mm_subs_epu16(  i0, vmin ); // saturating subtract
    i0 = _mm_srli_epi16(  i0, shft ); // shift right adding zeros
    i0 = _mm_shuffle_epi8(i0, mask0); // 0,1,2,3,4,5,6,7,x,x,x,x,x,x,x,x
    _mm_storel_epi64( (__m128i*) &(out[i]), i0 );
  }

}

void LUT_branch ( const uint16_t * restrict in,
		  uint8_t * restrict out,
		  uint16_t imin,
		  int len ){
  int i;
  for( i=0 ; i < len ; i=i+4 ) {
    out[i     ] = logLUT_branch( in[i     ], imin );
    out[i + 1 ] = logLUT_branch( in[i + 1 ], imin );
    out[i + 2 ] = logLUT_branch( in[i + 2 ], imin );
    out[i + 3 ] = logLUT_branch( in[i + 3 ], imin );
  }
}


void LUT_nobranch ( const uint16_t * restrict in,
		    uint8_t * restrict out,
		    uint16_t imin,
		    int len ){
  int i;
  for( i=0 ; i < len ; i=i+4 ) {
    out[i     ] = logLUT_nobranch( in[i     ], imin );
    out[i + 1 ] = logLUT_nobranch( in[i + 1 ], imin );
    out[i + 2 ] = logLUT_nobranch( in[i + 2 ], imin );
    out[i + 3 ] = logLUT_nobranch( in[i + 3 ], imin );
  }
}


void LUT_logfloat ( const uint16_t * restrict in,
		    uint8_t * restrict out,
		    uint16_t imin,
		    int len ){
  int i;
  uint16_t x;
  uint8_t t, n;
  w4 f;
  for( i=0 ; i < len ; i=i+1 ) {
    x = in[i] - imin;
    if ( x < 64u ) {
      out[i] = x;
    } else if ( x < 128) {
      out[i] = (x >> 1) + 32u;
    } else {
      x -= 64;
      f.single = (float) x;
      // Exponent
      n =  (( ( f.i32 >> 23  ) & 0xFF ) - 127) << 4;
      // Mantissa, range 0->255
      t =  ((uint8_t)(f.i32 >> 15 ) )>> 4 ;
      out[i] = n + t ;
    }
  }
}


void LUT_logfl_simd ( const uint16_t * restrict in,
		      uint8_t * restrict out,
		      uint16_t imin,
		      int len, int debug ){
  int i;

  __m128i msk;
  __oword i0, o1, o2, n1, t1;

  assert( is_aligned(  in, 16));
  assert( is_aligned( out, 16));

  const __m128i vmin  = _mm_set1_epi16( imin );
  const __m128i v32   = _mm_set1_epi16( 32 );
  const __m128i v63  = _mm_set1_epi16( 63 );
  const __m128i v64  = _mm_set1_epi16( 64 );
  const __m128i v127  = _mm_set1_epi16( 127 );
  const __m128i v255  = _mm_set1_epi16( 0xFF );
  const __m128i v0   = _mm_set1_epi16( 0 );

  const __m128i mask0 = _mm_set_epi8(128, 128, 128, 128, 128, 128, 128, 128,
  				       14, 12, 10, 8, 6, 4, 2, 0);

#pragma omp parallel for private(i0,o1,o2,n1,t1,msk)
  for( i=0 ; i < len ; i=i+8 ) {

    // Load from memory
    i0.m128i = _mm_stream_load_si128( (__m128i *) &(in[i]) );

    // Take off the minimum (saturating)
    i0.m128i = _mm_subs_epu16(  i0.m128i, vmin ); // saturating subtract

    //  n =  (x >> 1) + 32;
    o2.m128i = _mm_srli_epi16(  i0.m128i, 1 );    // shift right adding zeros
    o2.m128i = _mm_adds_epu16(  o2.m128i, v32 );  // saturating add 32

    // x>=64 where x is unsigned
    // mask is 1 for gt64, 0 for less. 
    msk = _mm_cmpeq_epi16(
	       _mm_srli_epi16(                   // shift right adding zeros
                   _mm_andnot_si128( v63,  i0.m128i ),  1), v0 );

    o2.m128i = _mm_blendv_epi8( o2.m128i, i0.m128i, msk );


    // Take off 64 for log part
    i0.m128i = _mm_subs_epu16(  i0.m128i, v64 ); // saturating subtract


    // mask is 1 for gt64, 0 for less.
    msk = _mm_cmpeq_epi16(
                _mm_srli_epi16(                   // shift right adding zeros
                   _mm_andnot_si128( v63,  i0.m128i ),  1), v0 );

    
    // take first 4 numbers as floats
    // https://stackoverflow.com/questions/9161807/sse-convert-short-integer-to-float/9169454
    o1.m128  = _mm_cvtepi32_ps( _mm_unpacklo_epi16( i0.m128i, v0));
    
    // e = np.right_shift((b-64).view(np.uint32),np.uint8(23))-127
    // f = np.right_shift((b-64).view(np.uint32),np.uint8(15))
    // g = np.reshape( np.frombuffer( f, dtype=np.uint8 ), (len(f), 4 ))
    //
    // def flog(a,e,g):
    // return np.where( a < 64, a,
    //                 np.where( a < 128, a/2 + 32,
    //                           e*16 + g[:,0]/16))

    // integer part of exponent
    n1.m128i = _mm_slli_epi32( 
		 _mm_subs_epu8(
		  _mm_srli_epi32( o1.m128i, 23 ),
		  v127)  , 4 );
    // remainder part
    t1.m128i = _mm_srli_epi32(
		 _mm_and_si128(
		   _mm_srli_epi32( o1.m128i, 15 ), v255 ), 4);

    n1.m128i = _mm_add_epi32( n1.m128i, t1.m128i );

    // Now the second 4
    o1.m128  = _mm_cvtepi32_ps( _mm_unpackhi_epi16( i0.m128i, v0));

    i0.m128i = _mm_slli_epi32( 
		 _mm_subs_epu8(
		   _mm_srli_epi32( o1.m128i, 23 ),
		   v127 )  , 4 );
    t1.m128i = _mm_srli_epi32(
		 _mm_and_si128(
		   _mm_srli_epi32( o1.m128i, 15 ), v255 ), 4);
    t1.m128i = _mm_add_epi32( i0.m128i, t1.m128i );
    
    // Combine the first and second 4 floats
    n1.m128i = _mm_packs_epi32 (n1.m128i, t1.m128i);

    // ... pick the ones above 128
    o2.m128i = _mm_blendv_epi8( n1.m128i, o2.m128i, msk );    

    // And put into output order
    o2.m128i = _mm_shuffle_epi8(o2.m128i, mask0);

    _mm_stream_pi( (__m64*) &(out[i]), _mm_movepi64_pi64(o2.m128i));
    
  }
}

/*
 *Sequence: 0000100110101111 0x9af
 *table [ 0  1  2  5  3  9  6 11 15  4  8 10 14  7 13 12]
 *def l2_deb( x ):
    v = x
    v = v | (v>>1)
    v = v | (v>>2)
    v = v | (v>>4)
    v = v | (v>>8)
    v = v ^ (v>>1)
    r = ((h*v)&(0xFFFF)) >> 12
    return r
*/


void LUT_logDEB   ( const uint16_t * restrict in,
		    uint8_t * restrict out,
		    uint16_t imin,
		    int len ){
  int i;
  uint16_t x,t,h;
  h =  0x9af;
  uint8_t n, L[16] = { 0 , 1 , 2 , 5 , 3 , 9 , 6 ,11,
		       15,  4 , 8, 10, 14,  7 ,13, 12 };
  for( i=0 ; i < len ; i=i+1 ) {
    x = in[i] - imin;
    if ( x < 64u ) {
      out[i] = x;
    } else if ( x < 128) {
      out[i] = (x >> 1) + 32u;
    } else {
      x -= 64;
      t = x;
      t = t | (t>>1);
      t = t | (t>>2);
      t = t | (t>>4);
      t = t | (t>>8);
      t = t ^ (t>>1);
      n = L[ ((h*t)&0xFFFF) >> 12 ];
      //      assert (n<16);
      t = x - (1u << n);
      /* if x >= 4 */
      if ( n | 4u ) {
	out[i] = ( ( n << 4 ) + ( t  >> (n - 4) ) );
      } else {
	out[i] = ( ( n << 4 ) + ( t  << (4 - n) ) );
      }
    }
  }
}



void LUT_log_simd ( const uint16_t * restrict in,
			   uint8_t * restrict out,
			   uint16_t imin,
			   int len ){
  int i,j;
  uint16_t t,s,x;
  uint8_t n;
  __oword i0, o2, o3,nv,tv,sv;
  __m128i msk64,m;
  assert( is_aligned(  in, 16));
  assert( is_aligned( out, 16));

  // imin as a vector
  const __m128i vmin  = _mm_set1_epi16( imin );
  const __m128i v0    = _mm_set1_epi16( 0 );
  const __m128i v8   = _mm_set1_epi16( 8 );
  const __m128i v63  = _mm_set1_epi16( 63 );
  const __m128i v64  = _mm_set1_epi16( 64 );
  const __m128i vFF00  = _mm_set1_epi16( 0xFF00 );

  const __m128i mask0 = _mm_set_epi8(128, 128, 128, 128, 128, 128, 128, 128,
				       14, 12, 10, 8, 6, 4, 2, 0);

 			  
  for( i=0 ; i < len ; i=i+8 ) {
    i0.m128i = _mm_stream_load_si128( (__m128i *) &(in[i]) );
    // saturating subtract - remove imin 
    i0.m128i = _mm_subs_epu16(  i0.m128i, vmin ); 

    //  n =  (x >> 1) + 32;
    o2.m128i = _mm_adds_epu16(  i0.m128i, v64 ); // saturating add 32
    o2.m128i = _mm_srli_epi16(  o2.m128i, 1 ); // shift right adding zeros


    // x>=64 where x is unsigned
    // mask is 1 for gt64, 0 for less.
    msk64 = _mm_cmpeq_epi16(
                _mm_srli_epi16(               // shift right adding zeros
                   _mm_andnot_si128( v63,  i0.m128i ),  1), v0 );
    o2.m128i = _mm_blendv_epi8( o2.m128i, i0.m128i, msk64 );
    o2.m128i = _mm_shuffle_epi8(o2.m128i, mask0); // 0,1,2,3,4,5,6,7,x,x,x,x,x,x,x,x
//    o3.m128i = _mm_shuffle_epi8(i0.m128i, mask0); // 0,1,2,3,4,5,6,7,x,x,x,x,x,x,x,x
/*
>>> format(0xFFC0,"016b")
'1111111111000000'
>>> format(64,"016b")
'0000000001000000'
>>> format(0xFF80,"016b")
'1111111110000000'
>>> format(127,"016b")
'0000000001111111'
>>> 

*/
    // subtract 64
    o3.m128i = _mm_subs_epu16( i0.m128i, v64);
    // n = (t > 0xFF  ) << 3; // n =   8       or 0
    m = _mm_cmpeq_epi16( _mm_srli_epi16( _mm_and_si128( o3.m128i, vFF00), 1), v0);
    // m is shift by 8 or shift by 0
    nv.m128i = _mm_blendv_epi8( v8, v0, m );
    // t = (x >> n);
    tv.m128i = _mm_blendv_epi8( _mm_srli_epi16( o3.m128i, 8 ), o3.m128i, m );
    //  s = (t > 0xF   ) << 2; // s = t/4
    m = _mm_cmpeq_epi16(
	  _mm_srli_epi16(
	     _mm_and_si128( tv.m128i, _mm_set1_epi16( 0xFFF0 )),1),v0);
    sv.m128i = _mm_blendv_epi8( _mm_set1_epi16(4), v0, m );
    // t >>= s;
    tv.m128i = _mm_blendv_epi8( _mm_srli_epi16( tv.m128i, 4 ), tv.m128i, m );
    nv.m128i = _mm_or_si128( nv.m128i, sv.m128i);
    // s = (t > 0x3   ) << 1;
    
    for( j=0; j < 8; j++){
      x = o3.m128i_u16[j];    
      if ((x+64) & 0xFF80) {  //  x>128

       
      /* Computes log2(x) which is the position of the first binary 1
       * see various internet articles (fls in linux kernel for int32)
       * https://graphics.stanford.edu/~seander/bithacks.html#IntegerLog
       */
      // n = (t > 0xFF  ) << 3; // n =   8       or 0
      // n = ( (t & 0xFF00)!=0  ) << 3; // n =   8       or 0
      n = nv.m128i_u16[j];
//      t = tv.m128i_u16[j]; //>>= n;
//      t = x;
//      t = (x >> n);
      t = tv.m128i_u16[j];
//      s = (t > 0xF   ) << 2; // s = t/4
      s = sv.m128i_u16[j];
     // t >>= s;
//      n |= s;
      s = (t > 0x3   ) << 1;
      t >>= s;
      n |= s;
      n |= (t >> 1);
      /* Remainder x-2^n */
      t = x - (1u << n);
      /* if x >= 4 */
      if ( n | 4u ) {
	n = ( ( n << 4 ) + ( t  >> (n - 4) ) );
	} else {
	n = ( ( n << 4 ) + ( t  << (4 - n) ) );
      }
//    } else if (x & 0xFFC0) { //  x > 64, so div2 and add 32
//	n =  (x >> 1) + 32;
//        n = o3.m128i_u8[j];
    } else {
      n = o2.m128i_u8[j];
    }
    out[i+j]=n;//v1.m128i_u8[j];
    }
  }
}
