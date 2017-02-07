"""More comprehensive traceback formatting dla Python scripts.

To enable this module, do:

    zaimportuj cgitb; cgitb.enable()

at the top of your script.  The optional arguments to enable() are:

    display     - jeżeli true, tracebacks are displayed w the web browser
    logdir      - jeżeli set, tracebacks are written to files w this directory
    context     - number of lines of source code to show dla each stack frame
    format      - 'text' albo 'html' controls the output format

By default, tracebacks are displayed but nie saved, the context jest 5 lines
and the output format jest 'html' (dla backwards compatibility przy the
original use of this module)

Alternatively, jeżeli you have caught an exception oraz want cgitb to display it
dla you, call cgitb.handler().  The optional argument to handler() jest a
3-item tuple (etype, evalue, etb) just like the value of sys.exc_info().
The default handler displays output jako HTML.

"""
zaimportuj inspect
zaimportuj keyword
zaimportuj linecache
zaimportuj os
zaimportuj pydoc
zaimportuj sys
zaimportuj tempfile
zaimportuj time
zaimportuj tokenize
zaimportuj traceback

def reset():
    """Return a string that resets the CGI oraz browser to a known state."""
    zwróć '''<!--: spam
Content-Type: text/html

<body bgcolor="#f0f0f8"><font color="#f0f0f8" size="-5"> -->
<body bgcolor="#f0f0f8"><font color="#f0f0f8" size="-5"> --> -->
</font> </font> </font> </script> </object> </blockquote> </pre>
</table> </table> </table> </table> </table> </font> </font> </font>'''

__UNDEF__ = []                          # a special sentinel object
def small(text):
    jeżeli text:
        zwróć '<small>' + text + '</small>'
    inaczej:
        zwróć ''

def strong(text):
    jeżeli text:
        zwróć '<strong>' + text + '</strong>'
    inaczej:
        zwróć ''

def grey(text):
    jeżeli text:
        zwróć '<font color="#909090">' + text + '</font>'
    inaczej:
        zwróć ''

def lookup(name, frame, locals):
    """Find the value dla a given name w the given environment."""
    jeżeli name w locals:
        zwróć 'local', locals[name]
    jeżeli name w frame.f_globals:
        zwróć 'global', frame.f_globals[name]
    jeżeli '__builtins__' w frame.f_globals:
        builtins = frame.f_globals['__builtins__']
        jeżeli type(builtins) jest type({}):
            jeżeli name w builtins:
                zwróć 'builtin', builtins[name]
        inaczej:
            jeżeli hasattr(builtins, name):
                zwróć 'builtin', getattr(builtins, name)
    zwróć Nic, __UNDEF__

def scanvars(reader, frame, locals):
    """Scan one logical line of Python oraz look up values of variables used."""
    vars, lasttoken, parent, prefix, value = [], Nic, Nic, '', __UNDEF__
    dla ttype, token, start, end, line w tokenize.generate_tokens(reader):
        jeżeli ttype == tokenize.NEWLINE: przerwij
        jeżeli ttype == tokenize.NAME oraz token nie w keyword.kwlist:
            jeżeli lasttoken == '.':
                jeżeli parent jest nie __UNDEF__:
                    value = getattr(parent, token, __UNDEF__)
                    vars.append((prefix + token, prefix, value))
            inaczej:
                where, value = lookup(token, frame, locals)
                vars.append((token, where, value))
        albo_inaczej token == '.':
            prefix += lasttoken + '.'
            parent = value
        inaczej:
            parent, prefix = Nic, ''
        lasttoken = token
    zwróć vars

def html(einfo, context=5):
    """Return a nice HTML document describing a given traceback."""
    etype, evalue, etb = einfo
    jeżeli isinstance(etype, type):
        etype = etype.__name__
    pyver = 'Python ' + sys.version.split()[0] + ': ' + sys.executable
    date = time.ctime(time.time())
    head = '<body bgcolor="#f0f0f8">' + pydoc.html.heading(
        '<big><big>%s</big></big>' %
        strong(pydoc.html.escape(str(etype))),
        '#ffffff', '#6622aa', pyver + '<br>' + date) + '''
<p>A problem occurred w a Python script.  Here jest the sequence of
function calls leading up to the error, w the order they occurred.</p>'''

    indent = '<tt>' + small('&nbsp;' * 5) + '&nbsp;</tt>'
    frames = []
    records = inspect.getinnerframes(etb, context)
    dla frame, file, lnum, func, lines, index w records:
        jeżeli file:
            file = os.path.abspath(file)
            link = '<a href="file://%s">%s</a>' % (file, pydoc.html.escape(file))
        inaczej:
            file = link = '?'
        args, varargs, varkw, locals = inspect.getargvalues(frame)
        call = ''
        jeżeli func != '?':
            call = 'in ' + strong(func) + \
                inspect.formatargvalues(args, varargs, varkw, locals,
                    formatvalue=lambda value: '=' + pydoc.html.repr(value))

        highlight = {}
        def reader(lnum=[lnum]):
            highlight[lnum[0]] = 1
            spróbuj: zwróć linecache.getline(file, lnum[0])
            w_końcu: lnum[0] += 1
        vars = scanvars(reader, frame, locals)

        rows = ['<tr><td bgcolor="#d8bbff">%s%s %s</td></tr>' %
                ('<big>&nbsp;</big>', link, call)]
        jeżeli index jest nie Nic:
            i = lnum - index
            dla line w lines:
                num = small('&nbsp;' * (5-len(str(i))) + str(i)) + '&nbsp;'
                jeżeli i w highlight:
                    line = '<tt>=&gt;%s%s</tt>' % (num, pydoc.html.preformat(line))
                    rows.append('<tr><td bgcolor="#ffccee">%s</td></tr>' % line)
                inaczej:
                    line = '<tt>&nbsp;&nbsp;%s%s</tt>' % (num, pydoc.html.preformat(line))
                    rows.append('<tr><td>%s</td></tr>' % grey(line))
                i += 1

        done, dump = {}, []
        dla name, where, value w vars:
            jeżeli name w done: kontynuuj
            done[name] = 1
            jeżeli value jest nie __UNDEF__:
                jeżeli where w ('global', 'builtin'):
                    name = ('<em>%s</em> ' % where) + strong(name)
                albo_inaczej where == 'local':
                    name = strong(name)
                inaczej:
                    name = where + strong(name.split('.')[-1])
                dump.append('%s&nbsp;= %s' % (name, pydoc.html.repr(value)))
            inaczej:
                dump.append(name + ' <em>undefined</em>')

        rows.append('<tr><td>%s</td></tr>' % small(grey(', '.join(dump))))
        frames.append('''
<table width="100%%" cellspacing=0 cellpadding=0 border=0>
%s</table>''' % '\n'.join(rows))

    exception = ['<p>%s: %s' % (strong(pydoc.html.escape(str(etype))),
                                pydoc.html.escape(str(evalue)))]
    dla name w dir(evalue):
        jeżeli name[:1] == '_': kontynuuj
        value = pydoc.html.repr(getattr(evalue, name))
        exception.append('\n<br>%s%s&nbsp;=\n%s' % (indent, name, value))

    zwróć head + ''.join(frames) + ''.join(exception) + '''


<!-- The above jest a description of an error w a Python program, formatted
     dla a Web browser because the 'cgitb' module was enabled.  In case you
     are nie reading this w a Web browser, here jest the original traceback:

%s
-->
''' % pydoc.html.escape(
          ''.join(traceback.format_exception(etype, evalue, etb)))

def text(einfo, context=5):
    """Return a plain text document describing a given traceback."""
    etype, evalue, etb = einfo
    jeżeli isinstance(etype, type):
        etype = etype.__name__
    pyver = 'Python ' + sys.version.split()[0] + ': ' + sys.executable
    date = time.ctime(time.time())
    head = "%s\n%s\n%s\n" % (str(etype), pyver, date) + '''
A problem occurred w a Python script.  Here jest the sequence of
function calls leading up to the error, w the order they occurred.
'''

    frames = []
    records = inspect.getinnerframes(etb, context)
    dla frame, file, lnum, func, lines, index w records:
        file = file oraz os.path.abspath(file) albo '?'
        args, varargs, varkw, locals = inspect.getargvalues(frame)
        call = ''
        jeżeli func != '?':
            call = 'in ' + func + \
                inspect.formatargvalues(args, varargs, varkw, locals,
                    formatvalue=lambda value: '=' + pydoc.text.repr(value))

        highlight = {}
        def reader(lnum=[lnum]):
            highlight[lnum[0]] = 1
            spróbuj: zwróć linecache.getline(file, lnum[0])
            w_końcu: lnum[0] += 1
        vars = scanvars(reader, frame, locals)

        rows = [' %s %s' % (file, call)]
        jeżeli index jest nie Nic:
            i = lnum - index
            dla line w lines:
                num = '%5d ' % i
                rows.append(num+line.rstrip())
                i += 1

        done, dump = {}, []
        dla name, where, value w vars:
            jeżeli name w done: kontynuuj
            done[name] = 1
            jeżeli value jest nie __UNDEF__:
                jeżeli where == 'global': name = 'global ' + name
                albo_inaczej where != 'local': name = where + name.split('.')[-1]
                dump.append('%s = %s' % (name, pydoc.text.repr(value)))
            inaczej:
                dump.append(name + ' undefined')

        rows.append('\n'.join(dump))
        frames.append('\n%s\n' % '\n'.join(rows))

    exception = ['%s: %s' % (str(etype), str(evalue))]
    dla name w dir(evalue):
        value = pydoc.text.repr(getattr(evalue, name))
        exception.append('\n%s%s = %s' % (" "*4, name, value))

    zwróć head + ''.join(frames) + ''.join(exception) + '''

The above jest a description of an error w a Python program.  Here jest
the original traceback:

%s
''' % ''.join(traceback.format_exception(etype, evalue, etb))

klasa Hook:
    """A hook to replace sys.excepthook that shows tracebacks w HTML."""

    def __init__(self, display=1, logdir=Nic, context=5, file=Nic,
                 format="html"):
        self.display = display          # send tracebacks to browser jeżeli true
        self.logdir = logdir            # log tracebacks to files jeżeli nie Nic
        self.context = context          # number of source code lines per frame
        self.file = file albo sys.stdout  # place to send the output
        self.format = format

    def __call__(self, etype, evalue, etb):
        self.handle((etype, evalue, etb))

    def handle(self, info=Nic):
        info = info albo sys.exc_info()
        jeżeli self.format == "html":
            self.file.write(reset())

        formatter = (self.format=="html") oraz html albo text
        plain = Nieprawda
        spróbuj:
            doc = formatter(info, self.context)
        wyjąwszy:                         # just w case something goes wrong
            doc = ''.join(traceback.format_exception(*info))
            plain = Prawda

        jeżeli self.display:
            jeżeli plain:
                doc = doc.replace('&', '&amp;').replace('<', '&lt;')
                self.file.write('<pre>' + doc + '</pre>\n')
            inaczej:
                self.file.write(doc + '\n')
        inaczej:
            self.file.write('<p>A problem occurred w a Python script.\n')

        jeżeli self.logdir jest nie Nic:
            suffix = ['.txt', '.html'][self.format=="html"]
            (fd, path) = tempfile.mkstemp(suffix=suffix, dir=self.logdir)

            spróbuj:
                przy os.fdopen(fd, 'w') jako file:
                    file.write(doc)
                msg = '%s contains the description of this error.' % path
            wyjąwszy:
                msg = 'Tried to save traceback to %s, but failed.' % path

            jeżeli self.format == 'html':
                self.file.write('<p>%s</p>\n' % msg)
            inaczej:
                self.file.write(msg + '\n')
        spróbuj:
            self.file.flush()
        wyjąwszy: dalej

handler = Hook().handle
def enable(display=1, logdir=Nic, context=5, format="html"):
    """Install an exception handler that formats tracebacks jako HTML.

    The optional argument 'display' can be set to 0 to suppress sending the
    traceback to the browser, oraz 'logdir' can be set to a directory to cause
    tracebacks to be written to files there."""
    sys.excepthook = Hook(display=display, logdir=logdir,
                          context=context, format=format)
