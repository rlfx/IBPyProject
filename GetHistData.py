#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ib.ext.Contract import Contract
from ib.opt          import ibConnection, message
from time            import sleep, strftime
import pandas as pd
import numpy as np

################# 請記得開啟 TWS 並將 API port 設定為 7496 ####################

# 存放歷史資料的變數
global hist
hist = []

# 歷史資料的 handler 
def my_hist_data_handler(msg):
    print(msg)
    # 當歷史資料跑完 = finished
    if "finished" in msg.date:
        # 確認結束連線
        print('disconnecting', con.disconnect())
        #  用 pandas 做好 hist 的 data frame 為 df, 設定要 call 回的資料行
        df = df = pd.DataFrame(index=np.arange(0, len(hist)), columns=('date', 'close' , 'volume'))
        # 開始將資料堆回 hist 
        for index, msg in enumerate(hist):
            df.loc[index,'date':'volume'] = msg.date, msg.close, msg.volume
        # show 一下 df 確認無誤    
        print(df )
    else:
        # 如果還沒結束就繼續把 msg append 到 hist 上頭
        hist.append(msg)
         
def makeStkContract(contractTuple):
    # 將需要的資料類型, 對到相應的合約格式
    newContract = Contract()
    newContract.m_symbol = contractTuple[0]
    newContract.m_secType = contractTuple[1]
    newContract.m_exchange = contractTuple[2]
    newContract.m_currency = contractTuple[3]
    newContract.m_expiry = contractTuple[4]
    newContract.m_strike = contractTuple[5]
    return newContract

if __name__ == '__main__':
    
    # 建立 IbPy 連線管道
    con = ibConnection()    
    #con.registerAll(watcher)
    # 註冊我們對回傳的 historicalData 要採取的 handler
    con.register(my_hist_data_handler, message.historicalData)
    # 開啟連線
    con.connect()
    sleep(1)
    # 設定要接回來的資料類型，在此為 EURUSD
    contractTuple = ('EUR', 'CASH', 'IDEALPRO', 'USD', '', 0.0, '')
    # 設定接回來的合約格式
    stkContract = makeStkContract(contractTuple)
    # 設定接回來的資料的時間格式(不能改,是對Ib提供的固定格式)
    endtime = strftime('%Y%m%d %H:%M:%S')   
    # 開始連線拿資料, "5 D" = 拿 5 天 , "1 hour" = 拿每小時資料 , "MIDPOINT" = 拿的報價形式
    # 關於 各種 bar size 與 duration 能拿的對應資料其實很有限
    # 請見 : http://xavierib.github.io/twsapidocs/historical_limitations.html
    con.reqHistoricalData(1,stkContract,endtime,"3 W","15 mins","MIDPOINT",1,1)
    sleep(2)
    con.disconnect()
    
## 在這上面就是從 Ib 拿歷史資料, 此行下方可以 run 你的 code 在 hist 資料做分析  ##    

    print("我是第1筆開盤價:",hist[1].open)
    print("我是第567筆最高價:",hist[567].high)
    
## 目前 bug : 好像有時候從 Ib 抓會沒抓到, 所以失敗可以再多跑幾次確認
## 然後留意資料不要抓太多, 越大的 duration 會要求你只能抓越大尺度的資料