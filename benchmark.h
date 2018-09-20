

/* https://stackoverflow.com/questions/2349776/how-can-i-benchmark-c-code-easily
 */

#include <stddef.h>
double get_time();

#ifdef WIN32

#include <windows.h>
double get_time()
{
    LARGE_INTEGER t, f;
    QueryPerformanceCounter(&t);
    QueryPerformanceFrequency(&f);
    return (double)t.QuadPart/(double)f.QuadPart;
}
#else
#include <sys/time.h>
double get_time()
{
    struct timeval t;
    gettimeofday(&t, NULL);
    return t.tv_sec + t.tv_usec*1e-6;
}
#endif



