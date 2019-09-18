import subprocess
subprocess.SW_HIDE = 1

for st in range(0, 2000, 100):
    cmd = r'python getStockList2.py kospi.lst %d %d 200 kospi.db'%(st, st+100)
    r = subprocess.Popen(cmd, shell=True).wait()
