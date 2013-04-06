import sys
import socket
import json
import threading
import time

class stdout2str:
    def __init__(self):
        self.s = ""
    def write(self, buf):
        self.s += buf

def runFun(function_name):
    tempout = sys.stdout
    out = stdout2str()
    sys.stdout = out
    exec("temp_ret = %s"%(function_name))
    sys.stdout = tempout
    return out.s, temp_ret

def start_server():
    address = ('127.0.0.1', 2046)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind(address)
    s.listen(5)

    while True:
        ss, addr = s.accept()
        if myfilter(ss, addr):
            continue
        print 'got connected from',addr
        function_name = ss.recv(512)
        if function_name == "byebye":
            ss.send("byebye")
            ss.close()
            break
        t = threading.Thread(target=return_data,args=(ss,function_name,))
        t.start()

    s.close()
    exit()

def return_data(ss,function_name):
    sent_data = {}
    sent_data['stdout'],sent_data['return'] = runFun(function_name)
    ss.send(json.dumps(sent_data))
    ss.close()


def start_cli(function_name):
    # client
    address = ('127.0.0.1', 2046)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(address)
    s.send(function_name)
    rec = s.recv(512)
    data = rec
    while len(rec) == 512:
        try:
            rec = s.recv(512)
            data += rec
        except:
            break
    print 'the data received is',data
    s.close()
    exit()

def myfilter(ss, addr):
    allow_ip = ["127.0.0.1"]
    if addr[0] in allow_ip: return False
    return True

def fun():
    print "hello windiwld"
    for i in range(1000): print i,
    time.sleep(3)
    return 2046

if __name__ == '__main__':
    t_s = threading.Thread(target=start_server)
    t_s.start()

    t_c = threading.Thread(target=start_cli,args=("fun()",))
    t_c.start()

    t_c2 = threading.Thread(target=start_cli,args=("byebye",))
    t_c2.start()

    t_s.join()
    exit()