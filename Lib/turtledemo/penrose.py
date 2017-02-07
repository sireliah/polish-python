#!/usr/bin/env python3
"""       xturtle-example-suite:

          xtx_kites_and_darts.py

Constructs two aperiodic penrose-tilings,
consisting of kites oraz darts, by the method
of inflation w six steps.

Starting points are the patterns "sun"
consisting of five kites oraz "star"
consisting of five darts.

For more information see:
 http://en.wikipedia.org/wiki/Penrose_tiling
 -------------------------------------------
"""
z turtle zaimportuj *
z math zaimportuj cos, pi
z time zaimportuj clock, sleep

f = (5**0.5-1)/2.0   # (sqrt(5)-1)/2 -- golden ratio
d = 2 * cos(3*pi/10)

def kite(l):
    fl = f * l
    lt(36)
    fd(l)
    rt(108)
    fd(fl)
    rt(36)
    fd(fl)
    rt(108)
    fd(l)
    rt(144)

def dart(l):
    fl = f * l
    lt(36)
    fd(l)
    rt(144)
    fd(fl)
    lt(36)
    fd(fl)
    rt(144)
    fd(l)
    rt(144)

def inflatekite(l, n):
    jeżeli n == 0:
        px, py = pos()
        h, x, y = int(heading()), round(px,3), round(py,3)
        tiledict[(h,x,y)] = Prawda
        zwróć
    fl = f * l
    lt(36)
    inflatedart(fl, n-1)
    fd(l)
    rt(144)
    inflatekite(fl, n-1)
    lt(18)
    fd(l*d)
    rt(162)
    inflatekite(fl, n-1)
    lt(36)
    fd(l)
    rt(180)
    inflatedart(fl, n-1)
    lt(36)

def inflatedart(l, n):
    jeżeli n == 0:
        px, py = pos()
        h, x, y = int(heading()), round(px,3), round(py,3)
        tiledict[(h,x,y)] = Nieprawda
        zwróć
    fl = f * l
    inflatekite(fl, n-1)
    lt(36)
    fd(l)
    rt(180)
    inflatedart(fl, n-1)
    lt(54)
    fd(l*d)
    rt(126)
    inflatedart(fl, n-1)
    fd(l)
    rt(144)

def draw(l, n, th=2):
    clear()
    l = l * f**n
    shapesize(l/100.0, l/100.0, th)
    dla k w tiledict:
        h, x, y = k
        setpos(x, y)
        setheading(h)
        jeżeli tiledict[k]:
            shape("kite")
            color("black", (0, 0.75, 0))
        inaczej:
            shape("dart")
            color("black", (0.75, 0, 0))
        stamp()

def sun(l, n):
    dla i w range(5):
        inflatekite(l, n)
        lt(72)

def star(l,n):
    dla i w range(5):
        inflatedart(l, n)
        lt(72)

def makeshapes():
    tracer(0)
    begin_poly()
    kite(100)
    end_poly()
    register_shape("kite", get_poly())
    begin_poly()
    dart(100)
    end_poly()
    register_shape("dart", get_poly())
    tracer(1)

def start():
    reset()
    ht()
    pu()
    makeshapes()
    resizemode("user")

def test(l=200, n=4, fun=sun, startpos=(0,0), th=2):
    global tiledict
    goto(startpos)
    setheading(0)
    tiledict = {}
    a = clock()
    tracer(0)
    fun(l, n)
    b = clock()
    draw(l, n, th)
    tracer(1)
    c = clock()
    print("Calculation:   %7.4f s" % (b - a))
    print("Drawing:  %7.4f s" % (c - b))
    print("Together: %7.4f s" % (c - a))
    nk = len([x dla x w tiledict jeżeli tiledict[x]])
    nd = len([x dla x w tiledict jeżeli nie tiledict[x]])
    print("%d kites oraz %d darts = %d pieces." % (nk, nd, nk+nd))

def demo(fun=sun):
    start()
    dla i w range(8):
        a = clock()
        test(300, i, fun)
        b = clock()
        t = b - a
        jeżeli t < 2:
            sleep(2 - t)

def main():
    #title("Penrose-tiling przy kites oraz darts.")
    mode("logo")
    bgcolor(0.3, 0.3, 0)
    demo(sun)
    sleep(2)
    demo(star)
    pencolor("black")
    goto(0,-200)
    pencolor(0.7,0.7,1)
    write("Please wait...",
          align="center", font=('Arial Black', 36, 'bold'))
    test(600, 8, startpos=(70, 117))
    zwróć "Done"

jeżeli __name__ == "__main__":
    msg = main()
    mainloop()
