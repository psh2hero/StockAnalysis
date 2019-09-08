from inquiry_stockdata import *
from getStockList import *
import time
import sqlite3
import numpy as np
from datetime import datetime

def loadDB_table(filename):
    con = sqlite3.connect(filename)
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table = cursor.fetchall()
    con.close()
    return table

def loadDB_data(filename, tablename):
    con = sqlite3.connect(filename)
    cursor = con.cursor()
    cmd = format("SELECT * FROM '%s'" % tablename)
    cursor.execute(cmd)
    data = cursor.fetchall()
    con.close()
    return data

class analysis():
    def __init__(self):
        self.data = list()
        self.minmax = list([0 for i in range(11)])
        self.avg5 = list()
        self.avg20 = list()
        self.avg60 = list()
        self.avg120 = list()
        self.amount = list()

    def setData(self, data):
        self.data = list(data)
        self.avg5 = list()
        self.avg20 = list()
        self.avg60 = list()
        self.avg120 = list()
        self.amount = list()

        if not data:
            return

        data_close = np.array(data)[:, 4].tolist()
        data_close = list(map(int, data_close))
        self.minmax[10] = max(data_close)
        self.minmax[0] = min(data_close)

        amount = np.array(data)[:, 5].tolist()
        self.amount = list(map(int, amount))

        step = (self.minmax[10] - self.minmax[0])/10.0
        for idx in range(1, 10):
            self.minmax[idx] = self.minmax[idx-1] + step
            #print(i, self.minmax[i])

        if len(data_close) >= 120:
            for i in range(0, len(data_close)-120):
                self.avg5.append(sum(data_close[i:i + 5]) // 5)
                self.avg20.append(sum(data_close[i:i + 20]) // 20)
                self.avg60.append(sum(data_close[i:i + 60]) // 60)
                self.avg120.append(sum(data_close[i:i + 120]) // 120)

    def analysis_greater(self, a, b):
        return a > b

    def analysis_low_high(self, avg1, avg2, index):
        ret = self.analysis_greater(avg1[index], avg2[index])
        ret &= self.analysis_greater(avg2[index+2], avg1[index+2])
        return ret

    def analysis1(self, count):
        if len(self.avg120) < (count+10):
            return 0

        for i in range(count):
            ret =  self.analysis_low_high(self.avg60, self.avg120, i)   # 60일선이 120일 선 위로 올라가는 시점
            ret &= self.analysis_greater(self.minmax[3], self.avg5[i])  # 5일선이 max의 30% 아래일때
            ret &= self.analysis_greater(self.avg60[i] - self.avg60[i+2], 0)  # 60일선이 올라가는 추세
            if ret:
                return i

        return 0

    def analysis2(self, count):
        if len(self.avg120) < (count+10):
            return (0, 0)

        for i in range(count):
            ret = self.analysis_low_high(self.avg60, self.avg120, i)   # 60일선이 120일 선 위로 올라가는 시점
            ret &= self.analysis_greater(self.minmax[5], self.avg5[i])  # 현재가가 max의 30% 아래일때
            ret &= self.analysis_greater(self.avg60[i] - self.avg60[i+2], 0)  # 60일선이 올라가는 추세
            if ret:
                if self.analysis_greater(self.minmax[1], self.avg5[i]):
                    return i, 10
                elif self.analysis_greater(self.minmax[2], self.avg5[i]):
                    return i, 20
                elif self.analysis_greater(self.minmax[3], self.avg5[i]):
                    return i, 30
                elif self.analysis_greater(self.minmax[4], self.avg5[i]):
                    return i, 40
                elif self.analysis_greater(self.minmax[5], self.avg5[i]):
                    return i, 50

                return i, 60
        return 0, 0

    def analysis3(self, count):
        if len(self.avg120) < (count+10):
            return 0

        for i in range(count):
            ret = self.analysis_low_high(self.avg60, self.avg120, i)   # 60일선이 120일 선 위로 올라가는 시점
            ret &= self.analysis_greater(self.minmax[3], self.data[0][4])  # 현재가가 max의 30% 아래일때
            ret &= self.analysis_greater(self.avg60[i] - self.avg60[i+2], 0)  # 60일선이 올라가는 추세
            if ret:
                return i

        return 0

    def analysis4(self, count):
        if len(self.avg120) < (count+10):
            return 0

        for i in range(count):
            ret = self.analysis_greater(self.amount[i], self.amount[i+1]*2)
            #ret &= self.analysis_greater(self.amount[i+1], self.amount[i+2]*2)
            #ret &= self.analysis_greater(self.amount[i+2], self.amount[i+3])
            #ret &= self.analysis_greater(self.amount[i+3], self.amount[i+4])
            #ret &= self.analysis_greater(self.amount[i+4], self.amount[i+5])
            if ret:
                return i

        return 0

if __name__ == '__main__':
    table_group = ['kospi.db', 'kosdaq.db', 'etf.db']

    number1 = number2 = number3 = number4 = per = 0
    for t in table_group:
        print("---- 분석시작 (%s) ----"%t)
        table = loadDB_table(t)
        table = np.array(table).flatten().tolist()

        anal = analysis()
        count = 0
        #print(table[0:5])
        for i in table:
            data = loadDB_data(t, i)
            anal.setData(data)
            (number2, per) = anal.analysis2(5)
            #number4 = anal.analysis4(2)
            if number2:
                count+=1
                print("\b\b\b\b\b\b", end="")
                print(count, i, data[number2][0], data[number2][4], per, "%")  # for analysis2
            elif number4:
                count+=1
                print("\b\b\b\b\b\b", end="")
                print(count, i, data[number4][0], data[number4][4])
            else:
                print("\b\b\b\b\b\b"+i, end="")

        print("\b\b\b\b\b\b---- 끝 ----\n")



