from inquiry_stockdata import *
from getStockList import *
import time
import sqlite3
import numpy as np
from datetime import datetime

def init_trade():
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    return kiwoom

def updateDB(filename, dbname, table):
    tempcon = sqlite3.connect('temp.db')
    tempcur = tempcon.cursor()
    cmd = format("SELECT * FROM '%s'" % table)
    tempcur.execute(cmd)
    tempdata = tempcur.fetchall()
    tempcon.close()

    con = sqlite3.connect(filename)
    cursor = con.cursor()
    for i in tempdata:
        cmd = format("INSERT INTO '%s' (index, open, high, low, close, volume)" % table)
        cmd += format("VALUES(%s, %d, %d, %d, %d, %d)" % (i[0], i[1], i[2], i[3], i[4], i[5]))
        cursor.execute(cmd)
    con.close()
    return data

def updateData(filename, dbname, table):
    today = datetime.today().strftime("%Y%m%d")
    lastDay = loadDB_data(DBNAME + '.db', table[0])
    if lastDay[0][0] == today:
        print(filename + " is updated latest!")
        return 0

    app = QApplication(sys.argv)
    kiwoom = init_trade()
    kiwoom.setLastData(lastDay[0][0])
    kiwoom.setLimit(200)
    kiwoom.today = today

    codelist = loadStockList(filename)

    for i in range(0, 1): #len(codelist)):
        code = codelist[i]
        inquiry_stockdata(kiwoom, code, "temp.db")
        print("%4d - %s 종목 업데이트 완료되었습니다" % (i, code))
        updateDB(filename, DBNAME + '.db', code)
        time.sleep(1)

    print("\n-----DB 업데이트 종료-----")

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

DBNAME = 'kospi'
if __name__ == '__main__':
    table = loadDB_table(DBNAME+'.db')
    table = np.array(table).flatten().tolist()
    updateData(DBNAME + ".lst", DBNAME + '.db', table)

    count = 0
    #print(table[0:5])
    for i in table:
        data = loadDB_data(DBNAME+'.db', i)
        data_close = np.array(data)[:,4].tolist()
        data_close = list(map(int, data_close))
        avg5, avg20, avg60, avg120 = avgline(data_close, 10)

        number = isGood(avg5, avg20, avg60, avg120)
        if number:
            count+=1
            print(count, i, data[number][0], data[number][4])

    print("\n---- 끝 ----")



