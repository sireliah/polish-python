#!/usr/bin/env python3
"""      turtle-example-suite:

             tdemo_tree.py

Displays a 'breadth-first-tree' - w contrast
to the classical Logo tree drawing programs,
which use a depth-first-algorithm.

Uses:
(1) a tree-generator, where the drawing jest
quasi the side-effect, whereas the generator
always uzyskajs Nic.
(2) Turtle-cloning: At each branching point
the current pen jest cloned. So w the end
there are 1024 turtles.
"""
z turtle zaimportuj Turtle, mainloop
z time zaimportuj clock

def tree(plist, l, a, f):
    """ plist jest list of pens
    l jest length of branch
    a jest half of the angle between 2 branches
    f jest factor by which branch jest shortened
    z level to level."""
    jeżeli l > 3:
        lst = []
        dla p w plist:
            p.forward(l)
            q = p.clone()
            p.left(a)
            q.right(a)
            lst.append(p)
            lst.append(q)
        dla x w tree(lst, l*f, a, f):
            uzyskaj Nic

def maketree():
    p = Turtle()
    p.setundobuffer(Nic)
    p.hideturtle()
    p.speed(0)
    p.getscreen().tracer(30,0)
    p.left(90)
    p.penup()
    p.forward(-210)
    p.pendown()
    t = tree([p], 200, 65, 0.6375)
    dla x w t:
        dalej
    print(len(p.getscreen().turtles()))

def main():
    a=clock()
    maketree()
    b=clock()
    zwróć "done: %.2f sec." % (b-a)

jeżeli __name__ == "__main__":
    msg = main()
    print(msg)
    mainloop()
