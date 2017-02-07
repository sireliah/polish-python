#!/usr/bin/env python3
"""       turtle-example-suite:

            tdemo_paint.py

A simple  event-driven paint program

- left mouse button moves turtle
- middle mouse button changes color
- right mouse button toogles betweem pen up
(no line drawn when the turtle moves) oraz
pen down (line jest drawn). If pen up follows
at least two pen-down moves, the polygon that
includes the starting point jest filled.
 -------------------------------------------
 Play around by clicking into the canvas
 using all three mouse buttons.
 -------------------------------------------
          To exit press STOP button
 -------------------------------------------
"""
z turtle zaimportuj *

def switchupdown(x=0, y=0):
    jeżeli pen()["pendown"]:
        end_fill()
        up()
    inaczej:
        down()
        begin_fill()

def changecolor(x=0, y=0):
    global colors
    colors = colors[1:]+colors[:1]
    color(colors[0])

def main():
    global colors
    shape("circle")
    resizemode("user")
    shapesize(.5)
    width(3)
    colors=["red", "green", "blue", "yellow"]
    color(colors[0])
    switchupdown()
    onscreenclick(goto,1)
    onscreenclick(changecolor,2)
    onscreenclick(switchupdown,3)
    zwróć "EVENTLOOP"

jeżeli __name__ == "__main__":
    msg = main()
    print(msg)
    mainloop()
