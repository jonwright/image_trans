
from __future__ import print_function, division
import time
import sys
import numpy as np
import SocketServer, socket
import thread # for shutdown ?
import sps
import fabio

class cor( object ):
    """
    Image correction thing
    Reads spec shared memory
    Computes corrected data
    Rebins and reduces to char
    """
    def __init__(self, dark=None, flat=None ):
        """ 
        dark is a dark (background) image
        flat is the beam with no sample (includes dark)
        """
        if dark is not None:
            self.dark = dark
        else:
            self.dark = None
        if flat is not None:
            self.flat = flat
        else:
            self.flat = None
        self.update()

    def update(self):
        """
        fill in any cached stuff
        """
        pass
        
    def setdark( self, path, name  ):
        """ get the dark from shared memory (live view) """
        self.dark = sps.getdata( path, name )
        self.update()

    def setdarkfile( self, filename  ):
        """ get the dark from a file """
        self.dark = fabio.open( filename ).data
        self.update()

    def setflat( self, path, name ):
        """ get the flat from shared memory (live view) """
        self.flat = sps.getdata( path, name )
        self.update()

    def setflatfile( self, filename ):
        """ get the flat from a file """
        self.flat = fabio.open( filename ).data
        self.update()

    def correct( self, path, name ):
        """ Do correction and publish to some sps segment (which?)
        re-write in C/Cython to avoid overflow etc """
        data = sps.getdata( path, name )
        return (data - self.dark) / (self.flat - self.dark)

    def setLUT( self, minval, maxval, typ):
        """
        """
        pass
    
    def get_binned_LUT( self, path, name, binfac=4 ):
        """
        Rebin data from path, name
        """
        pass
    
    def correct_bin_LUT(self ):
        pass

    def status(self):
        """
        tell about the dark/flat/dims/LUT
        """
        

class MyTCPHandler(SocketServer.StreamRequestHandler):
    """
    The request handler class for our TCP server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        req = self.rfile.readline().strip().split()
        print ("From:",self.client_address,"<<<",req,">>>")
        global COR
        try:
            if req[0] == 'exit':
                print("Exiting!")
                self.wfile.write("Exiting!")
                def close_the_server(server):
                    server.socket.shutdown(socket.SHUT_RDWR)
                    server.socket.close()
                    server.shutdown()
                    server.server_close()
                thread.start_new_thread( close_the_server, (server,))
                return
            if hasattr( COR, req[0] ):
                print("Found ",req[0],"calling it with:", req[1:] )
                try:
                    ret = getattr( COR, req[0] )( *req[1:] )
                    self.wfile.write( ret )
                except Exception as e:
                    self.wfile.write(str(e)+"\n")
                    print(str(e))
                return
            self.wfile.write("I do not understand\n")
            time.sleep(5)
            self.wfile.write("Goodbye\n")
        except:
            raise



if __name__ == "__main__":

    try:
        sps.create( "viewer" ,"dkf", 2048, 2048, sps.FLOAT, sps.TAG_ARRAY )
    except:
        pass
    COR = cor()

    
    # specify empty host for any!
    HOST, PORT = "" , 12346
    # Create the server, binding to localhost on port 9999
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print("Server on port",PORT)
    try:
        server.serve_forever()
    except:
        server.socket.close()
        print("There was an exception")


teststring = """

dark LimaCCds(5008) Frelon_2
flood LimaCCds(5008) Frelon_2
correct LimaCCds(5008) Frelon_2
"""
