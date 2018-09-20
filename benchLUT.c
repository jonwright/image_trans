

#include "benchmark.h"
#include "il2lut.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define NPX 2048*2048

int main(){
  uint16_t *src;
  uint8_t *dst;
  int i;
  double start, end;

  src = (uint16_t *) malloc( sizeof( uint16_t) * NPX );
  dst = (uint8_t  *) malloc( sizeof( uint8_t ) * NPX );

  for( i=0 ; i<NPX ; i++)
    src[i] = i;

  for( i=0; i<10 ; i++){
    start = get_time();
    LUT( src, dst, 0, NPX);
    end = get_time();
    printf("# LUT took %g s\n", end-start);
  }
  
  free(src);
  free(dst);
  
  return 0;
}
