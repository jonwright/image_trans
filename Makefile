
# centos5 ; grr
CC=gcc44


all : _imgtrans.so 

_imgtrans.so : _imgtrans.c Makefile
	$(CC) -std=c99 -shared -fPIC -fopenmp -O3 -msse4.2 _imgtrans.c  -o _imgtrans.so

test:	imgtrans.py _imgtrans.so test_imgtrans.py
	python run_bench_omp.py
	OMP_NUM_THREADS=4 python -O test_imgtrans.py 

