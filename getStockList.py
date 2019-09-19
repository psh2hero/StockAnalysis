from inquiry_stockdata import *
import os
import shutil

def saveStockList(filename, code_list):
    print(filename + "File is written.")
    file = open(filename, 'w')
    for code in code_list:
        file.write('%s\n' % code)
    file.close()

def loadStockList(filename):
    print(filename + " File is restored.")
    codelist = list()
    file = open(filename, 'r')

    while (1):
        line = file.readline()
        try:
            escape = line.index('\n')
        except:
            escape = len(line)
        if line:
            codelist.append(line[0:escape])
        else:
            break
    file.close()
    return codelist

def menu():
    print("1. 종목 리스트")
    print("2. 종목 조회 (DB저장)")
    print("3. 모두")
    print("무엇을 하시겠습니까? : ", end="")
    select = int(input())

    print("--- 시장 ---")
    print("1. 코스피")
    print("2. 코스닥")
    print("3. ETF")
    print("4. 전부")
    print("어느 시장의 종목 리스트를 원하나요? : ", end="")
    select_market = int(input())

    if select < 1 or select > 3:
        select = 0

    if select_market < 1 or select_market > 4:
        select_market = 0

    return select, select_market

market_list = list([[], ["코스피"], ["코스닥"], ["ETF"], ["코스피", "코스닥", "ETF"]])
market_dic = {"코스피": 0, "코스닥": 10, "ETF": 8}
market_lst = {"코스피": "kospi.lst", "코스닥": "kosdaq.lst", "ETF": "ETF.lst"}
market_db = {"코스피": "kospi.db", "코스닥": "kosdaq.db", "ETF": "ETF.db"}

def init_trade():
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    return kiwoom

def download_market_codelist(kiwoom, market):
    #app = QApplication(sys.argv)
    #kiwoom = init_trade()

    for m in market:
        code_list = kiwoom.get_code_list_by_market(market_dic[m])
        saveStockList(market_lst[m], code_list)
        print("<%s - total num : %d>"%(m,len(code_list)))
        print(code_list)

def saveAlldata(kiwoom, filename, start, end, count, dbname):
    kiwoom.setLimit(count)
    codelist = loadStockList(filename)

    if (start<0 or start>len(codelist)):
        start = 0

    for i in range(start, len(codelist)):
        code = codelist[i]
        inquiry_stockdata(kiwoom, code, dbname)
        print("%4d - %s 종목 조회 결과 %s에 저장 완료되었습니다" % (i, code, dbname))
        time.sleep(1)
        if i == end-1:
            return

    print("\n-----종료-----")


def saveAlldata_fast(kiwoom, filename, start, end, count, dbname):
    kiwoom.setLimit(count)
    codelist = loadStockList(filename)

    if start < 0 or start > len(codelist) or start > end:
        return

    for i in range(start, len(codelist)):
        code = codelist[i]
        inquiry_stockdata(kiwoom, code, dbname)
        print("%4d - %s 종목 조회 결과 %s에 저장 완료되었습니다" % (i, code, dbname))
        time.sleep(0.1)
        if i == end-1:
            return

    print("\n-----종료-----")


def backupDB(filename):
    print("%s를 backup하시겠습니까?(yes or no)" % filename, end="")
    ans = input()
    if ans == "yes":
        name, ext = os.path.splitext(filename)
        backupFilename = name + "_backup" + ext
        shutil.copy(filename, backupFilename)

if __name__ == "__main__":
    kiwoom = 0
    while 1:
        db, market = menu()

        if db and market and kiwoom == 0:
            app = QApplication(sys.argv)
            kiwoom = init_trade()

        if db == 1 or db==3:
            download_market_codelist(kiwoom, market_list[market])

        if db == 2 or db == 3:
            for m in market_list[market]:
                backupDB(market_db[m])
                print("시작 index : ", end="")
                start = int(input())
                saveAlldata(kiwoom, market_lst[m], start, -1, 200, market_db[m])


