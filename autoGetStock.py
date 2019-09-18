import subprocess
subprocess.SW_HIDE = 1

for st in range(0, 1600, 100):
    cmd = r'python getStockList2.py kospi.lst %d %d 200 kospi.db'%(st, st+100)
    r = subprocess.Popen(cmd, shell=True).wait()

for st in range(0, 1400, 100):
    cmd = r'python getStockList2.py kosdaq.lst %d %d 200 kosdaq.db'%(st, st+100)
    r = subprocess.Popen(cmd, shell=True).wait()

for st in range(300, 500, 100):
    cmd = r'python getStockList2.py ETF.lst %d %d 200 ETF.db'%(st, st+100)
    r = subprocess.Popen(cmd, shell=True).wait()
