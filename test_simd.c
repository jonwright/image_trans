
#include <time.h>
#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <smmintrin.h>

#define is_aligned(POINTER, BYTE_COUNT) \
    (((uintptr_t)(const void *)(POINTER)) % (BYTE_COUNT) == 0)

#if defined (_MSC_VER)
#define OWORD_ALIGNMENT __declspec(align(16))
#else
#define OWORD_ALIGNMENT __attribute__ ((aligned (16))) 
#endif

typedef union OWORD_ALIGNMENT __oword {
  __m128i  m128i;
  __m128   m128;
  float    mf[4];
  int8_t   m128i_i8[16];
  int16_t  m128i_i16[8];
	   int32_t  m128i_i32[4]; 
  int64_t  m128i_i64[2]; 
  uint8_t  m128i_u8[16];
  uint16_t m128i_u16[8];
  uint32_t m128i_u32[4];
  uint64_t m128i_u64[2];
} __oword;

#include <omp.h>
inline double now(void) {
  return omp_get_wtime();
}



void rebin2_simd( unsigned short *im,
		  int dim0,
		  int dim1,
		  char *dest){
  int i, j;
  __oword i0,i1;    // input row 0, row 1
  __oword t0,t1, t; // unpacked 16 -> 32 bits


  const __m128i vk0 = _mm_setzero_si128(); 

  assert( is_aligned( im  , 16) );
  //  assert( is_aligned( dest, 16) );
  
  for( i = 0 ; i < dim0; i = i+2 ){ // i loops on input rows
    for( j = 0; j < dim1; j = j+8 ){

      // load 8 values from 2 rows (16 values)
      //  00  01  02  03  04  05  06  07 
      i0.m128i = _mm_stream_load_si128( (__m128i *) &(im[    i*dim1 + j]) );
      //  10  11  12  13  14  15  16  17 
      i1.m128i = _mm_stream_load_si128( (__m128i *) &(im[(i+1)*dim1 + j]) );
      
      // unpack into int32 takes the first 4 values
      t0.m128i = _mm_cvtepu16_epi32(i0.m128i);
      //      printf("t0: %i %i %i %i\n", t0.m128i_i32[0], t0.m128i_i32[1], t0.m128i_i32[2], t0.m128i_i32[3]);

      t1.m128i = _mm_cvtepu16_epi32(i1.m128i);
      //      printf("t1: %i %i %i %i\n", t1.m128i_i32[0], t1.m128i_i32[1], t1.m128i_i32[2], t1.m128i_i32[3]);      

      // Sum across the rows - 4 values
      t.m128i = _mm_add_epi32( t0.m128i, t1.m128i );
      //      printf("t : %i %i %i %i\n", t.m128i_i32[0], t.m128i_i32[1], t.m128i_i32[2], t.m128i_i32[3]);      

      // unpack into int32 taking the last 4 values
      t0.m128i = _mm_cvtepu16_epi32( _mm_unpackhi_epi64(  i0.m128i, vk0 ));
      //      printf("t0: %i %i %i %i\n", t0.m128i_i32[0], t0.m128i_i32[1], t0.m128i_i32[2], t0.m128i_i32[3]);      
      t1.m128i = _mm_cvtepu16_epi32( _mm_unpackhi_epi64(  i1.m128i, vk0 ));
      //      printf("t1: %i %i %i %i\n", t1.m128i_i32[0], t1.m128i_i32[1], t1.m128i_i32[2], t1.m128i_i32[3]);      

      // Sum across the rows - 4 values
      t0.m128i = _mm_add_epi32( t0.m128i, t1.m128i );
      // printf("t0: %i %i %i %i\n", t0.m128i_i32[0], t0.m128i_i32[1], t0.m128i_i32[2], t0.m128i_i32[3]);      

      // Now horizontal add:
      t1.m128i = _mm_hadd_epi32( t.m128i, t0.m128i );

      //printf("i %d j %d : %i %i %i %i\n",i, j,
      //     t1.m128i_i32[0], t1.m128i_i32[1], t1.m128i_i32[2], t1.m128i_i32[3]);      

      // Now convert to char:


      if(1){
	// First go to float32:
	t1.m128 =  _mm_cvtepi32_ps( t1.m128i );

	// Take the square root:  65535 * 4 is 0>512
	t1.m128 =  _mm_sqrt_ps(t1.m128);

	// Back to int32:
	t1.m128i =  _mm_cvtps_epi32(t1.m128);

	//printf("i %d j %d : %i %i %i %i\n",i, j,
	//       t1.m128i_i32[0], t1.m128i_i32[1], t1.m128i_i32[2], t1.m128i_i32[3]);      


	// shift by 1 to divide by 2
	t1.m128i = _mm_srli_epi32(t1.m128i, 1);
      } else {
	// shift by 10 to divide by 65535*4/1024 = 
	t1.m128i = _mm_srli_epi32(t1.m128i, 10);
      }

      //printf("c: %d %d %d %d\n",t1.m128i_u8[0],t1.m128i_u8[4],t1.m128i_u8[8],t1.m128i_u8[12]);

      (*dest++) = t1.m128i_u8[0];
      (*dest++) = t1.m128i_u8[4];
      (*dest++) = t1.m128i_u8[8];
      (*dest++) = t1.m128i_u8[12];

    }
    
  }

}


int main ()
{
  
  unsigned short * data;
  char * binned;
  int dim0, dim1, i,j;
  double start, end;

  dim0=128;
  dim1=dim0;
  data = _mm_malloc( dim0*dim1*sizeof( unsigned short ), 16 );
  binned = _mm_malloc( dim0*dim1*sizeof( char )/4, 16 );

  for(i=0;i<dim0*dim1; i++) data[i]=i;


  start=now();

    rebin2_simd( data, dim0, dim1, binned);
  end=now();
  printf("That took %f ms\n",1e3*(end-start)/10);

  for(i=0;i<16/2;i++){
    for(j=0;j<16/2;j++){
      printf( "%4d ", (int)binned[i*dim1/2+j]) ;
    }
    printf("\n");
  }

  _mm_free(data);
  _mm_free(binned);

  return 0;
}
