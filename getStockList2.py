from getStockList import *

if __name__ == "__main__":
    import sys

    db_list = sys.argv[1]
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    number = int(sys.argv[4])
    db_filename = sys.argv[5]

    print(sys.argv)
#    print("db_list = " + db_list)
#    print("start = " + start)
#    print("end = " + end)
#    print("number = " + number)
#    print("db_filename = " + db_filename)

    app = QApplication(sys.argv)
    kiwoom = init_trade()

    try:
        saveAlldata_fast(kiwoom, db_list, start, end, number, db_filename)
    except:
        print("Error!\npython filename.lst start_index number filename.db")