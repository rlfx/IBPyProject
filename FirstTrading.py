from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import ibConnection, message
from time import sleep
import pandas as pd
import datetime as dt

class FirstTrading:
    def __init__(self, qty, resample_interval, averaging_period):
        self.order_id = 1
        self.symbol_id = 0
        self.qty = qty
        self.averaging_period = averaging_period
        self.con = None
        self.FXContract = None
        self.bid_price = 0
        self.ask_price = 0
        self.last_prices = pd.DataFrame(columns=[self.symbol_id])
        self.is_position_opened = False
        self.account_code = None
        self.unrealized_pnl = 0
        self.realized_pnl = 0
        self.position = 0            

    def price_tick_handler(self, msg):
        if msg.typeName == "nextValidId":
            self.order_id = msg.orderID
        elif msg.typeName == "managedAccounts":
            self.account_code = msg.accountsList
        elif msg.typeName == "updatePortfolio" and msg.contract.m_symbol == self.symbol:
            self.unrealized_pnl = msg.unrealizedPNL
            self.realized_pnl = msg.realizedPNL
            self.position = msg.position
        elif msg.typeName == "error" and msg.id != -1:
            return
        
    def my_BidAsk(self, msg):
        if msg.field == 1:
            self.bid_price = msg.price
        elif msg.field == 2:
            self.ask_price = msg.price
        elif msg.field == 4:
            self.last_prices.loc[dt.datetime.now()] = msg.price
            resampled_prices = self.last_prices.resample(self.resample_interval,
                                                         how="last",
                                                         fill_method="ffill")
        self.average_price = resampled_prices.tail(self.averaging_period).mean()[0]
        self.perform_trade_logic()
        
    def makeContract(self):
        newContract = Contract()
        newContract.m_symbol = 'EUR'
        newContract.m_secType = 'CASH'
        newContract.m_exchange = 'IDEALPRO'
        newContract.m_currency = 'USD'
        return newContract

    def makeOrder(self, action, price = None):
        newOrder = Order()
        newOrder.m_totalQuantity = self.qty
        newOrder.m_action = action
        if price is not None:
            newOrder.m_orderType = 'LMT'
            newOrder.m_lmtPrice = price
        else:
            newOrder.m_orderType = 'MKT'
        return newOrder

    def perform_trade_logic(self):
        is_buy_signal = self.ask_price < self.average_price
        is_sell_signal = self.bid_price > self.average_price
        print(dt.datetime.now(), " BUY/SELL? ", is_buy_signal, "/", is_sell_signal, \
              " Avg:", self.average_price)
        if self.average_price != 0 and self.bid_price != 0 and self.ask_price != 0 \
        and self.position == 0 and not self.is_position_opened:
            if is_sell_signal:
                order = self.makeOrder('SELL', self.qty)
                self.con.placeOrder(self.order_id, self.FXContract, order)
                self.is_position_opened = True
            elif is_buy_signal:
                order = self.makeOrder('BUY', self.qty)
                self.con.placeOrder(self.order_id, self.FXContract, order)
                self.is_position_opened = True
        elif self.is_position_opened:
            if self.position > 0 and is_sell_signal:
                order = self.makeOrder('SELL', self.qty)
                self.con.placeOrder(self.order_id, self.FXContract, order)
                self.is_position_opened = False
            elif self.position < 0 and is_buy_signal:
                order = self.makeOrder('BUY', self.qty)
                self.con.placeOrder(self.order_id, self.FXContract, order)
                self.is_position_opened = False
                
    def error_handler(self, msg):
        if msg.typeName == "error" and msg.id != -1:
            print("Server Error:", msg)
                
    def start(self):
        
        self.con = ibConnection()
        self.con.registerAll(self.price_tick_handler)
        self.con.register(self.error_handler, 'Error')
        self.con.register(self.my_BidAsk, message.tickPrice, message.tickSize)
        self.con.connect()
  
        print ('* * * * REQUESTING MARKET DATA * * * *')
        self.FXContract = self.makeContract()
        self.con.reqMktData(self.symbol_id, self.FXContract, '', False)
        sleep(1)
        
        print ('* * * * REQUESTING ACCOUNT UPDATES * * * *')
        self.con.reqAccountUpdates(True, self.account_code)
        
        while True:
            sleep(1)
        
        self.con.cancelMktData(self.symbol_id)
        self.con.disconnect()