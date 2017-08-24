from ib.opt import ibConnection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order
import time

global order_id
order_id = 0

def print_message_from_ib(msg):
    if msg.typeName == "managedAccounts":
        global account_code
        account_code = msg.accountsList
        print("accountCode:", account_code)
    if msg.typeName == "updatePortfolio":
        global position
        position = msg.position
        print("position:", position)

def my_BidAsk(msg):
    if msg.field == 1:
        global Gbid
        Gbid = msg.price
        print("bid:", Gbid)
    if msg.field == 2:
        global Gask
        Gask = msg.price
        print("ask:", Gask)
    trading_logic()

def trading_logic():
    global order_id
    order_id = order_id + 1
    print("orderId:", order_id)
    mktOrder = Order()
    mktOrder.m_totalQuantity = 100
    mktOrder.m_orderType = 'LMT'
    mktOrder.m_action = 'SELL'
    mktOrder.m_lmtPrice = Gbid + 0.001
    print("Make Order", order_id, ": ", mktOrder.m_action, " ", mktOrder.m_lmtPrice)
    conn.placeOrder(order_id, newContract, mktOrder)

def main():
    global conn

    ##get contract
    global newContract
    newContract = Contract()
    newContract.m_symbol = 'EUR'#買入物
    newContract.m_secType = 'CASH'#股票,外匯
    newContract.m_exchange = 'IDEALPRO'#交易所
    newContract.m_currency = 'USD'#交易貨幣

    conn = ibConnection()
    conn.registerAll(print_message_from_ib)
    conn.register(my_BidAsk, message.tickPrice)
    conn.connect()
    
    tickID = 0
    conn.reqMktData(tickID, newContract, '',False)
    
    time.sleep(1)
    conn.disconnect()

main()