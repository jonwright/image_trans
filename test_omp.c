
#define NPX 2048*2048
#include <omp.h>
#include <time.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

uint64_t dosum( unsigned short *img );
uint64_t dosum_simd( unsigned short *img );
uint64_t dosum_parallel_for( unsigned short *img );
uint64_t dosum_parallel_for_simd( unsigned short *img );
void bench( uint64_t (*f)( unsigned short *), unsigned short * img,
	    char* s
	    );

uint64_t dosum_simd( unsigned short *img ){
  uint64_t s=0;
#pragma omp simd aligned(img:__BIGGEST_ALIGNMENT__) reduction(+:s)
  for( int i = 0; i<NPX ; i++) s += img[i];
  return s;
}

uint64_t dosum_parallel_for( unsigned short *img ){
  uint64_t s=0;
#pragma omp parallel for reduction(+:s) schedule(static)
  for( int i = 0; i<NPX ; i++) s += img[i];
  return s;
}

uint64_t dosum_parallel_for_simd( unsigned short *img ){
  uint64_t s=0;
#pragma omp parallel for simd aligned(img:__BIGGEST_ALIGNMENT__) reduction(+:s) schedule(static)
  for( int i = 0; i<NPX ; i++) s += img[i];
  return s;
}

uint64_t dosum( unsigned short *img ){
  uint64_t s=0;
  for( int i = 0; i<NPX ; i++) s += img[i];
  return s;
}

inline double my_clock(void) {
  return omp_get_wtime();
}

void bench( uint64_t (*f)( unsigned short *), unsigned short * img,
	    char* s
	    ){
  double tic,toc;
  uint64_t t0;
  int i;
  i=0;
  tic = my_clock();
  while(++i){
    t0 = (*f)(img);
    toc = my_clock();
    if( (toc - tic)>1 ) break;
  }
  
printf("%lu %s: %d %.2f ms \n",t0,s,i,(toc-tic)*1e3/i);
}


int main(){
  int i;
  unsigned short *img = (unsigned short*)
    aligned_alloc(__BIGGEST_ALIGNMENT__ , NPX*sizeof(unsigned short) );

  for(i=0;i<NPX;i++) img[i]=42+i;
  
  bench( dosum, img, "dosum");
  bench( dosum_simd, img,"simd");
  bench( dosum_parallel_for, img,"pfor");
  bench( dosum_parallel_for_simd, img,"psimd");
  
  free(img);
  return 0;
}
