
import SocketServer, socket
import numpy as np
import thread
import time

DATA = np.arange(128*1024).astype(np.uint8).tobytes()
print(len(DATA))

class DataHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        req = self.rfile.readline().strip().split()
        print ("From:",self.client_address,"<<<",req,">>>")
        try:
            if req[0] == 'exit':
                self.wfile.write("Exiting!")
                def close_the_server(server):
                    server.socket.shutdown(socket.SHUT_RDWR)
                    server.socket.close()
                    server.shutdown()
                    server.server_close()
                thread.start_new_thread( close_the_server, (server,))
                return
            if req[0] == 'data':
                self.wfile.write( DATA )
                return # closes the connection - signals end
            else:
                self.wfile.write( "Sorry, i did not understand you" )
        except:
            raise

if __name__=="__main__":
    HOST, PORT = "" , 12346
    # Create the server, binding to localhost on port 9999
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer((HOST, PORT), DataHandler)
    print("Server on port",PORT,"interrupt the program with Ctrl-C")
    try:
        server.serve_forever()
    except:
        server.socket.close()
        print("There was an exception")
