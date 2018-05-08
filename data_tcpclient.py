

import socket
import sys
import time

def read_array( host, port, cmd='data' ):
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.connect((host, port))
        sock.sendall(cmd+'\n')
        received = []
        while 1:
            data = sock.recv(65535)
            if not data:
                break
            received.append(data)
    finally:
        sock.close()
    return "".join(received)

if __name__=="__main__":
    HOST, CMD, PORT = "localhost", "data", 12346
    try:
        HOST = sys.argv[1]
        CMD = sys.argv[2]
        PORT = int(sys.argv[3])
    except:
        pass
    start = time.time()
    received = read_array( HOST, PORT, cmd=CMD )
    end = time.time()
    #                    k     M
    MBS = len(received)/(1024.*1024.)/(end-start)
    print "Received: ",len(received),"in %s s"%(end-start)," %.2f MB/s"%(MBS)
