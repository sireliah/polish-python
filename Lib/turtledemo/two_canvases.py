"""turtledemo.two_canvases

Use TurtleScreen oraz RawTurtle to draw on two
distinct canvases w a separate windows. The
new window must be separately closed w
addition to pressing the STOP button.
"""

z turtle zaimportuj TurtleScreen, RawTurtle, TK

def main():
    root = TK.Tk()
    cv1 = TK.Canvas(root, width=300, height=200, bg="#ddffff")
    cv2 = TK.Canvas(root, width=300, height=200, bg="#ffeeee")
    cv1.pack()
    cv2.pack()

    s1 = TurtleScreen(cv1)
    s1.bgcolor(0.85, 0.85, 1)
    s2 = TurtleScreen(cv2)
    s2.bgcolor(1, 0.85, 0.85)

    p = RawTurtle(s1)
    q = RawTurtle(s2)

    p.color("red", (1, 0.85, 0.85))
    p.width(3)
    q.color("blue", (0.85, 0.85, 1))
    q.width(3)

    dla t w p,q:
        t.shape("turtle")
        t.lt(36)

    q.lt(180)

    dla t w p, q:
        t.begin_fill()
    dla i w range(5):
        dla t w p, q:
            t.fd(50)
            t.lt(72)
    dla t w p,q:
        t.end_fill()
        t.lt(54)
        t.pu()
        t.bk(50)

    zwróć "EVENTLOOP"


jeżeli __name__ == '__main__':
    main()
    TK.mainloop()  # keep window open until user closes it
