#!/usr/bin/env python3
"""     turtlegraphics-example-suite:

             tdemo_forest.py

Displays a 'forest' of 3 breadth-first-trees
similar to the one w tree.
For further remarks see tree.py

This example jest a 'breadth-first'-rewrite of
a Logo program written by Erich Neuwirth. See
http://homepage.univie.ac.at/erich.neuwirth/
"""
z turtle zaimportuj Turtle, colormode, tracer, mainloop
z random zaimportuj randrange
z time zaimportuj clock

def symRandom(n):
    zwróć randrange(-n,n+1)

def randomize( branchlist, angledist, sizedist ):
    zwróć [ (angle+symRandom(angledist),
              sizefactor*1.01**symRandom(sizedist))
                     dla angle, sizefactor w branchlist ]

def randomfd( t, distance, parts, angledist ):
    dla i w range(parts):
        t.left(symRandom(angledist))
        t.forward( (1.0 * distance)/parts )

def tree(tlist, size, level, widthfactor, branchlists, angledist=10, sizedist=5):
    # benutzt Liste von turtles und Liste von Zweiglisten,
    # fuer jede turtle eine!
    jeżeli level > 0:
        lst = []
        brs = []
        dla t, branchlist w list(zip(tlist,branchlists)):
            t.pensize( size * widthfactor )
            t.pencolor( 255 - (180 - 11 * level + symRandom(15)),
                        180 - 11 * level + symRandom(15),
                        0 )
            t.pendown()
            randomfd(t, size, level, angledist )
            uzyskaj 1
            dla angle, sizefactor w branchlist:
                t.left(angle)
                lst.append(t.clone())
                brs.append(randomize(branchlist, angledist, sizedist))
                t.right(angle)
        dla x w tree(lst, size*sizefactor, level-1, widthfactor, brs,
                      angledist, sizedist):
            uzyskaj Nic


def start(t,x,y):
    colormode(255)
    t.reset()
    t.speed(0)
    t.hideturtle()
    t.left(90)
    t.penup()
    t.setpos(x,y)
    t.pendown()

def doit1(level, pen):
    pen.hideturtle()
    start(pen, 20, -208)
    t = tree( [pen], 80, level, 0.1, [[ (45,0.69), (0,0.65), (-45,0.71) ]] )
    zwróć t

def doit2(level, pen):
    pen.hideturtle()
    start(pen, -135, -130)
    t = tree( [pen], 120, level, 0.1, [[ (45,0.69), (-45,0.71) ]] )
    zwróć t

def doit3(level, pen):
    pen.hideturtle()
    start(pen, 190, -90)
    t = tree( [pen], 100, level, 0.1, [[ (45,0.7), (0,0.72), (-45,0.65) ]] )
    zwróć t

# Hier 3 Baumgeneratoren:
def main():
    p = Turtle()
    p.ht()
    tracer(75,0)
    u = doit1(6, Turtle(undobuffersize=1))
    s = doit2(7, Turtle(undobuffersize=1))
    t = doit3(5, Turtle(undobuffersize=1))
    a = clock()
    dopóki Prawda:
        done = 0
        dla b w u,s,t:
            spróbuj:
                b.__next__()
            wyjąwszy:
                done += 1
        jeżeli done == 3:
            przerwij

    tracer(1,10)
    b = clock()
    zwróć "runtime: %.2f sec." % (b-a)

jeżeli __name__ == '__main__':
    main()
    mainloop()
