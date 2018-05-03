
/* transfer image across network
   ?   bin 2x2 or 3x3 or 4x4 etc
   ?   convert to 8 bit LUT
   ?   other compression
*/
#include <math.h>

char LUT[256*256];

void rebin2( unsigned short input[],
	     int dim1,
	     int dim2,
	     char output[]) {
  int odim1, odim2, io, jo, t;  
  odim1 = dim1/2;
  odim2 = dim2/2;
  for( io = 0 ; io < odim1 ; io++ ){
    for( jo = 0; jo < odim2 ; jo++ ) {
      t = ( input[ (io*2    )*dim2 + jo*2    ] +
 	    input[ (io*2    )*dim2 + jo*2 + 1] +
	    input[ (io*2 + 1)*dim2 + jo*2    ] +
	    input[ (io*2 + 1)*dim2 + jo*2 + 1] ) / 4 ;
      output[ odim2*io + jo ] = LUT[t]; 
    }
  }
}

void rebin3( unsigned short input[],
	     int dim1,
	     int dim2,
	     char output[]) {
  int odim1, odim2, io, jo, t;  
  odim1 = dim1/3;
  odim2 = dim2/3;
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
	    input[ (io*3 + 2)*dim2 + jo*3 + 2] ) / 9 ;
      output[ odim2*io + jo ] = LUT[t]; 
    }
  }
}


void rebin4( unsigned short input[],
	     int dim1,
	     int dim2,
	     char output[]) {
  int odim1, odim2, io, jo, t;  
  odim1 = dim1/4;
  odim2 = dim2/4;
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
	    input[ (io*4 + 3)*dim2 + jo*4 + 3] ) / 16;
      output[ odim2*io + jo ] = LUT[t]; 
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

