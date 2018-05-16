
/* transfer image across network
   ?   bin 2x2 or 3x3 or 4x4 etc
   ?   convert to 8 bit LUT
   ?   other compression
*/
#include <math.h>
#include <stdint.h>

#include <omp.h>


#define ALIGN 16

#ifdef _MSC_VER	
  __declspec(align(ALIGN),dllexport)	 char LUT[256*256];
#define restrict __restrict
#define DLL_EXPORT __declspec(dllexport)
#else
  char LUT[256*256] __attribute__((aligned(ALIGN)));
#define DLL_EXPORT 
#endif

DLL_EXPORT
int ALIGNMENT = ALIGN;


DLL_EXPORT
void pick2( unsigned short *restrict input,
	     int dim1,
	     int dim2,
	     char *restrict output){
  int i, j;
#pragma omp parallel for private(j)
  for( i = 0 ; i < dim1 ; i=i+2 ){
    for( j = 0; j < dim2 ; j=j+2 ) {
      output[ dim2*i/2 + j/2 ] = LUT[ input[ i*dim2 + j ] ] ;
    }
  }
}

DLL_EXPORT
void pick3( unsigned short *restrict input,
	     int dim1,
	     int dim2,
	     char *restrict output){
  int i, j;
#pragma omp parallel for private(j)
  for( i = 0 ; i < dim1 ; i=i+3 ){
    for( j = 0; j < dim2 ; j=j+3 ) {
      output[ dim2*i/3 + j/3 ] = LUT[ input[ i*dim2 + j ] ] ;
    }
  }
}

DLL_EXPORT
void pick4( unsigned short *restrict input,
	     int dim1,
	     int dim2,
	     char *restrict output){
  int i, j;
#pragma omp parallel for private(j)
  for( i = 0 ; i < dim1 ; i=i+4 ){
    for( j = 0; j < dim2 ; j=j+4 ) {
      output[ dim2*i/4 + j/4 ] = LUT[ input[ i*dim2 + j ] ] ;
    }
  }
}

DLL_EXPORT
void rebin2( unsigned short *restrict input,
	     int dim1,
	     int dim2,
	     char *restrict output){
  int odim1, odim2, io, jo, t;

  odim1 = dim1/2;
  odim2 = dim2/2;
  

#pragma omp parallel for private(jo, t)   
  for( io = 0 ; io < odim1 ; io++ ){
    for( jo = 0; jo < odim2 ; jo++ ) {
      t = ( input[ (io*2    )*dim2 + jo*2    ] +
 	    input[ (io*2    )*dim2 + jo*2 + 1] +
	    input[ (io*2 + 1)*dim2 + jo*2    ] +
	    input[ (io*2 + 1)*dim2 + jo*2 + 1] );
      output[ odim2*io + jo ] = LUT[t/4]; 
    }
  }
}

DLL_EXPORT
void rebin3( unsigned short *restrict input,
	     int dim1,
	     int dim2,
	     char *restrict output) {
  int odim1, odim2, io, jo, t;  
  odim1 = dim1/3;
  odim2 = dim2/3;
#pragma omp parallel for private(jo, t)   
  for( io = 0 ; io < odim1 ; io++ ){
    for( jo = 0; jo < odim2 ; jo++ ) {
      t = ( input[ (io*3    )*dim2 + jo*3    ] +
 	    input[ (io*3    )*dim2 + jo*3 + 1] +
 	    input[ (io*3    )*dim2 + jo*3 + 2] +	    
	    input[ (io*3 + 1)*dim2 + jo*3    ] +
	    input[ (io*3 + 1)*dim2 + jo*3 + 1] +
	    input[ (io*3 + 1)*dim2 + jo*3 + 2] +
	    input[ (io*3 + 2)*dim2 + jo*3    ] +
	    input[ (io*3 + 2)*dim2 + jo*3 + 1] +
	    input[ (io*3 + 2)*dim2 + jo*3 + 2] ) ;
      output[ odim2*io + jo ] = LUT[t/9]; 
    }
  }
}

DLL_EXPORT
void rebin4( unsigned short *restrict input,
	     int dim1,
	     int dim2,
	     char *restrict output) {
  int odim1, odim2, io, jo, t;  
  odim1 = dim1/4;
  odim2 = dim2/4;
#pragma omp parallel for private(jo, t)   
  for( io = 0 ; io < odim1 ; io++ ){
    for( jo = 0; jo < odim2 ; jo++ ) {
      t = ( input[ (io*4    )*dim2 + jo*4    ] +
 	    input[ (io*4    )*dim2 + jo*4 + 1] +
 	    input[ (io*4    )*dim2 + jo*4 + 2] +
 	    input[ (io*4    )*dim2 + jo*4 + 3] +
	    input[ (io*4 + 1)*dim2 + jo*4    ] +
 	    input[ (io*4 + 1)*dim2 + jo*4 + 1] +
 	    input[ (io*4 + 1)*dim2 + jo*4 + 2] +
 	    input[ (io*4 + 1)*dim2 + jo*4 + 3] +
	    input[ (io*4 + 2)*dim2 + jo*4    ] +
 	    input[ (io*4 + 2)*dim2 + jo*4 + 1] +
 	    input[ (io*4 + 2)*dim2 + jo*4 + 2] +
 	    input[ (io*4 + 2)*dim2 + jo*4 + 3] +
	    input[ (io*4 + 3)*dim2 + jo*4    ] +
 	    input[ (io*4 + 3)*dim2 + jo*4 + 1] +
 	    input[ (io*4 + 3)*dim2 + jo*4 + 2] +
	    input[ (io*4 + 3)*dim2 + jo*4 + 3] );
      output[ odim2*io + jo ] = LUT[t/16]; 
    }
  }
}


DLL_EXPORT
void setLUT( int minval, int maxval, int type){
  int i;
  float f,c,cm;
  for(i=0     ; i<=minval; i++) LUT[i]=0;
  for(i=maxval; i<=65535; i++)LUT[i]=255;
  if(type == 1){ /* log */
    c = 255./(log(maxval)-log(minval));
    cm = log(minval);
    for(i=minval; i<=maxval; i++){
      f = c*(log(i)-cm);
      LUT[i] = (char) round(f);
    }
    return;
  }
  if( type == 2){ /* sqrt */
    c = 255./(sqrt(maxval)-sqrt(minval));
    cm = sqrt(minval);
    for(i=minval; i<=maxval; i++){
      f = c*(sqrt(i)-cm);
      LUT[i] = (char) round(f);
    }
    return;
  }
  /* linear is the default, type == 0 etc */
  c = 255./(maxval-minval);
  for(i=minval; i<=maxval; i++){
    f = (i-minval)*c;
    LUT[i] = (char) round(f);
  }
}

/* to estimate possible speed of reading */
DLL_EXPORT
uint64_t imgsum( unsigned short *restrict im, int len){
  uint64_t s;
  int i;
  s=0;
#pragma omp parallel for reduction(+:s)
  for(i=0;i<len;i++){ s += im[i]; }
  return s;
}


/* to estimate possible speed of reading */
DLL_EXPORT
void imgstats( unsigned short *restrict im, int len,
	       uint64_t *sum, uint64_t *sum2,
	       uint16_t *mx, uint16_t *mn ){
  int i;

  *sum=0;
  *sum2=0;
  *mn=65535; /* limits for uint16 */
  *mx=0;
#pragma omp parallel 
  {
    uint64_t s=0, s2=0;
    uint16_t x=0, n=65535;
#pragma omp for
    for(i=0;i<len;i++){
      s  += im[i];
      s2 += im[i] * im[i] ;
      x = (im[i] > x) ? im[i] : x;
      n = (im[i] < n) ? im[i] : n;
    }
    #pragma omp critical
    {
    *sum  += s;
    *sum2 += s2;
    *mx = ( *mx > x ) ? *mx : x;
    *mn = ( *mn < x ) ? *mn : x;
    }
  }
}
