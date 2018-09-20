
#include <stdint.h>

#ifdef _MSC_VER	
#define restrict __restrict
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT 
#endif

void LUT( const uint16_t * restrict ,
	  uint8_t * restrict ,
	  uint16_t ,
	  int  );
