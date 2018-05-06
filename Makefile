
all : _imgtrans.so 

_imgtrans.so : _imgtrans.o Makefile
	gcc  -shared -fPIC -fopenmp -O3 -msse4.2  -static -nostdlib _imgtrans.o  -o _imgtrans.so

_imgtrans.o : _imgtrans.c Makefile
	gcc -std=c99 -fPIC -fopenmp -O3 -msse4.2 -c _imgtrans.c -o _imgtrans.o

test:	imgtrans.py _imgtrans.so test_imgtrans.py
	python run_bench_omp.py
	OMP_NUM_THREADS=1 time python -O test_imgtrans.py /data/id11/nanoscope/Commissioning/bliss/labradorite3_z3_/dt_y0025_/interlaced_1_1/Frelon/interlaced_1_1_Frelon0123.edf /data/id11/jon/wood_cell/els_2_6_topo_/els_2_6_topo_0023.edf
	time python test_imgtrans.py

