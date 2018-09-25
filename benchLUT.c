

#include "benchmark.h"
#include "il2lut.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define NPX 2048*2048

void bench( uint16_t *src, uint8_t *dst1, uint8_t *dst2, int debug){
  int i, j, k;
  uint8_t shift;
  uint16_t vmin, imgmin, imgmax, trumax, trumin;
  double start, end;
  uint8_t *dst3;

  trumax = src[0];
  trumin = src[0];
  for( i = 1; i<NPX ; i++){
    trumax = ( trumax > src[i] ) ? trumax : src[i] ;
    trumin = ( trumin < src[i] ) ? trumin : src[i] ;
  }

  
  dst3 = (uint8_t  *) malloc( sizeof( uint8_t ) * NPX );

  vmin  = 123;
  shift = 2;
  
  start = get_time();
  for( i=0; i<10 ; i++)  
    LUT_linear( src, dst1, vmin, shift, &imgmin, &imgmax, NPX);
  end = get_time();
  printf("#   LUT_linear      took    %g s", (end-start)/10.);
  if( (trumax == imgmax) && (trumin == imgmin)){
    printf(" min/max OK\n");
  } else {
    printf(" min: %d vs %d   max: %d vs %d\n",trumin,imgmin,trumax,imgmax);
  }
	  

  start = get_time();
  for( i=0; i<10 ; i++)  
    LUT_linear_simd(src, dst2, vmin, shift, &imgmin, &imgmax, NPX);
  end = get_time();
  printf("#   LUT_linear_simd took    %g s", (end-start)/10.);

  if( (trumax == imgmax) && (trumin == imgmin)){
    printf(" min/max OK\n");
  } else {
    printf(" min: %d vs %d   max: %d vs %d\n",trumin,imgmin,trumax,imgmax);
  }

  
  j = 0;
  for( i=0; i<NPX ; i++ ){
    if(dst1[i] != dst2[i])j++;
  }
  if (j != 0){ printf("#  %d errors\n",j); }
  
  
  start = get_time();  
  for( i=0; i<10 ; i++)
    LUT_branch( src, dst1, 0, NPX);
  end = get_time();
  printf("#   LUT_branch      took    %g s\n", (end-start)/10.);
  
  for( i=0; i<NPX; i++) dst2[i]=0;


start = get_time();  
  for( i=0; i<10 ; i++)
    LUT_simple( src, dst2, 0, NPX);
  end = get_time();
  printf("#   LUT_simple      took    %g s\n", (end-start)/10.);
  j = 0;
  for( i=0; i<NPX ; i++ ){
    if(dst1[i] != dst2[i])j++;
    dst3[i] = dst1[i];
  }
  if (j != 0){ printf("%d errors\n",j); }
  
  for( i=0; i<NPX; i++) dst2[i]=0;
  
  
  start = get_time();
  for( i=0; i<10 ; i++)  
    LUT_nobranch( src, dst2, 0, NPX);
  end = get_time();
  printf("#   LUT_nobranch    took    %g s\n", (end-start)/10.);

  j = 0;
  for( i=0; i<NPX ; i++ ){
    if(dst1[i] != dst2[i])j++;
    dst3[i] = dst1[i];
  }
  if (j != 0){ printf("%d errors\n",j); }


  for( i=0; i<NPX; i++) dst2[i]=0;
  start = get_time();
  for( i=0; i<10 ; i++)  
    LUT_log_simd( src, dst2, 0, NPX);
  end = get_time();
  printf("#   LUT_log_simd    took    %g s\n", (end-start)/10.);

  j = 0;
  for( i=0; i<NPX ; i++ ){
    if(dst1[i] != dst2[i])j++;
  }
  if (j != 0){ printf("%d errors\n",j); }


  for( i=0; i<NPX; i++) dst2[i]=0;
  start = get_time();
  for( i=0; i<10 ; i++)  
    LUT_logfloat( src, dst2, 0, NPX);
  end = get_time();
  printf("#   LUT_logfloat    took    %g s\n", (end-start)/10.);

  j = 0;
  for( i=0; i<NPX ; i++ ){
    if(dst1[i] != dst2[i])j++;
  }
  if (j != 0){ printf("%d errors\n",j); }

  for( i=0; i<NPX; i++) dst2[i]=0;
  start = get_time();
  for( i=0; i<10 ; i++)  
    LUT_logDEB( src, dst2, 0, NPX);
  end = get_time();
  printf("#   LUT_logDEB      took    %g s\n", (end-start)/10.);

  j = 0;
  for( i=0; i<NPX ; i++ ){
    if(dst1[i] != dst2[i])j++;
  }
  if (j != 0){ printf("%d errors\n",j); }

  for( i=0; i<NPX; i++) dst2[i]=0;
  start = get_time();
  for( i=0; i<10 ; i++)  
    LUT_logfl_simd( src, dst2, 0, NPX, debug);
  end = get_time();
  printf("#   LUT_logfl_simd  took    %g s\n", (end-start)/10.);

  j = 0;
  k = 0;
  for( i=0; i<NPX ; i++ ){
    if(dst1[i] != dst2[i]) j++;
    if(dst1[i] != dst3[i]) k++;
  }
  if (j != 0){ printf("%d %d errors\n",j, k); }

  free(dst3);

}


int main( int argc, char** argv ){
  uint16_t *src;
  uint8_t *dst1, *dst2;
  int i;

  src  = (uint16_t *) malloc( sizeof( uint16_t) * NPX );
  dst1 = (uint8_t  *) malloc( sizeof( uint8_t ) * NPX );
  dst2 = (uint8_t  *) malloc( sizeof( uint8_t ) * NPX );




  printf("# Sequential array\n");
  for( i=0 ; i<NPX ; i++)
    src[i] = (uint16_t) i;
  bench( src, dst1, dst2,0 );

  printf("# Random array\n");
  for( i=0 ; i<NPX ; i++)
    src[i] = (uint16_t) rand();
  bench( src, dst1, dst2,0 );

  printf("# Random array, clipped to 123:56789\n");
  for( i=0 ; i<NPX ; i++)
    src[i] = ( src[i] < 123 ) ? 123 :
      ( (src[i] > 56789) ? 56789 : src[i]    ) ;
  bench( src, dst1, dst2,0 );

  

  if ( argc > 1 ){
    for( i=0;i<(1<<16);i++){
      printf("%d %d %d %d\n", i  , src[i  ], dst1[i  ], dst2[i  ]);
    }
  }
  
  free(src);
  free(dst1);
  free(dst2);
  
  return 0;
}
