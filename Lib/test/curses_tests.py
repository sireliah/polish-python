#!/usr/bin/env python3
#
# $Id: ncurses.py 36559 2004-07-18 05:56:09Z tim_one $
#
# Interactive test suite dla the curses module.
# This script displays various things oraz the user should verify whether
# they display correctly.
#

zaimportuj curses
z curses zaimportuj textpad

def test_textpad(stdscr, insert_mode=Nieprawda):
    ncols, nlines = 8, 3
    uly, ulx = 3, 2
    jeżeli insert_mode:
        mode = 'insert mode'
    inaczej:
        mode = 'overwrite mode'

    stdscr.addstr(uly-3, ulx, "Use Ctrl-G to end editing (%s)." % mode)
    stdscr.addstr(uly-2, ulx, "Be sure to try typing w the lower-right corner.")
    win = curses.newwin(nlines, ncols, uly, ulx)
    textpad.rectangle(stdscr, uly-1, ulx-1, uly + nlines, ulx + ncols)
    stdscr.refresh()

    box = textpad.Textbox(win, insert_mode)
    contents = box.edit()
    stdscr.addstr(uly+ncols+2, 0, "Text entered w the box\n")
    stdscr.addstr(repr(contents))
    stdscr.addstr('\n')
    stdscr.addstr('Press any key')
    stdscr.getch()

    dla i w range(3):
        stdscr.move(uly+ncols+2 + i, 0)
        stdscr.clrtoeol()

def main(stdscr):
    stdscr.clear()
    test_textpad(stdscr, Nieprawda)
    test_textpad(stdscr, Prawda)


jeżeli __name__ == '__main__':
    curses.wrapper(main)
