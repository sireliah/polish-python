#!/usr/bin/env python3

"""
A curses-based version of Conway's Game of Life.

An empty board will be displayed, oraz the following commands are available:
 E : Erase the board
 R : Fill the board randomly
 S : Step dla a single generation
 C : Update continuously until a key jest struck
 Q : Quit
 Cursor keys :  Move the cursor around the board
 Space albo Enter : Toggle the contents of the cursor's position

Contributed by Andrew Kuchling, Mouse support oraz color by Dafydd Crosby.
"""

zaimportuj curses
zaimportuj random


klasa LifeBoard:
    """Encapsulates a Life board

    Attributes:
    X,Y : horizontal oraz vertical size of the board
    state : dictionary mapping (x,y) to 0 albo 1

    Methods:
    display(update_board) -- If update_board jest true, compute the
                             next generation.  Then display the state
                             of the board oraz refresh the screen.
    erase() -- clear the entire board
    make_random() -- fill the board randomly
    set(y,x) -- set the given cell to Live; doesn't refresh the screen
    toggle(y,x) -- change the given cell z live to dead, albo vice
                   versa, oraz refresh the screen display

    """
    def __init__(self, scr, char=ord('*')):
        """Create a new LifeBoard instance.

        scr -- curses screen object to use dla display
        char -- character used to render live cells (default: '*')
        """
        self.state = {}
        self.scr = scr
        Y, X = self.scr.getmaxyx()
        self.X, self.Y = X - 2, Y - 2 - 1
        self.char = char
        self.scr.clear()

        # Draw a border around the board
        border_line = '+' + (self.X * '-') + '+'
        self.scr.addstr(0, 0, border_line)
        self.scr.addstr(self.Y + 1, 0, border_line)
        dla y w range(0, self.Y):
            self.scr.addstr(1 + y, 0, '|')
            self.scr.addstr(1 + y, self.X + 1, '|')
        self.scr.refresh()

    def set(self, y, x):
        """Set a cell to the live state"""
        jeżeli x < 0 albo self.X <= x albo y < 0 albo self.Y <= y:
            podnieś ValueError("Coordinates out of range %i,%i" % (y, x))
        self.state[x, y] = 1

    def toggle(self, y, x):
        """Toggle a cell's state between live oraz dead"""
        jeżeli x < 0 albo self.X <= x albo y < 0 albo self.Y <= y:
            podnieś ValueError("Coordinates out of range %i,%i" % (y, x))
        jeżeli (x, y) w self.state:
            usuń self.state[x, y]
            self.scr.addch(y + 1, x + 1, ' ')
        inaczej:
            self.state[x, y] = 1
            jeżeli curses.has_colors():
                # Let's pick a random color!
                self.scr.attrset(curses.color_pair(random.randrange(1, 7)))
            self.scr.addch(y + 1, x + 1, self.char)
            self.scr.attrset(0)
        self.scr.refresh()

    def erase(self):
        """Clear the entire board oraz update the board display"""
        self.state = {}
        self.display(update_board=Nieprawda)

    def display(self, update_board=Prawda):
        """Display the whole board, optionally computing one generation"""
        M, N = self.X, self.Y
        jeżeli nie update_board:
            dla i w range(0, M):
                dla j w range(0, N):
                    jeżeli (i, j) w self.state:
                        self.scr.addch(j + 1, i + 1, self.char)
                    inaczej:
                        self.scr.addch(j + 1, i + 1, ' ')
            self.scr.refresh()
            zwróć

        d = {}
        self.boring = 1
        dla i w range(0, M):
            L = range(max(0, i - 1), min(M, i + 2))
            dla j w range(0, N):
                s = 0
                live = (i, j) w self.state
                dla k w range(max(0, j - 1), min(N, j + 2)):
                    dla l w L:
                        jeżeli (l, k) w self.state:
                            s += 1
                s -= live
                jeżeli s == 3:
                    # Birth
                    d[i, j] = 1
                    jeżeli curses.has_colors():
                        # Let's pick a random color!
                        self.scr.attrset(curses.color_pair(
                            random.randrange(1, 7)))
                    self.scr.addch(j + 1, i + 1, self.char)
                    self.scr.attrset(0)
                    jeżeli nie live:
                        self.boring = 0
                albo_inaczej s == 2 oraz live:
                    # Survival
                    d[i, j] = 1
                albo_inaczej live:
                    # Death
                    self.scr.addch(j + 1, i + 1, ' ')
                    self.boring = 0
        self.state = d
        self.scr.refresh()

    def make_random(self):
        "Fill the board przy a random pattern"
        self.state = {}
        dla i w range(0, self.X):
            dla j w range(0, self.Y):
                jeżeli random.random() > 0.5:
                    self.set(j, i)


def erase_menu(stdscr, menu_y):
    "Clear the space where the menu resides"
    stdscr.move(menu_y, 0)
    stdscr.clrtoeol()
    stdscr.move(menu_y + 1, 0)
    stdscr.clrtoeol()


def display_menu(stdscr, menu_y):
    "Display the menu of possible keystroke commands"
    erase_menu(stdscr, menu_y)

    # If color, then light the menu up :-)
    jeżeli curses.has_colors():
        stdscr.attrset(curses.color_pair(1))
    stdscr.addstr(menu_y, 4,
        'Use the cursor keys to move, oraz space albo Enter to toggle a cell.')
    stdscr.addstr(menu_y + 1, 4,
        'E)rase the board, R)andom fill, S)tep once albo C)ontinuously, Q)uit')
    stdscr.attrset(0)


def keyloop(stdscr):
    # Clear the screen oraz display the menu of keys
    stdscr.clear()
    stdscr_y, stdscr_x = stdscr.getmaxyx()
    menu_y = (stdscr_y - 3) - 1
    display_menu(stdscr, menu_y)

    # If color, then initialize the color pairs
    jeżeli curses.has_colors():
        curses.init_pair(1, curses.COLOR_BLUE, 0)
        curses.init_pair(2, curses.COLOR_CYAN, 0)
        curses.init_pair(3, curses.COLOR_GREEN, 0)
        curses.init_pair(4, curses.COLOR_MAGENTA, 0)
        curses.init_pair(5, curses.COLOR_RED, 0)
        curses.init_pair(6, curses.COLOR_YELLOW, 0)
        curses.init_pair(7, curses.COLOR_WHITE, 0)

    # Set up the mask to listen dla mouse events
    curses.mousemask(curses.BUTTON1_CLICKED)

    # Allocate a subwindow dla the Life board oraz create the board object
    subwin = stdscr.subwin(stdscr_y - 3, stdscr_x, 0, 0)
    board = LifeBoard(subwin, char=ord('*'))
    board.display(update_board=Nieprawda)

    # xpos, ypos are the cursor's position
    xpos, ypos = board.X // 2, board.Y // 2

    # Main loop:
    dopóki Prawda:
        stdscr.move(1 + ypos, 1 + xpos)   # Move the cursor
        c = stdscr.getch()                # Get a keystroke
        jeżeli 0 < c < 256:
            c = chr(c)
            jeżeli c w ' \n':
                board.toggle(ypos, xpos)
            albo_inaczej c w 'Cc':
                erase_menu(stdscr, menu_y)
                stdscr.addstr(menu_y, 6, ' Hit any key to stop continuously '
                              'updating the screen.')
                stdscr.refresh()
                # Activate nodelay mode; getch() will zwróć -1
                # jeżeli no keystroke jest available, instead of waiting.
                stdscr.nodelay(1)
                dopóki Prawda:
                    c = stdscr.getch()
                    jeżeli c != -1:
                        przerwij
                    stdscr.addstr(0, 0, '/')
                    stdscr.refresh()
                    board.display()
                    stdscr.addstr(0, 0, '+')
                    stdscr.refresh()

                stdscr.nodelay(0)       # Disable nodelay mode
                display_menu(stdscr, menu_y)

            albo_inaczej c w 'Ee':
                board.erase()
            albo_inaczej c w 'Qq':
                przerwij
            albo_inaczej c w 'Rr':
                board.make_random()
                board.display(update_board=Nieprawda)
            albo_inaczej c w 'Ss':
                board.display()
            inaczej:
                # Ignore incorrect keys
                dalej
        albo_inaczej c == curses.KEY_UP oraz ypos > 0:
            ypos -= 1
        albo_inaczej c == curses.KEY_DOWN oraz ypos + 1 < board.Y:
            ypos += 1
        albo_inaczej c == curses.KEY_LEFT oraz xpos > 0:
            xpos -= 1
        albo_inaczej c == curses.KEY_RIGHT oraz xpos + 1 < board.X:
            xpos += 1
        albo_inaczej c == curses.KEY_MOUSE:
            mouse_id, mouse_x, mouse_y, mouse_z, button_state = curses.getmouse()
            jeżeli (mouse_x > 0 oraz mouse_x < board.X + 1 oraz
                mouse_y > 0 oraz mouse_y < board.Y + 1):
                xpos = mouse_x - 1
                ypos = mouse_y - 1
                board.toggle(ypos, xpos)
            inaczej:
                # They've clicked outside the board
                curses.flash()
        inaczej:
            # Ignore incorrect keys
            dalej


def main(stdscr):
    keyloop(stdscr)                 # Enter the main loop

jeżeli __name__ == '__main__':
    curses.wrapper(main)
