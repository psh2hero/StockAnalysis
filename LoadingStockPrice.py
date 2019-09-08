import requests
from bs4 import BeautifulSoup

#MK: 한국 주식 가격 및 주식 종목 번호 검색

class mkGetStockPrice:
    def __init__(self):
        self.__webAddr = "https://finance.naver.com/item/main.nhn?code="
        self.__codeAddr = "http://www.ksfc.co.kr/services/loan/avg/popup/codes.do"
    #MK: Get Stock Price from NAVER Web
    def getPrice(self, codeNum):
        if not isinstance(codeNum, str):
            print("MK: First parameter must be String")
            return None
        webAddr = self.__webAddr + codeNum
        htmlStr = requests.get(webAddr).text
        soup = BeautifulSoup(htmlStr, 'html.parser')
        priceList = []
        for price in soup.select("dl[class=blind]"):
            if "현재가" in price.text:
                priceList = price.text.split()
                break
        currentPriceIndex = priceList.index("현재가")
        tmp = priceList[currentPriceIndex + 1]
        tmp = tmp.replace(",", "")
        currentPrice = int(tmp)
        return currentPrice
    # MK: Get Stock Code Number from KSFC (한국증권금융) webstie
    def getCodeNum(self, stockName):
        if not isinstance(stockName, str):
            print("MK: First parameter must be String")
            return None
        #MK: Post Data를 가져오기 위해서 출처 2 참조
        postData = {"findStr": stockName}
        codeReq = requests.post(self.__codeAddr, postData)
        htmlStr = codeReq.text
        soup = BeautifulSoup(htmlStr, "html.parser")
        codeList = []
        for code in soup.select("tr"):
            if stockName in code.text:
                tmp = code.text.split()
                if tmp.index(stockName):
                    codeList = code.text.split()
                    break
        retCodeNum = None
        if len(codeList) > 0:
            retCodeNum = codeList[0]
        return retCodeNum

if __name__ == "__main__":
    tmp = mkGetStockPrice()
    print(tmp.getCodeNum("삼성전자"))
    print(tmp.getPrice("005930"))
    print(tmp.getPrice(tmp.getCodeNum("현대자동차")))