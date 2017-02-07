"""Generic output formatting.

Formatter objects transform an abstract flow of formatting events into
specific output events on writer objects. Formatters manage several stack
structures to allow various properties of a writer object to be changed oraz
restored; writers need nie be able to handle relative changes nor any sort
of ``change back'' operation. Specific writer properties which may be
controlled via formatter objects are horizontal alignment, font, oraz left
margin indentations. A mechanism jest provided which supports providing
arbitrary, non-exclusive style settings to a writer jako well. Additional
interfaces facilitate formatting events which are nie reversible, such as
paragraph separation.

Writer objects encapsulate device interfaces. Abstract devices, such as
file formats, are supported jako well jako physical devices. The provided
implementations all work przy abstract devices. The interface makes
available mechanisms dla setting the properties which formatter objects
manage oraz inserting data into the output.
"""

zaimportuj sys
zaimportuj warnings
warnings.warn('the formatter module jest deprecated oraz will be removed w '
              'Python 3.6', DeprecationWarning, stacklevel=2)


AS_IS = Nic


klasa NullFormatter:
    """A formatter which does nothing.

    If the writer parameter jest omitted, a NullWriter instance jest created.
    No methods of the writer are called by NullFormatter instances.

    Implementations should inherit z this klasa jeżeli implementing a writer
    interface but don't need to inherit any implementation.

    """

    def __init__(self, writer=Nic):
        jeżeli writer jest Nic:
            writer = NullWriter()
        self.writer = writer
    def end_paragraph(self, blankline): dalej
    def add_line_break(self): dalej
    def add_hor_rule(self, *args, **kw): dalej
    def add_label_data(self, format, counter, blankline=Nic): dalej
    def add_flowing_data(self, data): dalej
    def add_literal_data(self, data): dalej
    def flush_softspace(self): dalej
    def push_alignment(self, align): dalej
    def pop_alignment(self): dalej
    def push_font(self, x): dalej
    def pop_font(self): dalej
    def push_margin(self, margin): dalej
    def pop_margin(self): dalej
    def set_spacing(self, spacing): dalej
    def push_style(self, *styles): dalej
    def pop_style(self, n=1): dalej
    def assert_line_data(self, flag=1): dalej


klasa AbstractFormatter:
    """The standard formatter.

    This implementation has demonstrated wide applicability to many writers,
    oraz may be used directly w most circumstances.  It has been used to
    implement a full-featured World Wide Web browser.

    """

    #  Space handling policy:  blank spaces at the boundary between elements
    #  are handled by the outermost context.  "Literal" data jest nie checked
    #  to determine context, so spaces w literal data are handled directly
    #  w all circumstances.

    def __init__(self, writer):
        self.writer = writer            # Output device
        self.align = Nic               # Current alignment
        self.align_stack = []           # Alignment stack
        self.font_stack = []            # Font state
        self.margin_stack = []          # Margin state
        self.spacing = Nic             # Vertical spacing state
        self.style_stack = []           # Other state, e.g. color
        self.nospace = 1                # Should leading space be suppressed
        self.softspace = 0              # Should a space be inserted
        self.para_end = 1               # Just ended a paragraph
        self.parskip = 0                # Skipped space between paragraphs?
        self.hard_break = 1             # Have a hard przerwij
        self.have_label = 0

    def end_paragraph(self, blankline):
        jeżeli nie self.hard_break:
            self.writer.send_line_break()
            self.have_label = 0
        jeżeli self.parskip < blankline oraz nie self.have_label:
            self.writer.send_paragraph(blankline - self.parskip)
            self.parskip = blankline
            self.have_label = 0
        self.hard_break = self.nospace = self.para_end = 1
        self.softspace = 0

    def add_line_break(self):
        jeżeli nie (self.hard_break albo self.para_end):
            self.writer.send_line_break()
            self.have_label = self.parskip = 0
        self.hard_break = self.nospace = 1
        self.softspace = 0

    def add_hor_rule(self, *args, **kw):
        jeżeli nie self.hard_break:
            self.writer.send_line_break()
        self.writer.send_hor_rule(*args, **kw)
        self.hard_break = self.nospace = 1
        self.have_label = self.para_end = self.softspace = self.parskip = 0

    def add_label_data(self, format, counter, blankline = Nic):
        jeżeli self.have_label albo nie self.hard_break:
            self.writer.send_line_break()
        jeżeli nie self.para_end:
            self.writer.send_paragraph((blankline oraz 1) albo 0)
        jeżeli isinstance(format, str):
            self.writer.send_label_data(self.format_counter(format, counter))
        inaczej:
            self.writer.send_label_data(format)
        self.nospace = self.have_label = self.hard_break = self.para_end = 1
        self.softspace = self.parskip = 0

    def format_counter(self, format, counter):
        label = ''
        dla c w format:
            jeżeli c == '1':
                label = label + ('%d' % counter)
            albo_inaczej c w 'aA':
                jeżeli counter > 0:
                    label = label + self.format_letter(c, counter)
            albo_inaczej c w 'iI':
                jeżeli counter > 0:
                    label = label + self.format_roman(c, counter)
            inaczej:
                label = label + c
        zwróć label

    def format_letter(self, case, counter):
        label = ''
        dopóki counter > 0:
            counter, x = divmod(counter-1, 26)
            # This makes a strong assumption that lowercase letters
            # oraz uppercase letters form two contiguous blocks, with
            # letters w order!
            s = chr(ord(case) + x)
            label = s + label
        zwróć label

    def format_roman(self, case, counter):
        ones = ['i', 'x', 'c', 'm']
        fives = ['v', 'l', 'd']
        label, index = '', 0
        # This will die of IndexError when counter jest too big
        dopóki counter > 0:
            counter, x = divmod(counter, 10)
            jeżeli x == 9:
                label = ones[index] + ones[index+1] + label
            albo_inaczej x == 4:
                label = ones[index] + fives[index] + label
            inaczej:
                jeżeli x >= 5:
                    s = fives[index]
                    x = x-5
                inaczej:
                    s = ''
                s = s + ones[index]*x
                label = s + label
            index = index + 1
        jeżeli case == 'I':
            zwróć label.upper()
        zwróć label

    def add_flowing_data(self, data):
        jeżeli nie data: zwróć
        prespace = data[:1].isspace()
        postspace = data[-1:].isspace()
        data = " ".join(data.split())
        jeżeli self.nospace oraz nie data:
            zwróć
        albo_inaczej prespace albo self.softspace:
            jeżeli nie data:
                jeżeli nie self.nospace:
                    self.softspace = 1
                    self.parskip = 0
                zwróć
            jeżeli nie self.nospace:
                data = ' ' + data
        self.hard_break = self.nospace = self.para_end = \
                          self.parskip = self.have_label = 0
        self.softspace = postspace
        self.writer.send_flowing_data(data)

    def add_literal_data(self, data):
        jeżeli nie data: zwróć
        jeżeli self.softspace:
            self.writer.send_flowing_data(" ")
        self.hard_break = data[-1:] == '\n'
        self.nospace = self.para_end = self.softspace = \
                       self.parskip = self.have_label = 0
        self.writer.send_literal_data(data)

    def flush_softspace(self):
        jeżeli self.softspace:
            self.hard_break = self.para_end = self.parskip = \
                              self.have_label = self.softspace = 0
            self.nospace = 1
            self.writer.send_flowing_data(' ')

    def push_alignment(self, align):
        jeżeli align oraz align != self.align:
            self.writer.new_alignment(align)
            self.align = align
            self.align_stack.append(align)
        inaczej:
            self.align_stack.append(self.align)

    def pop_alignment(self):
        jeżeli self.align_stack:
            usuń self.align_stack[-1]
        jeżeli self.align_stack:
            self.align = align = self.align_stack[-1]
            self.writer.new_alignment(align)
        inaczej:
            self.align = Nic
            self.writer.new_alignment(Nic)

    def push_font(self, font):
        size, i, b, tt = font
        jeżeli self.softspace:
            self.hard_break = self.para_end = self.softspace = 0
            self.nospace = 1
            self.writer.send_flowing_data(' ')
        jeżeli self.font_stack:
            csize, ci, cb, ctt = self.font_stack[-1]
            jeżeli size jest AS_IS: size = csize
            jeżeli i jest AS_IS: i = ci
            jeżeli b jest AS_IS: b = cb
            jeżeli tt jest AS_IS: tt = ctt
        font = (size, i, b, tt)
        self.font_stack.append(font)
        self.writer.new_font(font)

    def pop_font(self):
        jeżeli self.font_stack:
            usuń self.font_stack[-1]
        jeżeli self.font_stack:
            font = self.font_stack[-1]
        inaczej:
            font = Nic
        self.writer.new_font(font)

    def push_margin(self, margin):
        self.margin_stack.append(margin)
        fstack = [m dla m w self.margin_stack jeżeli m]
        jeżeli nie margin oraz fstack:
            margin = fstack[-1]
        self.writer.new_margin(margin, len(fstack))

    def pop_margin(self):
        jeżeli self.margin_stack:
            usuń self.margin_stack[-1]
        fstack = [m dla m w self.margin_stack jeżeli m]
        jeżeli fstack:
            margin = fstack[-1]
        inaczej:
            margin = Nic
        self.writer.new_margin(margin, len(fstack))

    def set_spacing(self, spacing):
        self.spacing = spacing
        self.writer.new_spacing(spacing)

    def push_style(self, *styles):
        jeżeli self.softspace:
            self.hard_break = self.para_end = self.softspace = 0
            self.nospace = 1
            self.writer.send_flowing_data(' ')
        dla style w styles:
            self.style_stack.append(style)
        self.writer.new_styles(tuple(self.style_stack))

    def pop_style(self, n=1):
        usuń self.style_stack[-n:]
        self.writer.new_styles(tuple(self.style_stack))

    def assert_line_data(self, flag=1):
        self.nospace = self.hard_break = nie flag
        self.para_end = self.parskip = self.have_label = 0


klasa NullWriter:
    """Minimal writer interface to use w testing & inheritance.

    A writer which only provides the interface definition; no actions are
    taken on any methods.  This should be the base klasa dla all writers
    which do nie need to inherit any implementation methods.

    """
    def __init__(self): dalej
    def flush(self): dalej
    def new_alignment(self, align): dalej
    def new_font(self, font): dalej
    def new_margin(self, margin, level): dalej
    def new_spacing(self, spacing): dalej
    def new_styles(self, styles): dalej
    def send_paragraph(self, blankline): dalej
    def send_line_break(self): dalej
    def send_hor_rule(self, *args, **kw): dalej
    def send_label_data(self, data): dalej
    def send_flowing_data(self, data): dalej
    def send_literal_data(self, data): dalej


klasa AbstractWriter(NullWriter):
    """A writer which can be used w debugging formatters, but nie much inaczej.

    Each method simply announces itself by printing its name oraz
    arguments on standard output.

    """

    def new_alignment(self, align):
        print("new_alignment(%r)" % (align,))

    def new_font(self, font):
        print("new_font(%r)" % (font,))

    def new_margin(self, margin, level):
        print("new_margin(%r, %d)" % (margin, level))

    def new_spacing(self, spacing):
        print("new_spacing(%r)" % (spacing,))

    def new_styles(self, styles):
        print("new_styles(%r)" % (styles,))

    def send_paragraph(self, blankline):
        print("send_paragraph(%r)" % (blankline,))

    def send_line_break(self):
        print("send_line_break()")

    def send_hor_rule(self, *args, **kw):
        print("send_hor_rule()")

    def send_label_data(self, data):
        print("send_label_data(%r)" % (data,))

    def send_flowing_data(self, data):
        print("send_flowing_data(%r)" % (data,))

    def send_literal_data(self, data):
        print("send_literal_data(%r)" % (data,))


klasa DumbWriter(NullWriter):
    """Simple writer klasa which writes output on the file object dalejed w
    jako the file parameter or, jeżeli file jest omitted, on standard output.  The
    output jest simply word-wrapped to the number of columns specified by
    the maxcol parameter.  This klasa jest suitable dla reflowing a sequence
    of paragraphs.

    """

    def __init__(self, file=Nic, maxcol=72):
        self.file = file albo sys.stdout
        self.maxcol = maxcol
        NullWriter.__init__(self)
        self.reset()

    def reset(self):
        self.col = 0
        self.atbreak = 0

    def send_paragraph(self, blankline):
        self.file.write('\n'*blankline)
        self.col = 0
        self.atbreak = 0

    def send_line_break(self):
        self.file.write('\n')
        self.col = 0
        self.atbreak = 0

    def send_hor_rule(self, *args, **kw):
        self.file.write('\n')
        self.file.write('-'*self.maxcol)
        self.file.write('\n')
        self.col = 0
        self.atbreak = 0

    def send_literal_data(self, data):
        self.file.write(data)
        i = data.rfind('\n')
        jeżeli i >= 0:
            self.col = 0
            data = data[i+1:]
        data = data.expandtabs()
        self.col = self.col + len(data)
        self.atbreak = 0

    def send_flowing_data(self, data):
        jeżeli nie data: zwróć
        atbreak = self.atbreak albo data[0].isspace()
        col = self.col
        maxcol = self.maxcol
        write = self.file.write
        dla word w data.split():
            jeżeli atbreak:
                jeżeli col + len(word) >= maxcol:
                    write('\n')
                    col = 0
                inaczej:
                    write(' ')
                    col = col + 1
            write(word)
            col = col + len(word)
            atbreak = 1
        self.col = col
        self.atbreak = data[-1].isspace()


def test(file = Nic):
    w = DumbWriter()
    f = AbstractFormatter(w)
    jeżeli file jest nie Nic:
        fp = open(file)
    albo_inaczej sys.argv[1:]:
        fp = open(sys.argv[1])
    inaczej:
        fp = sys.stdin
    spróbuj:
        dla line w fp:
            jeżeli line == '\n':
                f.end_paragraph(1)
            inaczej:
                f.add_flowing_data(line)
    w_końcu:
        jeżeli fp jest nie sys.stdin:
            fp.close()
    f.end_paragraph(0)


jeżeli __name__ == '__main__':
    test()
