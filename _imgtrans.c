
/* transfer image across network
   ?   bin 2x2 or 3x3 or 4x4 etc
   ?   convert to 8 bit LUT
   ?   other compression
*/
#include <math.h>
#include <stdint.h>

#include <omp.h>


#define ALIGN 16


char LUT[256*256] __attribute__((aligned(ALIGN)));
int ALIGNMENT = ALIGN;


void rebin2( unsigned short *restrict input,
	     int dim1,
	     int dim2,
	     char *restrict output){
  int odim1, odim2, io, jo, t;

  odim1 = dim1/2;
  odim2 = dim2/2;
  
#pragma omp parallel for simd aligned(input, output, LUT: ALIGN) private(jo, t)   
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

void rebin3( unsigned short *restrict input,
	     int dim1,
	     int dim2,
	     char *restrict output) {
  int odim1, odim2, io, jo, t;  
  odim1 = dim1/3;
  odim2 = dim2/3;
#pragma omp parallel for simd aligned(input, output, LUT: ALIGN) private(jo, t)   
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


void rebin4( unsigned short *restrict input,
	     int dim1,
	     int dim2,
	     char *restrict output) {
  int odim1, odim2, io, jo, t;  
  odim1 = dim1/4;
  odim2 = dim2/4;
#pragma omp parallel for simd aligned(input, output, LUT: ALIGN) private(jo, t)   
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
uint64_t imgsum( unsigned short *restrict im, int len){
  uint64_t s;
  int i;
  s=0;
#pragma omp parallel for simd aligned(im:16) reduction(+:s)
  for(i=0;i<len;i++){ s += im[i]; }
  return s;
}

/* to estimate possible speed of reading */
void imgstats( unsigned short *restrict im, int len,
	       uint64_t *sum, uint64_t *sum2,
	       uint16_t *mx, uint16_t *mn ){
  unsigned int i;
  uint64_t s, s2;
  uint16_t x, n;
  s=0;
  s2=0;
  n=65535; /* limits for uint16 */
  x=0;
#pragma omp parallel for simd aligned(im:ALIGN) reduction(+:s,s2), reduction(min:n),reduction(max:x)
    for(i=0;i<len;i++){
      s  += im[i];
      s2 += im[i] * im[i] ;
      x = (im[i] > x) ? im[i] : x;
      n = (im[i] < n) ? im[i] : n;
    }
  
  *sum=s;
  *sum2=s2;
  *mx=x;
  *mn=n;
}
