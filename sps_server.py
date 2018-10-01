
from __future__ import print_function, division

import numpy as np, time, img_simple
import SocketServer, socket, thread
try:
    import sps
except:
    pass

class spslocalproxy():
    """  for local """
    def __init__(self):
        # set up caching if we want to
        self.cache = {}
        
    def getarraynames(self):
        """ returns the arraynames """
        names = []
        for s in sps.getspeclist():
            for a in sps.getarraylist(s):
                names.append("%s@%s"%(s,a))
        return names

    def isupdated(self, name ):
        """ returns the data """
        specname, arrayname = name.split("@")
        d = sps.isupdated( specname, arrayname )
        return d

    def getdata(self, name, imin=64, outsize=512 ):
        """ returns the data as 8 bit """
        specname, arrayname = name.split("@")
        d = sps.getdata( specname, arrayname )
        data = np.require( d, dtype=np.uint16,
                           requirements=["C_CONTIGUOUS", "ALIGNED"] )
        outshape = list(data.shape)
        n=1
        while np.max(outshape) > outsize:
            n*=2
            outshape = [i//2 for i in outshape]
        binned = img_simple.log2bytesimd( img_simple.rebin( data, n ),
                                          minval = imin )
        # self.cache[ (specname, arrayname, imin, outsize ) ]
        return binned

    def onexit(self):
        pass

class spsremoteproxy():
    def __init__(self, host, port ):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(True)
        self.sock.settimeout(5.0)
        self.sock.connect( (self.host, self.port ) )
        self.rfile = self.sock.makefile("r")
        self.wfile = self.sock.makefile("w")
        
    def isupdated( self, name ):
        cmd = "isupdated %s\n"%( name )
        self.wfile.write( cmd )
        self.wfile.flush()
        resp = self.rfile.read(2)
        #print( "in isupdated, got",resp,"sent", cmd )
        return int(resp)
    
    def getarraynames( self ):
        cmd = "getarraynames\n"
        self.wfile.write( cmd )
        self.wfile.flush()
        resp = self.rfile.read(1024)
        # print("In getarraynames, got",resp)
        names = [name.rstrip() for name in resp.split("\n")
                 if name.find("@")>0 ]
        return names
    

    def getdata( self, name, imin=64, outsize=512 ):
        start=time.time()
        cmd = "getdata %s %d %d\n"%(name, imin, outsize )
        self.wfile.write( cmd )
        self.wfile.flush()
        #self.wfile.write( h.tostring() ) # int32 * 3
        #self.wfile.write( s )
        s0,s1,l = np.fromstring( self.rfile.read( 12 ), np.uint32 )
        # print(s0,s1,l)
        data = self.rfile.read(l)
        # print(len(data))
        data = np.frombuffer( data, dtype=np.uint8 )
        data.shape = s0, s1
        print("Reading data, takes %.3f ms",1000*(time.time()-start))
        return data

    def onexit( self ):
        print("Sending exit")
        self.wfile.write( "exit\n" )
        self.wfile.flush()
        
class DataHandler(SocketServer.StreamRequestHandler):
    """ Handle remote requests """
    def handle(self):
        global SPSPROXY
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        #self.socket.setblocking(True)
        #self.socket.settimeout(1.)
        while True:
            req = self.rfile.readline().strip().split()
            print('req',time.time(),req)
            print ("From:",self.client_address,"<<<",req,">>>")
            if len(req) == 0:
                print("Returning")
                return
            if req[0] == 'exit':
                print("Got an exit")
                self.wfile.write("Exiting!")
                self.wfile.flush()
                def close_the_server(server):
                    server.socket.shutdown(socket.SHUT_RDWR)
                    server.socket.close()
                    server.shutdown()
                    server.server_close()
                thread.start_new_thread( close_the_server, (server,))
                return
            if req[0].startswith( "isupdated"):
                name = req[1]
                print(req,name)
                if SPSPROXY.isupdated(name):
                    self.wfile.write("1\n")
                else:
                    self.wfile.write("0\n")
                self.wfile.flush()                        
                continue
            if req[0].startswith( "getdata" ):
                name, imin, outsize = req[1:]
                imin = int(imin)
                outsize = int(outsize)
                print(req, name, imin, outsize )
                d = SPSPROXY.getdata( name, imin, outsize )
                s = d.tostring()
                h = np.array( (d.shape[0],d.shape[1],len(s)), np.uint32 )
                self.wfile.write( h.tostring() )
                self.wfile.write( s )
                self.wfile.flush()
                continue
            if req[0].startswith( "getarraynames" ):
                s = "\n".join( SPSPROXY.getarraynames() )
                self.wfile.write("%-1024s"%(s))
                self.wfile.flush()
                print("Wrote arraynames")
                continue
            print("Not understood")
            




if __name__ == "__main__":
    SPSPROXY = spslocalproxy()
    HOST, PORT = "" , 12346
    # Create the server, binding to localhost on port PORT
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer((HOST, PORT), DataHandler)
    server.socket.setblocking(True)
    server.socket.settimeout(1.0)
    print("Server on port",PORT,"interrupt the program with Ctrl-C")
    try:
        server.serve_forever()
    except:
        server.socket.close()
        print("There was an exception")

