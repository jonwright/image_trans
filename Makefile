
CC = gcc
# CC=clang
# centos5 ; grr
# CC=gcc44


CFLAGS = -std=c99 -fPIC -fopenmp  -O3 -march=native -Wall -o
CFLAGS = -std=c99 -fPIC -fopenmp  -O3 -msse4.2 -Wall -o


ifeq ($(OS), Windows_NT)
	shlib = dll
#	CC = cl
#	CFLAGS = /LD /openmp /O2 /OUT:
else
	shlib = so
endif

all : _imgtrans.$(shlib)  test_simd benchLUT _img_simple.$(shlib)


_imgtrans.$(shlib) : _imgtrans.c Makefile
	$(CC) _imgtrans.c -shared $(CFLAGS)_imgtrans.$(shlib)

_img_simple.$(shlib) : img_simple.py
	python img_simple.py
	$(CC) img_simple.c  -shared $(CFLAGS) _img_simple.$(shlib)



test_simd : test_simd.c
	$(CC) test_simd.c -msse4.2 -Wall -std=c99 -g -fopenmp -O3 -o test_simd

benchLUT : benchLUT.c il2lut.c il2lut.h benchmark.h
	$(CC) benchLUT.c il2lut.c $(CFLAGS) benchLUT && ./benchLUT

test:	imgtrans.py _imgtrans.$(shlib) test_imgtrans.py
	python run_bench_omp.py
	python test_imgtrans.py 
	python test_imgsimple.py | tee img_simple.timing
