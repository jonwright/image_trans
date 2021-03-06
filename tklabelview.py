
from __future__ import print_function, division

import time, sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
from PIL import Image, ImageTk
import numpy as np

import colormaps

class mainWindow():
    times=1
    delay=0
    timestart=time.time()
    data=np.array(np.random.random((512,512))*100,dtype=np.uint8)
    im = None
    p = colormaps.viridis
    
    def __init__(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root, width=512, height=512)
        self.frame.pack()
        self.label = tk.Label( self.frame ) 
        self.label.pack()
        self.root.after(self.delay, self.start) # INCREASE THE 0 TO SLOW IT DOWN
        self.root.mainloop()

        
        
    def start(self):
        global data
        if self.im is None:
            self.im=Image.frombuffer('P',
                                 (self.data.shape[1],
                                  self.data.shape[0]),
                                 self.data.astype('b').tostring() )
            self.im.putpalette( self.p )
            self.photo = ImageTk.PhotoImage(image=self.im)
            self.label.configure( image = self.photo )
        else:
            self.im.putdata( self.data.astype('b').tostring() )
            self.photo.paste( self.im )
        self.root.update_idletasks()
        self.times+=1
        if self.times%33==0:
            print ( "%.02f FPS"%(self.times/(time.time()-self.timestart)),
                    end="\r" )
        self.root.after(self.delay,self.start)
        self.data=np.roll(self.data,-1,1)

if __name__ == '__main__':
    x=mainWindow()
