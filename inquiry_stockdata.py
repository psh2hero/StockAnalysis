import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import time
import pandas as pd
import sqlite3
from datetime import datetime

TR_REQ_TIME_INTERVAL = 0.2

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()
        self.totalcount = 0
        self.countlimit = 0
        self.lastday = str()
        self.today = str()
        self.netprofit = 0

    def setLimit(self, datacount):
        self.countlimit = datacount

    def setLastData(self, lastday):
        self.lastday = lastday

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10081_req":
            self._opt10081(rqname, trcode)
        elif rqname == "opt10001_req":
            self._opt10001(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _opt10081(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)
        self.totalcount += data_cnt
        if self.totalcount > self.countlimit:
            data_cnt -= (self.totalcount-self.countlimit)
            self.totalcount = self.countlimit

        for i in range(data_cnt):
            date = self._comm_get_data(trcode, "", rqname, i, "일자")
            open = self._comm_get_data(trcode, "", rqname, i, "시가")
            high = self._comm_get_data(trcode, "", rqname, i, "고가")
            low = self._comm_get_data(trcode, "", rqname, i, "저가")
            close = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")

            if date == self.lastday:
                self.totalcount = self.countlimit
                break

            self.ohlcv['date'].append(date)
            self.ohlcv['open'].append(int(open))
            self.ohlcv['high'].append(int(high))
            self.ohlcv['low'].append(int(low))
            self.ohlcv['close'].append(int(close))
            self.ohlcv['volume'].append(int(volume))

    def _opt10001(self, rqname, trcode):
        self.netprofit = self._comm_get_data(trcode, "", rqname, 0, "당기순이익")


def inquiry_stockdata(kiwoom, stockcode, dbname):
    #app = QApplication(sys.argv)
    #kiwoom = Kiwoom(datacount)
    #kiwoom.comm_connect()
    kiwoom.totalcount = 0
    kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

    # opt10081 TR 요청
    kiwoom.set_input_value("종목코드", stockcode)
    kiwoom.set_input_value("기준일자", kiwoom.today)
    kiwoom.set_input_value("수정주가구분", 1)
    kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

    #while kiwoom.remained_data == True:
    while kiwoom.totalcount < kiwoom.countlimit and kiwoom.remained_data == True:
        time.sleep(TR_REQ_TIME_INTERVAL)
        kiwoom.set_input_value("종목코드", stockcode)
        kiwoom.set_input_value("기준일자", kiwoom.today)
        #kiwoom.set_input_value("기준일자", "20190802")
        kiwoom.set_input_value("수정주가구분", 1)
        kiwoom.comm_rq_data("opt10081_req", "opt10081", 2, "0101")

    df = pd.DataFrame(kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'], index=kiwoom.ohlcv['date'])

    con = sqlite3.connect(dbname)
    df.to_sql(stockcode, con, if_exists='replace')


def inquiry_netprofit(kiwoom, stockcode):
    kiwoom.set_input_value("종목코드", stockcode)
    kiwoom.comm_rq_data("opt10001_req", "opt10001", 0, "0101")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    kiwoom.setLimit(20)
    while 1:
        print("종목코드를 입력하시오 : ", end="")
        stockcode = input()
        if stockcode != "":
            print("종목 조회 중...")
            #inquiry_stockdata(kiwoom, stockcode, 'kospi.db')
            #print("종목 조회 결과 kospi.db에 저장 완료")
            inquiry_netprofit(kiwoom, stockcode)
            kiwoom.netprofit == 0
            while(kiwoom.netprofit == 0):
                None
            print("종목 조회 완료 : 단기순이익 = ", kiwoom.netprofit)
        else:
            break

    print("종료")
