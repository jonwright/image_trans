
from cgi import parse_qs, escape

from PIL import Image, ImageDraw
import colormaps
import cStringIO

## TODO:
### populate list of shared memories
###  ask for log or linear and limits
###  ask for format (PNG|JPG)
### implement caching


home = b"""<!DOCTYPE html>
<html>
 <head>
 </head>
<body>

 <h> Hello There! </h>
 
 <img src="image.png" alt="An image"/>

</body>
</html>
"""


def getimg():
    im = Image.new( "P", (512,512))
    im.putpalette( colormaps.viridis )
    draw = ImageDraw.Draw(im)
    draw.line((50, 50) + im.size, fill=128)
    draw.line((80, im.size[1], im.size[0], 30), fill=128)
    del draw
    c = cStringIO.StringIO()
    im.save(c, format='PNG')
    return c.getvalue()

def app( env, start_response ):
    p = env['PATH_INFO']
    print("Incoming",p)
    if p == "/image.png":
        imgstr = getimg()
        with open("test.png","wb") as f:
            f.write( imgstr )
        print("write test.png")
        start_response('200 OK', [('Content-Type', 'image/png'),
                                  ('Content-Length', str(len(imgstr))) ] )
        return [imgstr]
    if p == "/":
        global home
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [home]
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'hello']


def demo(port = 12345):
    from  wsgiref.simple_server import make_server
    try:
        httpd = make_server( '', port, app )
        print('Serving on ',port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Exit!")
        

if __name__=="__main__":
    demo()



