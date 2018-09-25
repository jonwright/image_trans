
import time
from pyopengltk import OpenGLFrame 
import Tkinter as tk
from OpenGL import GL
import numpy as np

class FixedWin(OpenGLFrame):
    
    data  = (np.random.random((512,512,3))*128).astype(np.uint8)
    
    def initgl(self):
        GL.glViewport( 0, 0, self.width, self.height)
        GL.glClearColor(1.0,1.0,1.0,0.0)
        self.changed_data = True
        
    def redraw(self):
        if self.changed_data:
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)
            w,h = self.width, self.height
            GL.glDrawPixels(w, h, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, self.data)
            self.changed_data = False

    def set(self,data):
        self.data[:,:,:] = data
        self.changed_data = True
        self.redraw( )

root=tk.Tk()
root.title("Fixed OpenGL display")
a = FixedWin( root, width=512, height=512 )
a.pack_propagate(False)
a.pack()
a.animate=1000/24 # fps
root.resizable(0,0)

def ping_me( ):
    data  = np.roll( a.data, 3 )
    a.set( data )
    root.after( 1, ping_me )
    root.update()

root.after( 100, ping_me )
root.mainloop()
