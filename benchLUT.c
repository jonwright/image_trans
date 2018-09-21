

#include "benchmark.h"
#include "il2lut.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define NPX 2048*2048

void bench( uint16_t *src, uint8_t *dst1, uint8_t *dst2){
  int i, j;
  uint8_t shift;
  uint16_t vmin;
  double start, end;


  vmin  = 123;
  shift = 2;
  start = get_time();
  for( i=0; i<10 ; i++)  
    LUT_linear( src, dst1, vmin, shift, NPX);
  end = get_time();
  printf("#   LUT_linear      took    %g s\n", (end-start)/10.);
  

  start = get_time();
  for( i=0; i<10 ; i++)  
    LUT_linear_simd(src, dst2, vmin, shift, NPX);
  end = get_time();
  printf("#   LUT_linear_simd took    %g s\n", (end-start)/10.);
  
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
    LUT_nobranch( src, dst2, 0, NPX);
  end = get_time();
  printf("#   LUT_nobranch    took    %g s\n", (end-start)/10.);


  j = 0;
  for( i=0; i<NPX ; i++ ){
    if(dst1[i] != dst2[i])j++;
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

  
}


int main( int argc, char** argv ){
  uint16_t *src;
  uint8_t *dst1, *dst2;
  int i;

  src  = (uint16_t *) malloc( sizeof( uint16_t) * NPX );
  dst1 = (uint8_t  *) malloc( sizeof( uint8_t ) * NPX );
  dst2 = (uint8_t  *) malloc( sizeof( uint8_t ) * NPX );


  printf("# Random array\n");
  for( i=0 ; i<NPX ; i++)
    src[i] = rand();
  bench( src, dst1, dst2 );

  printf("# Sequential array\n");
  for( i=0 ; i<NPX ; i++)
    src[i] = i;
  bench( src, dst1, dst2 );

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
