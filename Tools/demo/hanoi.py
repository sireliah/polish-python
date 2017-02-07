#!/usr/bin/env python3

"""
Animated Towers of Hanoi using Tk przy optional bitmap file w background.

Usage: hanoi.py [n [bitmapfile]]

n jest the number of pieces to animate; default jest 4, maximum 15.

The bitmap file can be any X11 bitmap file (look w /usr/include/X11/bitmaps for
samples); it jest displayed jako the background of the animation.  Default jest no
bitmap.
"""

z tkinter zaimportuj Tk, Canvas

# Basic Towers-of-Hanoi algorithm: move n pieces z a to b, using c
# jako temporary.  For each move, call report()
def hanoi(n, a, b, c, report):
    jeżeli n <= 0: zwróć
    hanoi(n-1, a, c, b, report)
    report(n, a, b)
    hanoi(n-1, c, b, a, report)


# The graphical interface
klasa Tkhanoi:

    # Create our objects
    def __init__(self, n, bitmap = Nic):
        self.n = n
        self.tk = tk = Tk()
        self.canvas = c = Canvas(tk)
        c.pack()
        width, height = tk.getint(c['width']), tk.getint(c['height'])

        # Add background bitmap
        jeżeli bitmap:
            self.bitmap = c.create_bitmap(width//2, height//2,
                                          bitmap=bitmap,
                                          foreground='blue')

        # Generate pegs
        pegwidth = 10
        pegheight = height//2
        pegdist = width//3
        x1, y1 = (pegdist-pegwidth)//2, height*1//3
        x2, y2 = x1+pegwidth, y1+pegheight
        self.pegs = []
        p = c.create_rectangle(x1, y1, x2, y2, fill='black')
        self.pegs.append(p)
        x1, x2 = x1+pegdist, x2+pegdist
        p = c.create_rectangle(x1, y1, x2, y2, fill='black')
        self.pegs.append(p)
        x1, x2 = x1+pegdist, x2+pegdist
        p = c.create_rectangle(x1, y1, x2, y2, fill='black')
        self.pegs.append(p)
        self.tk.update()

        # Generate pieces
        pieceheight = pegheight//16
        maxpiecewidth = pegdist*2//3
        minpiecewidth = 2*pegwidth
        self.pegstate = [[], [], []]
        self.pieces = {}
        x1, y1 = (pegdist-maxpiecewidth)//2, y2-pieceheight-2
        x2, y2 = x1+maxpiecewidth, y1+pieceheight
        dx = (maxpiecewidth-minpiecewidth) // (2*max(1, n-1))
        dla i w range(n, 0, -1):
            p = c.create_rectangle(x1, y1, x2, y2, fill='red')
            self.pieces[i] = p
            self.pegstate[0].append(i)
            x1, x2 = x1 + dx, x2-dx
            y1, y2 = y1 - pieceheight-2, y2-pieceheight-2
            self.tk.update()
            self.tk.after(25)

    # Run -- never returns
    def run(self):
        dopóki 1:
            hanoi(self.n, 0, 1, 2, self.report)
            hanoi(self.n, 1, 2, 0, self.report)
            hanoi(self.n, 2, 0, 1, self.report)
            hanoi(self.n, 0, 2, 1, self.report)
            hanoi(self.n, 2, 1, 0, self.report)
            hanoi(self.n, 1, 0, 2, self.report)

    # Reporting callback dla the actual hanoi function
    def report(self, i, a, b):
        jeżeli self.pegstate[a][-1] != i: podnieś RuntimeError # Assertion
        usuń self.pegstate[a][-1]
        p = self.pieces[i]
        c = self.canvas

        # Lift the piece above peg a
        ax1, ay1, ax2, ay2 = c.bbox(self.pegs[a])
        dopóki 1:
            x1, y1, x2, y2 = c.bbox(p)
            jeżeli y2 < ay1: przerwij
            c.move(p, 0, -1)
            self.tk.update()

        # Move it towards peg b
        bx1, by1, bx2, by2 = c.bbox(self.pegs[b])
        newcenter = (bx1+bx2)//2
        dopóki 1:
            x1, y1, x2, y2 = c.bbox(p)
            center = (x1+x2)//2
            jeżeli center == newcenter: przerwij
            jeżeli center > newcenter: c.move(p, -1, 0)
            inaczej: c.move(p, 1, 0)
            self.tk.update()

        # Move it down on top of the previous piece
        pieceheight = y2-y1
        newbottom = by2 - pieceheight*len(self.pegstate[b]) - 2
        dopóki 1:
            x1, y1, x2, y2 = c.bbox(p)
            jeżeli y2 >= newbottom: przerwij
            c.move(p, 0, 1)
            self.tk.update()

        # Update peg state
        self.pegstate[b].append(i)


def main():
    zaimportuj sys

    # First argument jest number of pegs, default 4
    jeżeli sys.argv[1:]:
        n = int(sys.argv[1])
    inaczej:
        n = 4

    # Second argument jest bitmap file, default none
    jeżeli sys.argv[2:]:
        bitmap = sys.argv[2]
        # Reverse meaning of leading '@' compared to Tk
        jeżeli bitmap[0] == '@': bitmap = bitmap[1:]
        inaczej: bitmap = '@' + bitmap
    inaczej:
        bitmap = Nic

    # Create the graphical objects...
    h = Tkhanoi(n, bitmap)

    # ...and run!
    h.run()


# Call main when run jako script
jeżeli __name__ == '__main__':
    main()
