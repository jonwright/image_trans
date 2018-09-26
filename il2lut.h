
#include <stdint.h>

#include <smmintrin.h>
#include <emmintrin.h>

#ifndef NTMAX
// Max threads to use - we dont want too many...
#define NTMAX 8
#endif

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
  //  __m64i   m64i[2];
  __m64    m64[2];
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


typedef union w4 {
  float    single;
  int8_t   i8[4];
  int16_t  i16[2];
  int32_t  i32; 
  uint8_t  u8[4];
  uint16_t u16[2];
  uint32_t u32;
} w4;



#ifdef _MSC_VER	
#define restrict __restrict
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT 
#endif


void LUT_branch( const uint16_t * restrict ,
		 uint8_t * restrict ,
		 uint16_t ,
		 int  );

void LUT_simple( const uint16_t * restrict ,
		   uint8_t * restrict ,
		   uint16_t ,
		   int  );


void LUT_nobranch( const uint16_t * restrict ,
		   uint8_t * restrict ,
		   uint16_t ,
		   int  );

void LUT_linear ( const uint16_t * restrict ,
		  uint8_t * restrict ,
		  uint16_t ,
		  uint8_t ,
		  uint16_t *,
		  uint16_t *,
		  int  );

void LUT_linear_simd ( const uint16_t * restrict ,
		       uint8_t * restrict ,
		       uint16_t ,
		       uint8_t ,
		       uint16_t *,
		       uint16_t *,
		       int  );

void LUT_log_simd ( const uint16_t * restrict ,
			 uint8_t * restrict ,
			 uint16_t ,
			 int );

void LUT_logfloat ( const uint16_t * restrict ,
			 uint8_t * restrict ,
			 uint16_t ,
			 int );


void LUT_logfl_simd ( const uint16_t * restrict ,
			 uint8_t * restrict ,
			 uint16_t ,
		      int, int );


void LUT_logDEB ( const uint16_t * restrict ,
			 uint8_t * restrict ,
			 uint16_t ,
			 int );
