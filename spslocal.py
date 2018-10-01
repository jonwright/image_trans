
from __future__ import print_function, division

import time, sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
    
from PIL import Image, ImageTk
import numpy as np

import fabio
import img_simple
import colormaps
import sps_server

class spslocalwin():
    def __init__( self ):
        self.cache = {}

        self.root = tk.Tk()

        self.imin=90
        self.im = None
        self.pal = colormaps.viridis
        #
        # Array selection

        #
        #
        #self.proxy = sps_server.spslocalproxy()
        self.proxy = sps_server.spsremoteproxy("lid11frelon1.esrf.fr",12346 )
        names = self.proxy.getarraynames()
        self.arraystring = tk.StringVar()
        self.arraystring.set(names[0])
        self.arrayselection = tk.OptionMenu( self.root,
                                             self.arraystring,
                                             *names )
        self.arrayselection.pack(side=tk.TOP)
        self.arraystring.trace( 'w', self.changed )
        #
        #
        self.frame = tk.Frame(self.root, width=512, height=512)
        self.frame.pack()
        self.label = tk.Label( self.frame ) 
        self.label.pack()
        
        self.onscreen = ""
        self.root.after( 100, self.changed )
        self.root.mainloop()

    def changed(self, *args):
        """ user made a new selection """
        name = self.arraystring.get()
        print("name changed to name",name)
        self.checkdata( name )
        
    def checkdata( self, name ):
        print("Checking",name)
        if self.proxy.isupdated( name ) or name not in self.cache:
            data=self.proxy.getdata( name )
            self.cache[name] = data
            self.onscreen = ""
        else:
            print("No change")
        self.render( name )    
#        self.root.after(100, self.changed )

    def render(self, name):
        if name == self.onscreen:
            print("Skip render,done" )
        binned = self.cache[name]
        if self.im is None:
            self.im=Image.frombuffer('P',
                                     (binned.shape[1],
                                      binned.shape[0]),
                                      binned.astype('b').tostring(),
                                      "raw",'P',0,1)
                                     
            self.im.putpalette( self.pal )
            self.photo = ImageTk.PhotoImage(image=self.im)
            self.label.configure( image = self.photo )
            self.onscreen = name
        else:
            self.im.putdata( binned.astype('b').tostring() )
            self.photo.paste( self.im )
            self.onscreen = name
            
    
if __name__ == '__main__':
    x=spslocalwin()
    
