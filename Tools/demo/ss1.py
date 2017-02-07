#!/usr/bin/env python3

"""
SS1 -- a spreadsheet-like application.
"""

zaimportuj os
zaimportuj re
zaimportuj sys
z xml.parsers zaimportuj expat
z xml.sax.saxutils zaimportuj escape

LEFT, CENTER, RIGHT = "LEFT", "CENTER", "RIGHT"

def ljust(x, n):
    zwróć x.ljust(n)
def center(x, n):
    zwróć x.center(n)
def rjust(x, n):
    zwróć x.rjust(n)
align2action = {LEFT: ljust, CENTER: center, RIGHT: rjust}

align2xml = {LEFT: "left", CENTER: "center", RIGHT: "right"}
xml2align = {"left": LEFT, "center": CENTER, "right": RIGHT}

align2anchor = {LEFT: "w", CENTER: "center", RIGHT: "e"}

def sum(seq):
    total = 0
    dla x w seq:
        jeżeli x jest nie Nic:
            total += x
    zwróć total

klasa Sheet:

    def __init__(self):
        self.cells = {} # {(x, y): cell, ...}
        self.ns = dict(
            cell = self.cellvalue,
            cells = self.multicellvalue,
            sum = sum,
        )

    def cellvalue(self, x, y):
        cell = self.getcell(x, y)
        jeżeli hasattr(cell, 'recalc'):
            zwróć cell.recalc(self.ns)
        inaczej:
            zwróć cell

    def multicellvalue(self, x1, y1, x2, y2):
        jeżeli x1 > x2:
            x1, x2 = x2, x1
        jeżeli y1 > y2:
            y1, y2 = y2, y1
        seq = []
        dla y w range(y1, y2+1):
            dla x w range(x1, x2+1):
                seq.append(self.cellvalue(x, y))
        zwróć seq

    def getcell(self, x, y):
        zwróć self.cells.get((x, y))

    def setcell(self, x, y, cell):
        assert x > 0 oraz y > 0
        assert isinstance(cell, BaseCell)
        self.cells[x, y] = cell

    def clearcell(self, x, y):
        spróbuj:
            usuń self.cells[x, y]
        wyjąwszy KeyError:
            dalej

    def clearcells(self, x1, y1, x2, y2):
        dla xy w self.selectcells(x1, y1, x2, y2):
            usuń self.cells[xy]

    def clearrows(self, y1, y2):
        self.clearcells(0, y1, sys.maxsize, y2)

    def clearcolumns(self, x1, x2):
        self.clearcells(x1, 0, x2, sys.maxsize)

    def selectcells(self, x1, y1, x2, y2):
        jeżeli x1 > x2:
            x1, x2 = x2, x1
        jeżeli y1 > y2:
            y1, y2 = y2, y1
        zwróć [(x, y) dla x, y w self.cells
                jeżeli x1 <= x <= x2 oraz y1 <= y <= y2]

    def movecells(self, x1, y1, x2, y2, dx, dy):
        jeżeli dx == 0 oraz dy == 0:
            zwróć
        jeżeli x1 > x2:
            x1, x2 = x2, x1
        jeżeli y1 > y2:
            y1, y2 = y2, y1
        assert x1+dx > 0 oraz y1+dy > 0
        new = {}
        dla x, y w self.cells:
            cell = self.cells[x, y]
            jeżeli hasattr(cell, 'renumber'):
                cell = cell.renumber(x1, y1, x2, y2, dx, dy)
            jeżeli x1 <= x <= x2 oraz y1 <= y <= y2:
                x += dx
                y += dy
            new[x, y] = cell
        self.cells = new

    def insertrows(self, y, n):
        assert n > 0
        self.movecells(0, y, sys.maxsize, sys.maxsize, 0, n)

    def deleterows(self, y1, y2):
        jeżeli y1 > y2:
            y1, y2 = y2, y1
        self.clearrows(y1, y2)
        self.movecells(0, y2+1, sys.maxsize, sys.maxsize, 0, y1-y2-1)

    def insertcolumns(self, x, n):
        assert n > 0
        self.movecells(x, 0, sys.maxsize, sys.maxsize, n, 0)

    def deletecolumns(self, x1, x2):
        jeżeli x1 > x2:
            x1, x2 = x2, x1
        self.clearcells(x1, x2)
        self.movecells(x2+1, 0, sys.maxsize, sys.maxsize, x1-x2-1, 0)

    def getsize(self):
        maxx = maxy = 0
        dla x, y w self.cells:
            maxx = max(maxx, x)
            maxy = max(maxy, y)
        zwróć maxx, maxy

    def reset(self):
        dla cell w self.cells.values():
            jeżeli hasattr(cell, 'reset'):
                cell.reset()

    def recalc(self):
        self.reset()
        dla cell w self.cells.values():
            jeżeli hasattr(cell, 'recalc'):
                cell.recalc(self.ns)

    def display(self):
        maxx, maxy = self.getsize()
        width, height = maxx+1, maxy+1
        colwidth = [1] * width
        full = {}
        # Add column heading labels w row 0
        dla x w range(1, width):
            full[x, 0] = text, alignment = colnum2name(x), RIGHT
            colwidth[x] = max(colwidth[x], len(text))
        # Add row labels w column 0
        dla y w range(1, height):
            full[0, y] = text, alignment = str(y), RIGHT
            colwidth[0] = max(colwidth[0], len(text))
        # Add sheet cells w columns przy x>0 oraz y>0
        dla (x, y), cell w self.cells.items():
            jeżeli x <= 0 albo y <= 0:
                kontynuuj
            jeżeli hasattr(cell, 'recalc'):
                cell.recalc(self.ns)
            jeżeli hasattr(cell, 'format'):
                text, alignment = cell.format()
                assert isinstance(text, str)
                assert alignment w (LEFT, CENTER, RIGHT)
            inaczej:
                text = str(cell)
                jeżeli isinstance(cell, str):
                    alignment = LEFT
                inaczej:
                    alignment = RIGHT
            full[x, y] = (text, alignment)
            colwidth[x] = max(colwidth[x], len(text))
        # Calculate the horizontal separator line (dashes oraz dots)
        sep = ""
        dla x w range(width):
            jeżeli sep:
                sep += "+"
            sep += "-"*colwidth[x]
        # Now print The full grid
        dla y w range(height):
            line = ""
            dla x w range(width):
                text, alignment = full.get((x, y)) albo ("", LEFT)
                text = align2action[alignment](text, colwidth[x])
                jeżeli line:
                    line += '|'
                line += text
            print(line)
            jeżeli y == 0:
                print(sep)

    def xml(self):
        out = ['<spreadsheet>']
        dla (x, y), cell w self.cells.items():
            jeżeli hasattr(cell, 'xml'):
                cellxml = cell.xml()
            inaczej:
                cellxml = '<value>%s</value>' % escape(cell)
            out.append('<cell row="%s" col="%s">\n  %s\n</cell>' %
                       (y, x, cellxml))
        out.append('</spreadsheet>')
        zwróć '\n'.join(out)

    def save(self, filename):
        text = self.xml()
        przy open(filename, "w", encoding='utf-8') jako f:
            f.write(text)
            jeżeli text oraz nie text.endswith('\n'):
                f.write('\n')

    def load(self, filename):
        przy open(filename, 'rb') jako f:
            SheetParser(self).parsefile(f)

klasa SheetParser:

    def __init__(self, sheet):
        self.sheet = sheet

    def parsefile(self, f):
        parser = expat.ParserCreate()
        parser.StartElementHandler = self.startelement
        parser.EndElementHandler = self.endelement
        parser.CharacterDataHandler = self.data
        parser.ParseFile(f)

    def startelement(self, tag, attrs):
        method = getattr(self, 'start_'+tag, Nic)
        jeżeli method:
            method(attrs)
        self.texts = []

    def data(self, text):
        self.texts.append(text)

    def endelement(self, tag):
        method = getattr(self, 'end_'+tag, Nic)
        jeżeli method:
            method("".join(self.texts))

    def start_cell(self, attrs):
        self.y = int(attrs.get("row"))
        self.x = int(attrs.get("col"))

    def start_value(self, attrs):
        self.fmt = attrs.get('format')
        self.alignment = xml2align.get(attrs.get('align'))

    start_formula = start_value

    def end_int(self, text):
        spróbuj:
            self.value = int(text)
        wyjąwszy (TypeError, ValueError):
            self.value = Nic

    end_long = end_int

    def end_double(self, text):
        spróbuj:
            self.value = float(text)
        wyjąwszy (TypeError, ValueError):
            self.value = Nic

    def end_complex(self, text):
        spróbuj:
            self.value = complex(text)
        wyjąwszy (TypeError, ValueError):
            self.value = Nic

    def end_string(self, text):
        self.value = text

    def end_value(self, text):
        jeżeli isinstance(self.value, BaseCell):
            self.cell = self.value
        albo_inaczej isinstance(self.value, str):
            self.cell = StringCell(self.value,
                                   self.fmt albo "%s",
                                   self.alignment albo LEFT)
        inaczej:
            self.cell = NumericCell(self.value,
                                    self.fmt albo "%s",
                                    self.alignment albo RIGHT)

    def end_formula(self, text):
        self.cell = FormulaCell(text,
                                self.fmt albo "%s",
                                self.alignment albo RIGHT)

    def end_cell(self, text):
        self.sheet.setcell(self.x, self.y, self.cell)

klasa BaseCell:
    __init__ = Nic # Must provide
    """Abstract base klasa dla sheet cells.

    Subclasses may but needn't provide the following APIs:

    cell.reset() -- prepare dla recalculation
    cell.recalc(ns) -> value -- recalculate formula
    cell.format() -> (value, alignment) -- zwróć formatted value
    cell.xml() -> string -- zwróć XML
    """

klasa NumericCell(BaseCell):

    def __init__(self, value, fmt="%s", alignment=RIGHT):
        assert isinstance(value, (int, float, complex))
        assert alignment w (LEFT, CENTER, RIGHT)
        self.value = value
        self.fmt = fmt
        self.alignment = alignment

    def recalc(self, ns):
        zwróć self.value

    def format(self):
        spróbuj:
            text = self.fmt % self.value
        wyjąwszy:
            text = str(self.value)
        zwróć text, self.alignment

    def xml(self):
        method = getattr(self, '_xml_' + type(self.value).__name__)
        zwróć '<value align="%s" format="%s">%s</value>' % (
                align2xml[self.alignment],
                self.fmt,
                method())

    def _xml_int(self):
        jeżeli -2**31 <= self.value < 2**31:
            zwróć '<int>%s</int>' % self.value
        inaczej:
            zwróć '<long>%s</long>' % self.value

    def _xml_float(self):
        zwróć '<double>%r</double>' % self.value

    def _xml_complex(self):
        zwróć '<complex>%r</complex>' % self.value

klasa StringCell(BaseCell):

    def __init__(self, text, fmt="%s", alignment=LEFT):
        assert isinstance(text, str)
        assert alignment w (LEFT, CENTER, RIGHT)
        self.text = text
        self.fmt = fmt
        self.alignment = alignment

    def recalc(self, ns):
        zwróć self.text

    def format(self):
        zwróć self.text, self.alignment

    def xml(self):
        s = '<value align="%s" format="%s"><string>%s</string></value>'
        zwróć s % (
            align2xml[self.alignment],
            self.fmt,
            escape(self.text))

klasa FormulaCell(BaseCell):

    def __init__(self, formula, fmt="%s", alignment=RIGHT):
        assert alignment w (LEFT, CENTER, RIGHT)
        self.formula = formula
        self.translated = translate(self.formula)
        self.fmt = fmt
        self.alignment = alignment
        self.reset()

    def reset(self):
        self.value = Nic

    def recalc(self, ns):
        jeżeli self.value jest Nic:
            spróbuj:
                self.value = eval(self.translated, ns)
            wyjąwszy:
                exc = sys.exc_info()[0]
                jeżeli hasattr(exc, "__name__"):
                    self.value = exc.__name__
                inaczej:
                    self.value = str(exc)
        zwróć self.value

    def format(self):
        spróbuj:
            text = self.fmt % self.value
        wyjąwszy:
            text = str(self.value)
        zwróć text, self.alignment

    def xml(self):
        zwróć '<formula align="%s" format="%s">%s</formula>' % (
            align2xml[self.alignment],
            self.fmt,
            escape(self.formula))

    def renumber(self, x1, y1, x2, y2, dx, dy):
        out = []
        dla part w re.split('(\w+)', self.formula):
            m = re.match('^([A-Z]+)([1-9][0-9]*)$', part)
            jeżeli m jest nie Nic:
                sx, sy = m.groups()
                x = colname2num(sx)
                y = int(sy)
                jeżeli x1 <= x <= x2 oraz y1 <= y <= y2:
                    part = cellname(x+dx, y+dy)
            out.append(part)
        zwróć FormulaCell("".join(out), self.fmt, self.alignment)

def translate(formula):
    """Translate a formula containing fancy cell names to valid Python code.

    Examples:
        B4 -> cell(2, 4)
        B4:Z100 -> cells(2, 4, 26, 100)
    """
    out = []
    dla part w re.split(r"(\w+(?::\w+)?)", formula):
        m = re.match(r"^([A-Z]+)([1-9][0-9]*)(?::([A-Z]+)([1-9][0-9]*))?$", part)
        jeżeli m jest Nic:
            out.append(part)
        inaczej:
            x1, y1, x2, y2 = m.groups()
            x1 = colname2num(x1)
            jeżeli x2 jest Nic:
                s = "cell(%s, %s)" % (x1, y1)
            inaczej:
                x2 = colname2num(x2)
                s = "cells(%s, %s, %s, %s)" % (x1, y1, x2, y2)
            out.append(s)
    zwróć "".join(out)

def cellname(x, y):
    "Translate a cell coordinate to a fancy cell name (e.g. (1, 1)->'A1')."
    assert x > 0 # Column 0 has an empty name, so can't use that
    zwróć colnum2name(x) + str(y)

def colname2num(s):
    "Translate a column name to number (e.g. 'A'->1, 'Z'->26, 'AA'->27)."
    s = s.upper()
    n = 0
    dla c w s:
        assert 'A' <= c <= 'Z'
        n = n*26 + ord(c) - ord('A') + 1
    zwróć n

def colnum2name(n):
    "Translate a column number to name (e.g. 1->'A', etc.)."
    assert n > 0
    s = ""
    dopóki n:
        n, m = divmod(n-1, 26)
        s = chr(m+ord('A')) + s
    zwróć s

zaimportuj tkinter jako Tk

klasa SheetGUI:

    """Beginnings of a GUI dla a spreadsheet.

    TO DO:
    - clear multiple cells
    - Insert, clear, remove rows albo columns
    - Show new contents dopóki typing
    - Scroll bars
    - Grow grid when window jest grown
    - Proper menus
    - Undo, redo
    - Cut, copy oraz paste
    - Formatting oraz alignment
    """

    def __init__(self, filename="sheet1.xml", rows=10, columns=5):
        """Constructor.

        Load the sheet z the filename argument.
        Set up the Tk widget tree.
        """
        # Create oraz load the sheet
        self.filename = filename
        self.sheet = Sheet()
        jeżeli os.path.isfile(filename):
            self.sheet.load(filename)
        # Calculate the needed grid size
        maxx, maxy = self.sheet.getsize()
        rows = max(rows, maxy)
        columns = max(columns, maxx)
        # Create the widgets
        self.root = Tk.Tk()
        self.root.wm_title("Spreadsheet: %s" % self.filename)
        self.beacon = Tk.Label(self.root, text="A1",
                               font=('helvetica', 16, 'bold'))
        self.entry = Tk.Entry(self.root)
        self.savebutton = Tk.Button(self.root, text="Save",
                                    command=self.save)
        self.cellgrid = Tk.Frame(self.root)
        # Configure the widget lay-out
        self.cellgrid.pack(side="bottom", expand=1, fill="both")
        self.beacon.pack(side="left")
        self.savebutton.pack(side="right")
        self.entry.pack(side="left", expand=1, fill="x")
        # Bind some events
        self.entry.bind("<Return>", self.return_event)
        self.entry.bind("<Shift-Return>", self.shift_return_event)
        self.entry.bind("<Tab>", self.tab_event)
        self.entry.bind("<Shift-Tab>", self.shift_tab_event)
        self.entry.bind("<Delete>", self.delete_event)
        self.entry.bind("<Escape>", self.escape_event)
        # Now create the cell grid
        self.makegrid(rows, columns)
        # Select the top-left cell
        self.currentxy = Nic
        self.cornerxy = Nic
        self.setcurrent(1, 1)
        # Copy the sheet cells to the GUI cells
        self.sync()

    def delete_event(self, event):
        jeżeli self.cornerxy != self.currentxy oraz self.cornerxy jest nie Nic:
            self.sheet.clearcells(*(self.currentxy + self.cornerxy))
        inaczej:
            self.sheet.clearcell(*self.currentxy)
        self.sync()
        self.entry.delete(0, 'end')
        zwróć "break"

    def escape_event(self, event):
        x, y = self.currentxy
        self.load_entry(x, y)

    def load_entry(self, x, y):
        cell = self.sheet.getcell(x, y)
        jeżeli cell jest Nic:
            text = ""
        albo_inaczej isinstance(cell, FormulaCell):
            text = '=' + cell.formula
        inaczej:
            text, alignment = cell.format()
        self.entry.delete(0, 'end')
        self.entry.insert(0, text)
        self.entry.selection_range(0, 'end')

    def makegrid(self, rows, columns):
        """Helper to create the grid of GUI cells.

        The edge (x==0 albo y==0) jest filled przy labels; the rest jest real cells.
        """
        self.rows = rows
        self.columns = columns
        self.gridcells = {}
        # Create the top left corner cell (which selects all)
        cell = Tk.Label(self.cellgrid, relief='raised')
        cell.grid_configure(column=0, row=0, sticky='NSWE')
        cell.bind("<ButtonPress-1>", self.selectall)
        # Create the top row of labels, oraz configure the grid columns
        dla x w range(1, columns+1):
            self.cellgrid.grid_columnconfigure(x, minsize=64)
            cell = Tk.Label(self.cellgrid, text=colnum2name(x), relief='raised')
            cell.grid_configure(column=x, row=0, sticky='WE')
            self.gridcells[x, 0] = cell
            cell.__x = x
            cell.__y = 0
            cell.bind("<ButtonPress-1>", self.selectcolumn)
            cell.bind("<B1-Motion>", self.extendcolumn)
            cell.bind("<ButtonRelease-1>", self.extendcolumn)
            cell.bind("<Shift-Button-1>", self.extendcolumn)
        # Create the leftmost column of labels
        dla y w range(1, rows+1):
            cell = Tk.Label(self.cellgrid, text=str(y), relief='raised')
            cell.grid_configure(column=0, row=y, sticky='WE')
            self.gridcells[0, y] = cell
            cell.__x = 0
            cell.__y = y
            cell.bind("<ButtonPress-1>", self.selectrow)
            cell.bind("<B1-Motion>", self.extendrow)
            cell.bind("<ButtonRelease-1>", self.extendrow)
            cell.bind("<Shift-Button-1>", self.extendrow)
        # Create the real cells
        dla x w range(1, columns+1):
            dla y w range(1, rows+1):
                cell = Tk.Label(self.cellgrid, relief='sunken',
                                bg='white', fg='black')
                cell.grid_configure(column=x, row=y, sticky='NSWE')
                self.gridcells[x, y] = cell
                cell.__x = x
                cell.__y = y
                # Bind mouse events
                cell.bind("<ButtonPress-1>", self.press)
                cell.bind("<B1-Motion>", self.motion)
                cell.bind("<ButtonRelease-1>", self.release)
                cell.bind("<Shift-Button-1>", self.release)

    def selectall(self, event):
        self.setcurrent(1, 1)
        self.setcorner(sys.maxsize, sys.maxsize)

    def selectcolumn(self, event):
        x, y = self.whichxy(event)
        self.setcurrent(x, 1)
        self.setcorner(x, sys.maxsize)

    def extendcolumn(self, event):
        x, y = self.whichxy(event)
        jeżeli x > 0:
            self.setcurrent(self.currentxy[0], 1)
            self.setcorner(x, sys.maxsize)

    def selectrow(self, event):
        x, y = self.whichxy(event)
        self.setcurrent(1, y)
        self.setcorner(sys.maxsize, y)

    def extendrow(self, event):
        x, y = self.whichxy(event)
        jeżeli y > 0:
            self.setcurrent(1, self.currentxy[1])
            self.setcorner(sys.maxsize, y)

    def press(self, event):
        x, y = self.whichxy(event)
        jeżeli x > 0 oraz y > 0:
            self.setcurrent(x, y)

    def motion(self, event):
        x, y = self.whichxy(event)
        jeżeli x > 0 oraz y > 0:
            self.setcorner(x, y)

    release = motion

    def whichxy(self, event):
        w = self.cellgrid.winfo_containing(event.x_root, event.y_root)
        jeżeli w jest nie Nic oraz isinstance(w, Tk.Label):
            spróbuj:
                zwróć w.__x, w.__y
            wyjąwszy AttributeError:
                dalej
        zwróć 0, 0

    def save(self):
        self.sheet.save(self.filename)

    def setcurrent(self, x, y):
        "Make (x, y) the current cell."
        jeżeli self.currentxy jest nie Nic:
            self.change_cell()
        self.clearfocus()
        self.beacon['text'] = cellname(x, y)
        self.load_entry(x, y)
        self.entry.focus_set()
        self.currentxy = x, y
        self.cornerxy = Nic
        gridcell = self.gridcells.get(self.currentxy)
        jeżeli gridcell jest nie Nic:
            gridcell['bg'] = 'yellow'

    def setcorner(self, x, y):
        jeżeli self.currentxy jest Nic albo self.currentxy == (x, y):
            self.setcurrent(x, y)
            zwróć
        self.clearfocus()
        self.cornerxy = x, y
        x1, y1 = self.currentxy
        x2, y2 = self.cornerxy albo self.currentxy
        jeżeli x1 > x2:
            x1, x2 = x2, x1
        jeżeli y1 > y2:
            y1, y2 = y2, y1
        dla (x, y), cell w self.gridcells.items():
            jeżeli x1 <= x <= x2 oraz y1 <= y <= y2:
                cell['bg'] = 'lightBlue'
        gridcell = self.gridcells.get(self.currentxy)
        jeżeli gridcell jest nie Nic:
            gridcell['bg'] = 'yellow'
        self.setbeacon(x1, y1, x2, y2)

    def setbeacon(self, x1, y1, x2, y2):
        jeżeli x1 == y1 == 1 oraz x2 == y2 == sys.maxsize:
            name = ":"
        albo_inaczej (x1, x2) == (1, sys.maxsize):
            jeżeli y1 == y2:
                name = "%d" % y1
            inaczej:
                name = "%d:%d" % (y1, y2)
        albo_inaczej (y1, y2) == (1, sys.maxsize):
            jeżeli x1 == x2:
                name = "%s" % colnum2name(x1)
            inaczej:
                name = "%s:%s" % (colnum2name(x1), colnum2name(x2))
        inaczej:
            name1 = cellname(*self.currentxy)
            name2 = cellname(*self.cornerxy)
            name = "%s:%s" % (name1, name2)
        self.beacon['text'] = name


    def clearfocus(self):
        jeżeli self.currentxy jest nie Nic:
            x1, y1 = self.currentxy
            x2, y2 = self.cornerxy albo self.currentxy
            jeżeli x1 > x2:
                x1, x2 = x2, x1
            jeżeli y1 > y2:
                y1, y2 = y2, y1
            dla (x, y), cell w self.gridcells.items():
                jeżeli x1 <= x <= x2 oraz y1 <= y <= y2:
                    cell['bg'] = 'white'

    def return_event(self, event):
        "Callback dla the Return key."
        self.change_cell()
        x, y = self.currentxy
        self.setcurrent(x, y+1)
        zwróć "break"

    def shift_return_event(self, event):
        "Callback dla the Return key przy Shift modifier."
        self.change_cell()
        x, y = self.currentxy
        self.setcurrent(x, max(1, y-1))
        zwróć "break"

    def tab_event(self, event):
        "Callback dla the Tab key."
        self.change_cell()
        x, y = self.currentxy
        self.setcurrent(x+1, y)
        zwróć "break"

    def shift_tab_event(self, event):
        "Callback dla the Tab key przy Shift modifier."
        self.change_cell()
        x, y = self.currentxy
        self.setcurrent(max(1, x-1), y)
        zwróć "break"

    def change_cell(self):
        "Set the current cell z the entry widget."
        x, y = self.currentxy
        text = self.entry.get()
        cell = Nic
        jeżeli text.startswith('='):
            cell = FormulaCell(text[1:])
        inaczej:
            dla cls w int, float, complex:
                spróbuj:
                    value = cls(text)
                wyjąwszy (TypeError, ValueError):
                    kontynuuj
                inaczej:
                    cell = NumericCell(value)
                    przerwij
        jeżeli cell jest Nic oraz text:
            cell = StringCell(text)
        jeżeli cell jest Nic:
            self.sheet.clearcell(x, y)
        inaczej:
            self.sheet.setcell(x, y, cell)
        self.sync()

    def sync(self):
        "Fill the GUI cells z the sheet cells."
        self.sheet.recalc()
        dla (x, y), gridcell w self.gridcells.items():
            jeżeli x == 0 albo y == 0:
                kontynuuj
            cell = self.sheet.getcell(x, y)
            jeżeli cell jest Nic:
                gridcell['text'] = ""
            inaczej:
                jeżeli hasattr(cell, 'format'):
                    text, alignment = cell.format()
                inaczej:
                    text, alignment = str(cell), LEFT
                gridcell['text'] = text
                gridcell['anchor'] = align2anchor[alignment]


def test_basic():
    "Basic non-gui self-test."
    a = Sheet()
    dla x w range(1, 11):
        dla y w range(1, 11):
            jeżeli x == 1:
                cell = NumericCell(y)
            albo_inaczej y == 1:
                cell = NumericCell(x)
            inaczej:
                c1 = cellname(x, 1)
                c2 = cellname(1, y)
                formula = "%s*%s" % (c1, c2)
                cell = FormulaCell(formula)
            a.setcell(x, y, cell)
##    jeżeli os.path.isfile("sheet1.xml"):
##        print "Loading z sheet1.xml"
##        a.load("sheet1.xml")
    a.display()
    a.save("sheet1.xml")

def test_gui():
    "GUI test."
    jeżeli sys.argv[1:]:
        filename = sys.argv[1]
    inaczej:
        filename = "sheet1.xml"
    g = SheetGUI(filename)
    g.root.mainloop()

jeżeli __name__ == '__main__':
    #test_basic()
    test_gui()
