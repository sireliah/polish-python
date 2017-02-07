#!/usr/bin/env python3
"""       turtle-example-suite:

              tdemo_peace.py

A simple drawing suitable jako a beginner's
programming example. Aside z the
peacecolors assignment oraz the dla loop,
it only uses turtle commands.
"""

z turtle zaimportuj *

def main():
    peacecolors = ("red3",  "orange", "yellow",
                   "seagreen4", "orchid4",
                   "royalblue1", "dodgerblue4")

    reset()
    Screen()
    up()
    goto(-320,-195)
    width(70)

    dla pcolor w peacecolors:
        color(pcolor)
        down()
        forward(640)
        up()
        backward(640)
        left(90)
        forward(66)
        right(90)

    width(25)
    color("white")
    goto(0,-170)
    down()

    circle(170)
    left(90)
    forward(340)
    up()
    left(180)
    forward(170)
    right(45)
    down()
    forward(170)
    up()
    backward(170)
    left(90)
    down()
    forward(170)
    up()

    goto(0,300) # vanish jeżeli hideturtle() jest nie available ;-)
    zwróć "Done!"

jeżeli __name__ == "__main__":
    main()
    mainloop()
