
import os
for i in range(1,8):
    os.environ["OMP_NUM_THREADS"]=str(i)
    os.system("python bench_omp.py")
