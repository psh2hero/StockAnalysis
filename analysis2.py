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


def analysis_greater(a, b):
    return a > b


def analysis_low_high(avg1, avg2, index):
    ret = analysis_greater(avg1[index], avg2[index])
    ret &= analysis_greater(avg2[index + 2], avg1[index + 2])
    return ret


class Analysis:
    def __init__(self):
        self.codename = str()
        self.data = list()
        self.minmax = list([0 for i in range(11)])
        self.avg5 = list()
        self.avg20 = list()
        self.avg60 = list()
        self.avg120 = list()
        self.amount = list()

    def setCodename(self, code):
        self.codename = code

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

        step = (self.minmax[10] - self.minmax[0]) / 10.0
        for idx in range(1, 10):
            self.minmax[idx] = self.minmax[idx - 1] + step
            # print(i, self.minmax[i])

        if len(data_close) >= 120:
            for i in range(0, len(data_close) - 120):
                self.avg5.append(sum(data_close[i:i + 5]) // 5)
                self.avg20.append(sum(data_close[i:i + 20]) // 20)
                self.avg60.append(sum(data_close[i:i + 60]) // 60)
                self.avg120.append(sum(data_close[i:i + 120]) // 120)

    def cross_20_60_under120(self, start, duration):
        if (len(self.avg120) - start) < (duration + 10):
            return 0, 0

        for i in range(start, duration + start):
            ret = analysis_low_high(self.avg20, self.avg60, i)  # 60일선이 120일 선 위로 올라가는 시점
            ret &= analysis_greater(self.avg20[i] - self.avg20[i + 2], 0)  # 20일선이 올라가는 추세
            ret &= analysis_greater(self.avg120[i], self.data[i][4])  # 당시가가 60일선보다 작은 값
            ret &= analysis_greater(self.avg120[i], self.data[start][4])  # 현재가가 60일선보다 작은 값
            if ret:
                if analysis_greater(self.minmax[1], self.avg5[i]):
                    return i, 10
                elif analysis_greater(self.minmax[2], self.avg5[i]):
                    return i, 20
                elif analysis_greater(self.minmax[3], self.avg5[i]):
                    return i, 30
                # elif analysis_greater(self.minmax[4], self.avg5[i]):
                #     return i, 40
                # elif analysis_greater(self.minmax[5], self.avg5[i]):
                #     return i, 50
                #
                # return i, 60
        return 0, 0

    def cross_60_120_avg5(self, start, duration):
        if (len(self.avg120)-start) < (duration + 10):
            return 0, 0

        for i in range(start, duration + start):
            ret = analysis_low_high(self.avg60, self.avg120, i)  # 60일선이 120일 선 위로 올라가는 시점
            ret &= analysis_greater(self.minmax[5], self.avg5[i])  # 5일선이 max의 30% 아래일때
            ret &= analysis_greater(self.avg60[i] - self.avg60[i + 2], 0)  # 60일선이 올라가는 추세
            if ret:
                if analysis_greater(self.minmax[1], self.avg5[i]):
                    return i, 10
                elif analysis_greater(self.minmax[2], self.avg5[i]):
                    return i, 20
                elif analysis_greater(self.minmax[3], self.avg5[i]):
                    return i, 30
                elif analysis_greater(self.minmax[4], self.avg5[i]):
                    return i, 40
                elif analysis_greater(self.minmax[5], self.avg5[i]):
                    return i, 50

                return i, 60
        return 0, 0

    def cross_60_120_last(self, start, duration):
        if (len(self.avg120) - start) < (duration + 10):
            return 0, 0

        for i in range(start, duration + start):
            ret = analysis_low_high(self.avg60, self.avg120, i)  # 60일선이 120일 선 위로 올라가는 시점
            ret &= analysis_greater(self.minmax[5], self.data[start][4])  # 현재가가 max의 50% 아래일때
            ret &= analysis_greater(self.avg60[i] - self.avg60[i + 2], 0)  # 60일선이 올라가는 추세
            if ret:
                if analysis_greater(self.minmax[1], self.data[start][4]):
                    return i, 10
                elif analysis_greater(self.minmax[2], self.data[start][4]):
                    return i, 20
                elif analysis_greater(self.minmax[3], self.data[start][4]):
                    return i, 30
                elif analysis_greater(self.minmax[4], self.data[start][4]):
                    return i, 40
                elif analysis_greater(self.minmax[5], self.data[start][4]):
                    return i, 50

                return i, 60
        return 0, 0

    def analysis4(self, count):
        return 0


def analysis_cross_60_120_avg5(anal_list, start, duration):
    count = 0
    for anal in anal_list:
        (number, per) = anal.cross_60_120_avg5(start, duration)
        if number:
            count += 1
            print(count, anal.codename, anal.data[number][0], anal.data[number][4], per, "%")  # for cross_60_120_avg5
    print("---- 끝 ----")


def analysis_cross_60_120_last(anal_list, start, duration):
    count = 0
    for anal in anal_list:
        (number, per) = anal.cross_60_120_last(start, duration)
        if number:
            count += 1
            print(count, anal.codename, anal.data[number][0], anal.data[number][4], per, "%")  # for cross_60_120_avg5
    print("---- 끝 ----")


def analysis_cross_20_60_under120(anal_list, start, duration):
    count = 0
    for anal in anal_list:
        (number, per) = anal.cross_20_60_under120(start, duration)
        if number:
            count += 1
            print(count, anal.codename, anal.data[number][0], anal.data[number][4], per, "%")
    print("---- 끝 ----")


def menu():
    print("\n1. 120일선 & 200일선 골든 크로스(당시 5일선이 50%이하 가격)")
    print("2. 120일선 & 200일선 골든 크로스(현제가가 50%이하 가격)")
    print("3. 60일선 & 120일선 골든 크로스(당시 현재가가 200일선 보다 작을 때)")
    print("무엇을 하시겠습니까? : ", end="")
    sel = int(input())

    if sel < 1 or sel > 3:
        sel = 0
    return sel


def loadDB(dbname):
    anal_list = list()
    table = loadDB_table(dbname)
    table_list = np.array(table).flatten().tolist()
    print("Reading '%s' : 000000" % dbname, end="")
    for code in table_list:
        anal = Analysis()
        print("\b\b\b\b\b\b%s"%code, end="")
        data = loadDB_data(dbname, code)
        anal.setCodename(code)
        anal.setData(data)
        anal_list.append(anal)
    print("\rFinish reading '%s' " % dbname)
    return anal_list


if __name__ == '__main__':
    kospi_anal = loadDB('kospi.db')
    kosdaq_anal = loadDB('kosdaq.db')
    etf_anal = loadDB('etf.db')

    while(1):
        select = menu()
        if select == 1:
            print("---- 분석시작 ----")
            print("<Kospi>")

            analysis_cross_60_120_avg5(kospi_anal, 0, 5)
            print("<Kosdaq>")
            analysis_cross_60_120_avg5(kosdaq_anal, 0, 5)
            print("<ETF>")
            analysis_cross_60_120_avg5(etf_anal, 0, 10)
        elif select == 2:
            print("---- 분석시작 ----")
            print("<Kospi>")
            analysis_cross_60_120_last(kospi_anal, 0, 5)
            print("<Kosdaq>")
            analysis_cross_60_120_last(kosdaq_anal, 0, 5)
            print("<ETF>")
            analysis_cross_60_120_last(etf_anal, 0, 10)
        elif select == 3:
            print("---- 분석시작 ----")
            print("<Kospi>")
            analysis_cross_20_60_under120(kospi_anal, 0, 10)
            print("<Kosdaq>")
            analysis_cross_20_60_under120(kosdaq_anal, 0, 10)
            print("<ETF>")
            analysis_cross_20_60_under120(etf_anal, 0, 10)
        else:
            exit(1)