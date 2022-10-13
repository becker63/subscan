from dis import findlinestarts
from multiprocessing import context
from pydoc import resolve
import signal
from contextlib import contextmanager
import ipaddress
import threading, queue
import socket
import re
import subprocess
from termcolor import colored

sub = "10.150.0.0/16"
q = queue.Queue()
out_q = queue.Queue()

def fping(ip):
    error = -1
    try:
        output = subprocess.check_output(f"timeout 0.1 fping -c 1 {ip}", shell=True, stderr=subprocess.DEVNULL)
        error = 1
    except subprocess.CalledProcessError as e:
        error = -1
    return(error)


def namecheck():
    while True:
        ip = q.get()

        host = socket.getfqdn(str(ip))

        if sub[0:5] not in host:
            full = ip + " : " + colored(host, "green")
            out_q.put(full)
            print(full)
        else:
                if fping(ip) == 1:
                    full = ip + " : " + colored(ip, "green")
                    out_q.put(full)
                    print(full)

                else:
                    print(ip + " : " + colored(ip, "red"))
        q.task_done()
            

def get_ip_from_subnet(ip_subnet):
    ips= ipaddress.ip_network(ip_subnet)
    for ip in ips:
        q.put(str(ip))




def main():
    # turn-on the worker thread
    get_ip_from_subnet(sub)
    for x in range(200):
        threading.Thread(target=namecheck, daemon=True).start()

    # block until all tasks are done
    q.join()
    print('All work completed')
    print("\n\n\n")
    
    while True:
        try:
            msg = out_q.get_nowait()
        except queue.Empty:
            break
        print(msg)
        

    
main()