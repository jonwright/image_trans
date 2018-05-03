
_imgtrans.so : _imgtrans.c
	gcc -shared -o _imgtrans.so -fPIC -O2 _imgtrans.c -Wall
