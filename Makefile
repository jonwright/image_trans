
_imgtrans.so : _imgtrans.c
	gcc -shared -o _imgtrans.so -fPIC -Ofast _imgtrans.c -Wall

test:	imgtrans.py _imgtrans.so
	python imgtrans.py
	python imgtrans.py /data/id11/nanoscope/Commissioning/bliss/labradorite3_z3_/dt_y0025_/interlaced_1_1/Frelon/interlaced_1_1_Frelon0123.edf /data/id11/jon/wood_cell/els_2_6_topo_/els_2_6_topo_0023.edf
