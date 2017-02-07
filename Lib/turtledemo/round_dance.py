"""      turtle-example-suite:

         tdemo_round_dance.py

(Needs version 1.1 of the turtle module that
comes przy Python 3.1)

Dancing turtles have a compound shape
consisting of a series of triangles of
decreasing size.

Turtles march along a circle dopóki rotating
pairwise w opposite direction, przy one
exception. Does that przerwijing of symmetry
enhance the attractiveness of the example?

Press any key to stop the animation.

Technically: demonstrates use of compound
shapes, transformation of shapes jako well as
cloning turtles. The animation jest
controlled through update().
"""

z turtle zaimportuj *

def stop():
    global running
    running = Nieprawda

def main():
    global running
    clearscreen()
    bgcolor("gray10")
    tracer(Nieprawda)
    shape("triangle")
    f =   0.793402
    phi = 9.064678
    s = 5
    c = 1
    # create compound shape
    sh = Shape("compound")
    dla i w range(10):
        shapesize(s)
        p =get_shapepoly()
        s *= f
        c *= f
        tilt(-phi)
        sh.addcomponent(p, (c, 0.25, 1-c), "black")
    register_shape("multitri", sh)
    # create dancers
    shapesize(1)
    shape("multitri")
    pu()
    setpos(0, -200)
    dancers = []
    dla i w range(180):
        fd(7)
        tilt(-4)
        lt(2)
        update()
        jeżeli i % 12 == 0:
            dancers.append(clone())
    home()
    # dance
    running = Prawda
    onkeypress(stop)
    listen()
    cs = 1
    dopóki running:
        ta = -4
        dla dancer w dancers:
            dancer.fd(7)
            dancer.lt(2)
            dancer.tilt(ta)
            ta = -4 jeżeli ta > 0 inaczej 2
        jeżeli cs < 180:
            right(4)
            shapesize(cs)
            cs *= 1.005
        update()
    zwróć "DONE!"

jeżeli __name__=='__main__':
    print(main())
    mainloop()
