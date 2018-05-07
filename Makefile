
all : _imgtrans.so 

_imgtrans.so : _imgtrans.o Makefile
	gcc  -shared -fPIC -fopenmp -O3 -msse4.2  -static -nostdlib _imgtrans.o  -o _imgtrans.so

_imgtrans.o : _imgtrans.c Makefile
	gcc -std=c99 -fPIC -fopenmp -O3 -msse4.2 -c _imgtrans.c -o _imgtrans.o

test:	imgtrans.py _imgtrans.so test_imgtrans.py
	python run_bench_omp.py
	OMP_NUM_THREADS=4 python -O test_imgtrans.py 

