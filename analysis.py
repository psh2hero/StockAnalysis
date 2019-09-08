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

def avgline(data, count):
    avg5 = list()
    avg20 = list()
    avg60 = list()
    avg120 = list()

    if len(data)<(count+120):
        return avg5, avg20, avg60, avg120

    for i in range(0, count):
        avg5.append(sum(data[i:i + 5]) // 5)
        avg20.append(sum(data[i:i + 20]) // 20)
        avg60.append(sum(data[i:i + 60]) // 60)
        avg120.append(sum(data[i:i + 120]) // 120)

    return avg5, avg20, avg60, avg120

def isGood(avg5, avg20, avg60, avg120):
    for i in range(len(avg120)-2):
        if avg60[i]>avg120[i] \
                and avg60[i+2]<avg120[i+2] \
                and (avg5[i]-avg5[i+2])>0 \
                and (avg20[i]-avg20[i+2])>0 \
                and (avg60[i]-avg60[i+2])>0:
            #print(i, avg60[i], avg5[i])
            return i

    return 0


DEF_SAVE_ALL_DATA = 0  # 주가정보를 모두 받아오려면 1로 설정, 분석용이면 0으로 설정
if __name__ == '__main__':
    if DEF_SAVE_ALL_DATA:
        saveAlldata("kosdaq.lst", 200, 'kosdaq.db')
        exit(1)

    table = loadDB_table('./kospi.db')
    table = np.array(table).flatten().tolist()

    count = 0
    #print(table[0:5])
    for i in table:
        data = loadDB_data('./kospi.db', i)
        data_close = np.array(data)[:,4].tolist()
        data_close = list(map(int, data_close))
        avg5, avg20, avg60, avg120 = avgline(data_close, 10)

        number = isGood(avg5, avg20, avg60, avg120)
        if number:
            count+=1
            print(count, i, data[number][0], data[number][4])

    print("\n---- 끝 ----")



