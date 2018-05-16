
# centos5 ; grr
# CC=gcc44

CC = gcc
CFLAGS = -std=c99 -shared -fopenmp  -O3 -msse4.2 -o 


ifeq ($(OS), Windows_NT)
	shlib = dll
#	CC = cl
#	CFLAGS = /LD /openmp /O2 /OUT:
else
	shlib = so
endif

all : _imgtrans.$(shlib)  test_simd


_imgtrans.$(shlib) : _imgtrans.c Makefile
	$(CC) _imgtrans.c $(CFLAGS)_imgtrans.$(shlib)


test_simd : test_simd.c
	$(CC) test_simd.c -msse4.2 -Wall -std=c99 -g -fopenmp -O3 -o test_simd



test:	imgtrans.py _imgtrans.$(shlib) test_imgtrans.py
	python run_bench_omp.py
	python test_imgtrans.py 

