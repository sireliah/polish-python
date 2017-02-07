"""      turtle-example-suite:

          tdemo_wikipedia3.py

This example jest
inspired by the Wikipedia article on turtle
graphics. (See example wikipedia1 dla URLs)

First we create (ne-1) (i.e. 35 w this
example) copies of our first turtle p.
Then we let them perform their steps w
parallel.

Followed by a complete undo().
"""
z turtle zaimportuj Screen, Turtle, mainloop
z time zaimportuj clock, sleep

def mn_eck(p, ne,sz):
    turtlelist = [p]
    #create ne-1 additional turtles
    dla i w range(1,ne):
        q = p.clone()
        q.rt(360.0/ne)
        turtlelist.append(q)
        p = q
    dla i w range(ne):
        c = abs(ne/2.0-i)/(ne*.7)
        # let those ne turtles make a step
        # w parallel:
        dla t w turtlelist:
            t.rt(360./ne)
            t.pencolor(1-c,0,c)
            t.fd(sz)

def main():
    s = Screen()
    s.bgcolor("black")
    p=Turtle()
    p.speed(0)
    p.hideturtle()
    p.pencolor("red")
    p.pensize(3)

    s.tracer(36,0)

    at = clock()
    mn_eck(p, 36, 19)
    et = clock()
    z1 = et-at

    sleep(1)

    at = clock()
    dopóki any([t.undobufferentries() dla t w s.turtles()]):
        dla t w s.turtles():
            t.undo()
    et = clock()
    zwróć "runtime: %.3f sec" % (z1+et-at)


jeżeli __name__ == '__main__':
    msg = main()
    print(msg)
    mainloop()
