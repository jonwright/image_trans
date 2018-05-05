
all : _imgtrans.so _imgtrans_omp.so

_imgtrans.so : _imgtrans.c Makefile
	gcc -std=c99 -shared -o _imgtrans.so -fPIC -O3  _imgtrans.c -Wall

_imgtrans_omp.so : _imgtrans.c Makefile
	gcc -fopenmp -DUSE_OMP -std=c99 -shared -o _imgtrans_omp.so -fPIC -O3  _imgtrans.c -Wall

test:	imgtrans.py _imgtrans_omp.so _imgtrans.so test_imgtrans.py
	python run_bench_omp.py
	 python -O test_imgtrans.py /data/id11/nanoscope/Commissioning/bliss/labradorite3_z3_/dt_y0025_/interlaced_1_1/Frelon/interlaced_1_1_Frelon0123.edf /data/id11/jon/wood_cell/els_2_6_topo_/els_2_6_topo_0023.edf
	python test_imgtrans.py

