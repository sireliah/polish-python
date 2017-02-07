"""      turtle-example-suite:

            tdemo_nim.py

Play nim against the computer. The player
who takes the last stick jest the winner.

Implements the model-view-controller
design pattern.
"""


zaimportuj turtle
zaimportuj random
zaimportuj time

SCREENWIDTH = 640
SCREENHEIGHT = 480

MINSTICKS = 7
MAXSTICKS = 31

HUNIT = SCREENHEIGHT // 12
WUNIT = SCREENWIDTH // ((MAXSTICKS // 5) * 11 + (MAXSTICKS % 5) * 2)

SCOLOR = (63, 63, 31)
HCOLOR = (255, 204, 204)
COLOR = (204, 204, 255)

def randomrow():
    zwróć random.randint(MINSTICKS, MAXSTICKS)

def computerzug(state):
    xored = state[0] ^ state[1] ^ state[2]
    jeżeli xored == 0:
        zwróć randommove(state)
    dla z w range(3):
        s = state[z] ^ xored
        jeżeli s <= state[z]:
            move = (z, s)
            zwróć move

def randommove(state):
    m = max(state)
    dopóki Prawda:
        z = random.randint(0,2)
        jeżeli state[z] > (m > 1):
            przerwij
    rand = random.randint(m > 1, state[z]-1)
    zwróć z, rand


klasa NimModel(object):
    def __init__(self, game):
        self.game = game

    def setup(self):
        jeżeli self.game.state nie w [Nim.CREATED, Nim.OVER]:
            zwróć
        self.sticks = [randomrow(), randomrow(), randomrow()]
        self.player = 0
        self.winner = Nic
        self.game.view.setup()
        self.game.state = Nim.RUNNING

    def move(self, row, col):
        maxspalte = self.sticks[row]
        self.sticks[row] = col
        self.game.view.notify_move(row, col, maxspalte, self.player)
        jeżeli self.game_over():
            self.game.state = Nim.OVER
            self.winner = self.player
            self.game.view.notify_over()
        albo_inaczej self.player == 0:
            self.player = 1
            row, col = computerzug(self.sticks)
            self.move(row, col)
            self.player = 0

    def game_over(self):
        zwróć self.sticks == [0, 0, 0]

    def notify_move(self, row, col):
        jeżeli self.sticks[row] <= col:
            zwróć
        self.move(row, col)


klasa Stick(turtle.Turtle):
    def __init__(self, row, col, game):
        turtle.Turtle.__init__(self, visible=Nieprawda)
        self.row = row
        self.col = col
        self.game = game
        x, y = self.coords(row, col)
        self.shape("square")
        self.shapesize(HUNIT/10.0, WUNIT/20.0)
        self.speed(0)
        self.pu()
        self.goto(x,y)
        self.color("white")
        self.showturtle()

    def coords(self, row, col):
        packet, remainder = divmod(col, 5)
        x = (3 + 11 * packet + 2 * remainder) * WUNIT
        y = (2 + 3 * row) * HUNIT
        zwróć x - SCREENWIDTH // 2 + WUNIT // 2, SCREENHEIGHT // 2 - y - HUNIT // 2

    def makemove(self, x, y):
        jeżeli self.game.state != Nim.RUNNING:
            zwróć
        self.game.controller.notify_move(self.row, self.col)


klasa NimView(object):
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.mousuń = game.model
        self.screen.colormode(255)
        self.screen.tracer(Nieprawda)
        self.screen.bgcolor((240, 240, 255))
        self.writer = turtle.Turtle(visible=Nieprawda)
        self.writer.pu()
        self.writer.speed(0)
        self.sticks = {}
        dla row w range(3):
            dla col w range(MAXSTICKS):
                self.sticks[(row, col)] = Stick(row, col, game)
        self.display("... a moment please ...")
        self.screen.tracer(Prawda)

    def display(self, msg1, msg2=Nic):
        self.screen.tracer(Nieprawda)
        self.writer.clear()
        jeżeli msg2 jest nie Nic:
            self.writer.goto(0, - SCREENHEIGHT // 2 + 48)
            self.writer.pencolor("red")
            self.writer.write(msg2, align="center", font=("Courier",18,"bold"))
        self.writer.goto(0, - SCREENHEIGHT // 2 + 20)
        self.writer.pencolor("black")
        self.writer.write(msg1, align="center", font=("Courier",14,"bold"))
        self.screen.tracer(Prawda)

    def setup(self):
        self.screen.tracer(Nieprawda)
        dla row w range(3):
            dla col w range(self.model.sticks[row]):
                self.sticks[(row, col)].color(SCOLOR)
        dla row w range(3):
            dla col w range(self.model.sticks[row], MAXSTICKS):
                self.sticks[(row, col)].color("white")
        self.display("Your turn! Click leftmost stick to remove.")
        self.screen.tracer(Prawda)

    def notify_move(self, row, col, maxspalte, player):
        jeżeli player == 0:
            farbe = HCOLOR
            dla s w range(col, maxspalte):
                self.sticks[(row, s)].color(farbe)
        inaczej:
            self.display(" ... thinking ...         ")
            time.sleep(0.5)
            self.display(" ... thinking ... aaah ...")
            farbe = COLOR
            dla s w range(maxspalte-1, col-1, -1):
                time.sleep(0.2)
                self.sticks[(row, s)].color(farbe)
            self.display("Your turn! Click leftmost stick to remove.")

    def notify_over(self):
        jeżeli self.game.model.winner == 0:
            msg2 = "Congrats. You're the winner!!!"
        inaczej:
            msg2 = "Sorry, the computer jest the winner."
        self.display("To play again press space bar. To leave press ESC.", msg2)

    def clear(self):
        jeżeli self.game.state == Nim.OVER:
            self.screen.clear()


klasa NimController(object):

    def __init__(self, game):
        self.game = game
        self.sticks = game.view.sticks
        self.BUSY = Nieprawda
        dla stick w self.sticks.values():
            stick.onclick(stick.makemove)
        self.game.screen.onkey(self.game.model.setup, "space")
        self.game.screen.onkey(self.game.view.clear, "Escape")
        self.game.view.display("Press space bar to start game")
        self.game.screen.listen()

    def notify_move(self, row, col):
        jeżeli self.BUSY:
            zwróć
        self.BUSY = Prawda
        self.game.model.notify_move(row, col)
        self.BUSY = Nieprawda


klasa Nim(object):
    CREATED = 0
    RUNNING = 1
    OVER = 2
    def __init__(self, screen):
        self.state = Nim.CREATED
        self.screen = screen
        self.mousuń = NimModel(self)
        self.view = NimView(self)
        self.controller = NimController(self)


def main():
    mainscreen = turtle.Screen()
    mainscreen.mode("standard")
    mainscreen.setup(SCREENWIDTH, SCREENHEIGHT)
    nim = Nim(mainscreen)
    zwróć "EVENTLOOP"

jeżeli __name__ == "__main__":
    main()
    turtle.mainloop()
