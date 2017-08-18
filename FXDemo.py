from ib.opt import Connection
import time
    
def print_message_from_ib(msg):
    print(msg)
    
def main():
    conn = Connection.create(port=7496, clientId=0)
    conn.registerAll(print_message_from_ib)
    conn.connect()
        
    time.sleep(1) #Simply to give the program time to print messages sent from IB
    conn.disconnect()
    
if __name__ == "__main__": main()