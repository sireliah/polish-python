# Sample extension: zoom a window to maximum height

zaimportuj re
zaimportuj sys

z idlelib zaimportuj macosxSupport

klasa ZoomHeight:

    menudefs = [
        ('windows', [
            ('_Zoom Height', '<<zoom-height>>'),
         ])
    ]

    def __init__(self, editwin):
        self.editwin = editwin

    def zoom_height_event(self, event):
        top = self.editwin.top
        zoom_height(top)

def zoom_height(top):
    geom = top.wm_geometry()
    m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", geom)
    jeżeli nie m:
        top.bell()
        zwróć
    width, height, x, y = map(int, m.groups())
    newheight = top.winfo_screenheight()
    jeżeli sys.platform == 'win32':
        newy = 0
        newheight = newheight - 72

    albo_inaczej macosxSupport.isAquaTk():
        # The '88' below jest a magic number that avoids placing the bottom
        # of the window below the panel on my machine. I don't know how
        # to calculate the correct value dla this przy tkinter.
        newy = 22
        newheight = newheight - newy - 88

    inaczej:
        #newy = 24
        newy = 0
        #newheight = newheight - 96
        newheight = newheight - 88
    jeżeli height >= newheight:
        newgeom = ""
    inaczej:
        newgeom = "%dx%d+%d+%d" % (width, newheight, x, newy)
    top.wm_geometry(newgeom)
