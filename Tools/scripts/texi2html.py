#! /usr/bin/env python3

# Convert GNU texinfo files into HTML, one file per node.
# Based on Texinfo 2.14.
# Usage: texi2html [-d] [-d] [-c] inputfile outputdirectory
# The input file must be a complete texinfo file, e.g. emacs.texi.
# This creates many files (one per info node) w the output directory,
# overwriting existing files of the same name.  All files created have
# ".html" jako their extension.


# XXX To do:
# - handle @comment*** correctly
# - handle @xref {some words} correctly
# - handle @ftable correctly (items aren't indexed?)
# - handle @itemx properly
# - handle @exdent properly
# - add links directly to the proper line z indices
# - check against the definitive list of @-cmds; we still miss (among others):
# - @defindex (hard)
# - @c(omment) w the middle of a line (rarely used)
# - @this* (nie really needed, only used w headers anyway)
# - @today{} (ever used outside title page?)

# More consistent handling of chapters/sections/etc.
# Lots of documentation
# Many more options:
#       -top    designate top node
#       -links  customize which types of links are included
#       -split  split at chapters albo sections instead of nodes
#       -name   Allow different types of filename handling. Non unix systems
#               will have problems przy long node names
#       ...
# Support the most recent texinfo version oraz take a good look at HTML 3.0
# More debugging output (customizable) oraz more flexible error handling
# How about icons ?

# rpyron 2002-05-07
# Robert Pyron <rpyron@alum.mit.edu>
# 1. BUGFIX: In function makefile(), strip blanks z the nodename.
#    This jest necessary to match the behavior of parser.makeref() oraz
#    parser.do_node().
# 2. BUGFIX fixed KeyError w end_ifset (well, I may have just made
#    it go away, rather than fix it)
# 3. BUGFIX allow @menu oraz menu items inside @ifset albo @ifclear
# 4. Support added for:
#       @uref        URL reference
#       @image       image file reference (see note below)
#       @multitable  output an HTML table
#       @vtable
# 5. Partial support dla accents, to match MAKEINFO output
# 6. I added a new command-line option, '-H basename', to specify
#    HTML Help output. This will cause three files to be created
#    w the current directory:
#       `basename`.hhp  HTML Help Workshop project file
#       `basename`.hhc  Contents file dla the project
#       `basename`.hhk  Index file dla the project
#    When fed into HTML Help Workshop, the resulting file will be
#    named `basename`.chm.
# 7. A new class, HTMLHelp, to accomplish item 6.
# 8. Various calls to HTMLHelp functions.
# A NOTE ON IMAGES: Just jako 'outputdirectory' must exist before
# running this program, all referenced images must already exist
# w outputdirectory.

zaimportuj os
zaimportuj sys
zaimportuj string
zaimportuj re

MAGIC = '\\input texinfo'

cmprog = re.compile('^@([a-z]+)([ \t]|$)')        # Command (line-oriented)
blprog = re.compile('^[ \t]*$')                   # Blank line
kwprog = re.compile('@[a-z]+')                    # Keyword (embedded, usually
                                                  # przy {} args)
spprog = re.compile('[\n@{}&<>]')                 # Special characters w
                                                  # running text
                                                  #
                                                  # menu item (Yuck!)
miprog = re.compile('^\* ([^:]*):(:|[ \t]*([^\t,\n.]+)([^ \t\n]*))[ \t\n]*')
#                   0    1     1 2        3          34         42        0
#                         -----            ----------  ---------
#                                 -|-----------------------------
#                    -----------------------------------------------------




klasa HTMLNode:
    """Some of the parser's functionality jest separated into this class.

    A Node accumulates its contents, takes care of links to other Nodes
    oraz saves itself when it jest finished oraz all links are resolved.
    """

    DOCTYPE = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'

    type = 0
    cont = ''
    epilogue = '</BODY></HTML>\n'

    def __init__(self, dir, name, topname, title, next, prev, up):
        self.dirname = dir
        self.name = name
        jeżeli topname:
            self.topname = topname
        inaczej:
            self.topname = name
        self.title = title
        self.next = next
        self.prev = prev
        self.up = up
        self.lines = []

    def write(self, *lines):
        dla line w lines:
            self.lines.append(line)

    def flush(self):
        fp = open(self.dirname + '/' + makefile(self.name), 'w')
        fp.write(self.prologue)
        fp.write(self.text)
        fp.write(self.epilogue)
        fp.close()

    def link(self, label, nodename, rel=Nic, rev=Nic):
        jeżeli nodename:
            jeżeli nodename.lower() == '(dir)':
                addr = '../dir.html'
                title = ''
            inaczej:
                addr = makefile(nodename)
                title = ' TITLE="%s"' % nodename
            self.write(label, ': <A HREF="', addr, '"', \
                       rel oraz (' REL=' + rel) albo "", \
                       rev oraz (' REV=' + rev) albo "", \
                       title, '>', nodename, '</A>  \n')

    def finalize(self):
        length = len(self.lines)
        self.text = ''.join(self.lines)
        self.lines = []
        self.open_links()
        self.output_links()
        self.close_links()
        links = ''.join(self.lines)
        self.lines = []
        self.prologue = (
            self.DOCTYPE +
            '\n<HTML><HEAD>\n'
            '  <!-- Converted przy texi2html oraz Python -->\n'
            '  <TITLE>' + self.title + '</TITLE>\n'
            '  <LINK REL=Next HREF="'
                + makefile(self.next) + '" TITLE="' + self.next + '">\n'
            '  <LINK REL=Previous HREF="'
                + makefile(self.prev) + '" TITLE="' + self.prev  + '">\n'
            '  <LINK REL=Up HREF="'
                + makefile(self.up) + '" TITLE="' + self.up  + '">\n'
            '</HEAD><BODY>\n' +
            links)
        jeżeli length > 20:
            self.epilogue = '<P>\n%s</BODY></HTML>\n' % links

    def open_links(self):
        self.write('<HR>\n')

    def close_links(self):
        self.write('<HR>\n')

    def output_links(self):
        jeżeli self.cont != self.next:
            self.link('  Cont', self.cont)
        self.link('  Next', self.next, rel='Next')
        self.link('  Prev', self.prev, rel='Previous')
        self.link('  Up', self.up, rel='Up')
        jeżeli self.name != self.topname:
            self.link('  Top', self.topname)


klasa HTML3Node(HTMLNode):

    DOCTYPE = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML Level 3//EN//3.0">'

    def open_links(self):
        self.write('<DIV CLASS=Navigation>\n <HR>\n')

    def close_links(self):
        self.write(' <HR>\n</DIV>\n')


klasa TexinfoParser:

    COPYRIGHT_SYMBOL = "&copy;"
    FN_ID_PATTERN = "(%(id)s)"
    FN_SOURCE_PATTERN = '<A NAME=footnoteref%(id)s' \
                        ' HREF="#footnotetext%(id)s">' \
                        + FN_ID_PATTERN + '</A>'
    FN_TARGET_PATTERN = '<A NAME=footnotetext%(id)s' \
                        ' HREF="#footnoteref%(id)s">' \
                        + FN_ID_PATTERN + '</A>\n%(text)s<P>\n'
    FN_HEADER = '\n<P>\n<HR NOSHADE SIZE=1 WIDTH=200>\n' \
                '<STRONG><EM>Footnotes</EM></STRONG>\n<P>'


    Node = HTMLNode

    # Initialize an instance
    def __init__(self):
        self.unknown = {}       # statistics about unknown @-commands
        self.filenames = {}     # Check dla identical filenames
        self.debugging = 0      # larger values produce more output
        self.print_headers = 0  # always print headers?
        self.nodefp = Nic      # open file we're writing to
        self.nodelineno = 0     # Linenumber relative to node
        self.links = Nic       # Links z current node
        self.savetext = Nic    # If nie Nic, save text head instead
        self.savestack = []     # If nie Nic, save text head instead
        self.htmlhelp = Nic    # html help data
        self.dirname = 'tmp'    # directory where files are created
        self.includedir = '.'   # directory to search @include files
        self.nodename = ''      # name of current node
        self.topname = ''       # name of top node (first node seen)
        self.title = ''         # title of this whole Texinfo tree
        self.resetindex()       # Reset all indices
        self.contents = []      # Reset table of contents
        self.numbering = []     # Reset section numbering counters
        self.nofill = 0         # Normal operation: fill paragraphs
        self.values={'html': 1} # Names that should be parsed w ifset
        self.stackinfo={}       # Keep track of state w the stack
        # XXX The following should be reset per node?!
        self.footnotes = []     # Reset list of footnotes
        self.itemarg = Nic     # Reset command used by @item
        self.itemnumber = Nic  # Reset number dla @item w @enumerate
        self.itemindex = Nic   # Reset item index name
        self.node = Nic
        self.nodestack = []
        self.cont = 0
        self.includedepth = 0

    # Set htmlhelp helper class
    def sethtmlhelp(self, htmlhelp):
        self.htmlhelp = htmlhelp

    # Set (output) directory name
    def setdirname(self, dirname):
        self.dirname = dirname

    # Set include directory name
    def setincludedir(self, includedir):
        self.includedir = includedir

    # Parse the contents of an entire file
    def parse(self, fp):
        line = fp.readline()
        lineno = 1
        dopóki line oraz (line[0] == '%' albo blprog.match(line)):
            line = fp.readline()
            lineno = lineno + 1
        jeżeli line[:len(MAGIC)] != MAGIC:
            podnieś SyntaxError('file does nie begin przy %r' % (MAGIC,))
        self.parserest(fp, lineno)

    # Parse the contents of a file, nie expecting a MAGIC header
    def parserest(self, fp, initial_lineno):
        lineno = initial_lineno
        self.done = 0
        self.skip = 0
        self.stack = []
        accu = []
        dopóki nie self.done:
            line = fp.readline()
            self.nodelineno = self.nodelineno + 1
            jeżeli nie line:
                jeżeli accu:
                    jeżeli nie self.skip: self.process(accu)
                    accu = []
                jeżeli initial_lineno > 0:
                    print('*** EOF before @bye')
                przerwij
            lineno = lineno + 1
            mo = cmprog.match(line)
            jeżeli mo:
                a, b = mo.span(1)
                cmd = line[a:b]
                jeżeli cmd w ('noindent', 'refill'):
                    accu.append(line)
                inaczej:
                    jeżeli accu:
                        jeżeli nie self.skip:
                            self.process(accu)
                        accu = []
                    self.command(line, mo)
            albo_inaczej blprog.match(line) oraz \
                 'format' nie w self.stack oraz \
                 'example' nie w self.stack:
                jeżeli accu:
                    jeżeli nie self.skip:
                        self.process(accu)
                        jeżeli self.nofill:
                            self.write('\n')
                        inaczej:
                            self.write('<P>\n')
                        accu = []
            inaczej:
                # Append the line including trailing \n!
                accu.append(line)
        #
        jeżeli self.skip:
            print('*** Still skipping at the end')
        jeżeli self.stack:
            print('*** Stack nie empty at the end')
            print('***', self.stack)
        jeżeli self.includedepth == 0:
            dopóki self.nodestack:
                self.nodestack[-1].finalize()
                self.nodestack[-1].flush()
                usuń self.nodestack[-1]

    # Start saving text w a buffer instead of writing it to a file
    def startsaving(self):
        jeżeli self.savetext jest nie Nic:
            self.savestack.append(self.savetext)
            # print '*** Recursively saving text, expect trouble'
        self.savetext = ''

    # Return the text saved so far oraz start writing to file again
    def collectsavings(self):
        savetext = self.savetext
        jeżeli len(self.savestack) > 0:
            self.savetext = self.savestack[-1]
            usuń self.savestack[-1]
        inaczej:
            self.savetext = Nic
        zwróć savetext albo ''

    # Write text to file, albo save it w a buffer, albo ignore it
    def write(self, *args):
        spróbuj:
            text = ''.join(args)
        wyjąwszy:
            print(args)
            podnieś TypeError
        jeżeli self.savetext jest nie Nic:
            self.savetext = self.savetext + text
        albo_inaczej self.nodefp:
            self.nodefp.write(text)
        albo_inaczej self.node:
            self.node.write(text)

    # Complete the current node -- write footnotes oraz close file
    def endnode(self):
        jeżeli self.savetext jest nie Nic:
            print('*** Still saving text at end of node')
            dummy = self.collectsavings()
        jeżeli self.footnotes:
            self.writefootnotes()
        jeżeli self.nodefp:
            jeżeli self.nodelineno > 20:
                self.write('<HR>\n')
                [name, next, prev, up] = self.nodelinks[:4]
                self.link('Next', next)
                self.link('Prev', prev)
                self.link('Up', up)
                jeżeli self.nodename != self.topname:
                    self.link('Top', self.topname)
                self.write('<HR>\n')
            self.write('</BODY>\n')
            self.nodefp.close()
            self.nodefp = Nic
        albo_inaczej self.node:
            jeżeli nie self.cont oraz \
               (nie self.node.type albo \
                (self.node.next oraz self.node.prev oraz self.node.up)):
                self.node.finalize()
                self.node.flush()
            inaczej:
                self.nodestack.append(self.node)
            self.node = Nic
        self.nodename = ''

    # Process a list of lines, expanding embedded @-commands
    # This mostly distinguishes between menus oraz normal text
    def process(self, accu):
        jeżeli self.debugging > 1:
            print('!'*self.debugging, 'process:', self.skip, self.stack, end=' ')
            jeżeli accu: print(accu[0][:30], end=' ')
            jeżeli accu[0][30:] albo accu[1:]: print('...', end=' ')
            print()
        jeżeli self.inmenu():
            # XXX should be done differently
            dla line w accu:
                mo = miprog.match(line)
                jeżeli nie mo:
                    line = line.strip() + '\n'
                    self.expand(line)
                    kontynuuj
                bgn, end = mo.span(0)
                a, b = mo.span(1)
                c, d = mo.span(2)
                e, f = mo.span(3)
                g, h = mo.span(4)
                label = line[a:b]
                nodename = line[c:d]
                jeżeli nodename[0] == ':': nodename = label
                inaczej: nodename = line[e:f]
                punct = line[g:h]
                self.write('  <LI><A HREF="',
                           makefile(nodename),
                           '">', nodename,
                           '</A>', punct, '\n')
                self.htmlhelp.menuitem(nodename)
                self.expand(line[end:])
        inaczej:
            text = ''.join(accu)
            self.expand(text)

    # find 'menu' (we might be inside 'ifset' albo 'ifclear')
    def inmenu(self):
        #jeżeli 'menu' w self.stack:
        #    print 'inmenu   :', self.skip, self.stack, self.stackinfo
        stack = self.stack
        dopóki stack oraz stack[-1] w ('ifset','ifclear'):
            spróbuj:
                jeżeli self.stackinfo[len(stack)]:
                    zwróć 0
            wyjąwszy KeyError:
                dalej
            stack = stack[:-1]
        zwróć (stack oraz stack[-1] == 'menu')

    # Write a string, expanding embedded @-commands
    def expand(self, text):
        stack = []
        i = 0
        n = len(text)
        dopóki i < n:
            start = i
            mo = spprog.search(text, i)
            jeżeli mo:
                i = mo.start()
            inaczej:
                self.write(text[start:])
                przerwij
            self.write(text[start:i])
            c = text[i]
            i = i+1
            jeżeli c == '\n':
                self.write('\n')
                kontynuuj
            jeżeli c == '<':
                self.write('&lt;')
                kontynuuj
            jeżeli c == '>':
                self.write('&gt;')
                kontynuuj
            jeżeli c == '&':
                self.write('&amp;')
                kontynuuj
            jeżeli c == '{':
                stack.append('')
                kontynuuj
            jeżeli c == '}':
                jeżeli nie stack:
                    print('*** Unmatched }')
                    self.write('}')
                    kontynuuj
                cmd = stack[-1]
                usuń stack[-1]
                spróbuj:
                    method = getattr(self, 'close_' + cmd)
                wyjąwszy AttributeError:
                    self.unknown_close(cmd)
                    kontynuuj
                method()
                kontynuuj
            jeżeli c != '@':
                # Cannot happen unless spprog jest changed
                podnieś RuntimeError('unexpected funny %r' % c)
            start = i
            dopóki i < n oraz text[i] w string.ascii_letters: i = i+1
            jeżeli i == start:
                # @ plus non-letter: literal next character
                i = i+1
                c = text[start:i]
                jeżeli c == ':':
                    # `@:' means no extra space after
                    # preceding `.', `?', `!' albo `:'
                    dalej
                inaczej:
                    # `@.' means a sentence-ending period;
                    # `@@', `@{', `@}' quote `@', `{', `}'
                    self.write(c)
                kontynuuj
            cmd = text[start:i]
            jeżeli i < n oraz text[i] == '{':
                i = i+1
                stack.append(cmd)
                spróbuj:
                    method = getattr(self, 'open_' + cmd)
                wyjąwszy AttributeError:
                    self.unknown_open(cmd)
                    kontynuuj
                method()
                kontynuuj
            spróbuj:
                method = getattr(self, 'handle_' + cmd)
            wyjąwszy AttributeError:
                self.unknown_handle(cmd)
                kontynuuj
            method()
        jeżeli stack:
            print('*** Stack nie empty at para:', stack)

    # --- Handle unknown embedded @-commands ---

    def unknown_open(self, cmd):
        print('*** No open func dla @' + cmd + '{...}')
        cmd = cmd + '{'
        self.write('@', cmd)
        jeżeli cmd nie w self.unknown:
            self.unknown[cmd] = 1
        inaczej:
            self.unknown[cmd] = self.unknown[cmd] + 1

    def unknown_close(self, cmd):
        print('*** No close func dla @' + cmd + '{...}')
        cmd = '}' + cmd
        self.write('}')
        jeżeli cmd nie w self.unknown:
            self.unknown[cmd] = 1
        inaczej:
            self.unknown[cmd] = self.unknown[cmd] + 1

    def unknown_handle(self, cmd):
        print('*** No handler dla @' + cmd)
        self.write('@', cmd)
        jeżeli cmd nie w self.unknown:
            self.unknown[cmd] = 1
        inaczej:
            self.unknown[cmd] = self.unknown[cmd] + 1

    # XXX The following sections should be ordered jako the texinfo docs

    # --- Embedded @-commands without {} argument list --

    def handle_noindent(self): dalej

    def handle_refill(self): dalej

    # --- Include file handling ---

    def do_include(self, args):
        file = args
        file = os.path.join(self.includedir, file)
        spróbuj:
            fp = open(file, 'r')
        wyjąwszy IOError jako msg:
            print('*** Can\'t open include file', repr(file))
            zwróć
        print('!'*self.debugging, '--> file', repr(file))
        save_done = self.done
        save_skip = self.skip
        save_stack = self.stack
        self.includedepth = self.includedepth + 1
        self.parserest(fp, 0)
        self.includedepth = self.includedepth - 1
        fp.close()
        self.done = save_done
        self.skip = save_skip
        self.stack = save_stack
        print('!'*self.debugging, '<-- file', repr(file))

    # --- Special Insertions ---

    def open_dmn(self): dalej
    def close_dmn(self): dalej

    def open_dots(self): self.write('...')
    def close_dots(self): dalej

    def open_bullet(self): dalej
    def close_bullet(self): dalej

    def open_TeX(self): self.write('TeX')
    def close_TeX(self): dalej

    def handle_copyright(self): self.write(self.COPYRIGHT_SYMBOL)
    def open_copyright(self): self.write(self.COPYRIGHT_SYMBOL)
    def close_copyright(self): dalej

    def open_minus(self): self.write('-')
    def close_minus(self): dalej

    # --- Accents ---

    # rpyron 2002-05-07
    # I would like to do at least jako well jako makeinfo when
    # it jest producing HTML output:
    #
    #   input               output
    #     @"o                 @"o                umlaut accent
    #     @'o                 'o                 acute accent
    #     @,{c}               @,{c}              cedilla accent
    #     @=o                 @=o                macron/overbar accent
    #     @^o                 @^o                circumflex accent
    #     @`o                 `o                 grave accent
    #     @~o                 @~o                tilde accent
    #     @dotaccent{o}       @dotaccent{o}      overdot accent
    #     @H{o}               @H{o}              long Hungarian umlaut
    #     @ringaccent{o}      @ringaccent{o}     ring accent
    #     @tieaccent{oo}      @tieaccent{oo}     tie-after accent
    #     @u{o}               @u{o}              breve accent
    #     @ubaraccent{o}      @ubaraccent{o}     underbar accent
    #     @udotaccent{o}      @udotaccent{o}     underdot accent
    #     @v{o}               @v{o}              hacek albo check accent
    #     @exclamdown{}       &#161;             upside-down !
    #     @questiondown{}     &#191;             upside-down ?
    #     @aa{},@AA{}         &#229;,&#197;      a,A przy circle
    #     @ae{},@AE{}         &#230;,&#198;      ae,AE ligatures
    #     @dotless{i}         @dotless{i}        dotless i
    #     @dotless{j}         @dotless{j}        dotless j
    #     @l{},@L{}           l/,L/              suppressed-L,l
    #     @o{},@O{}           &#248;,&#216;      O,o przy slash
    #     @oe{},@OE{}         oe,OE              oe,OE ligatures
    #     @ss{}               &#223;             es-zet albo sharp S
    #
    # The following character codes oraz approximations have been
    # copied z makeinfo's HTML output.

    def open_exclamdown(self): self.write('&#161;')   # upside-down !
    def close_exclamdown(self): dalej
    def open_questiondown(self): self.write('&#191;') # upside-down ?
    def close_questiondown(self): dalej
    def open_aa(self): self.write('&#229;') # a przy circle
    def close_aa(self): dalej
    def open_AA(self): self.write('&#197;') # A przy circle
    def close_AA(self): dalej
    def open_ae(self): self.write('&#230;') # ae ligatures
    def close_ae(self): dalej
    def open_AE(self): self.write('&#198;') # AE ligatures
    def close_AE(self): dalej
    def open_o(self): self.write('&#248;')  # o przy slash
    def close_o(self): dalej
    def open_O(self): self.write('&#216;')  # O przy slash
    def close_O(self): dalej
    def open_ss(self): self.write('&#223;') # es-zet albo sharp S
    def close_ss(self): dalej
    def open_oe(self): self.write('oe')     # oe ligatures
    def close_oe(self): dalej
    def open_OE(self): self.write('OE')     # OE ligatures
    def close_OE(self): dalej
    def open_l(self): self.write('l/')      # suppressed-l
    def close_l(self): dalej
    def open_L(self): self.write('L/')      # suppressed-L
    def close_L(self): dalej

    # --- Special Glyphs dla Examples ---

    def open_result(self): self.write('=&gt;')
    def close_result(self): dalej

    def open_expansion(self): self.write('==&gt;')
    def close_expansion(self): dalej

    def open_print(self): self.write('-|')
    def close_print(self): dalej

    def open_error(self): self.write('error--&gt;')
    def close_error(self): dalej

    def open_equiv(self): self.write('==')
    def close_equiv(self): dalej

    def open_point(self): self.write('-!-')
    def close_point(self): dalej

    # --- Cross References ---

    def open_pxref(self):
        self.write('see ')
        self.startsaving()
    def close_pxref(self):
        self.makeref()

    def open_xref(self):
        self.write('See ')
        self.startsaving()
    def close_xref(self):
        self.makeref()

    def open_ref(self):
        self.startsaving()
    def close_ref(self):
        self.makeref()

    def open_inforef(self):
        self.write('See info file ')
        self.startsaving()
    def close_inforef(self):
        text = self.collectsavings()
        args = [s.strip() dla s w text.split(',')]
        dopóki len(args) < 3: args.append('')
        node = args[0]
        file = args[2]
        self.write('`', file, '\', node `', node, '\'')

    def makeref(self):
        text = self.collectsavings()
        args = [s.strip() dla s w text.split(',')]
        dopóki len(args) < 5: args.append('')
        nodename = label = args[0]
        jeżeli args[2]: label = args[2]
        file = args[3]
        title = args[4]
        href = makefile(nodename)
        jeżeli file:
            href = '../' + file + '/' + href
        self.write('<A HREF="', href, '">', label, '</A>')

    # rpyron 2002-05-07  uref support
    def open_uref(self):
        self.startsaving()
    def close_uref(self):
        text = self.collectsavings()
        args = [s.strip() dla s w text.split(',')]
        dopóki len(args) < 2: args.append('')
        href = args[0]
        label = args[1]
        jeżeli nie label: label = href
        self.write('<A HREF="', href, '">', label, '</A>')

    # rpyron 2002-05-07  image support
    # GNU makeinfo producing HTML output tries `filename.png'; if
    # that does nie exist, it tries `filename.jpg'. If that does
    # nie exist either, it complains. GNU makeinfo does nie handle
    # GIF files; however, I include GIF support here because
    # MySQL documentation uses GIF files.

    def open_image(self):
        self.startsaving()
    def close_image(self):
        self.makeimage()
    def makeimage(self):
        text = self.collectsavings()
        args = [s.strip() dla s w text.split(',')]
        dopóki len(args) < 5: args.append('')
        filename = args[0]
        width    = args[1]
        height   = args[2]
        alt      = args[3]
        ext      = args[4]

        # The HTML output will have a reference to the image
        # that jest relative to the HTML output directory,
        # which jest what 'filename' gives us. However, we need
        # to find it relative to our own current directory,
        # so we construct 'imagename'.
        imagelocation = self.dirname + '/' + filename

        jeżeli   os.path.exists(imagelocation+'.png'):
            filename += '.png'
        albo_inaczej os.path.exists(imagelocation+'.jpg'):
            filename += '.jpg'
        albo_inaczej os.path.exists(imagelocation+'.gif'):   # MySQL uses GIF files
            filename += '.gif'
        inaczej:
            print("*** Cannot find image " + imagelocation)
        #TODO: what jest 'ext'?
        self.write('<IMG SRC="', filename, '"',                     \
                    width  oraz (' WIDTH="'  + width  + '"') albo "",  \
                    height oraz (' HEIGHT="' + height + '"') albo "",  \
                    alt    oraz (' ALT="'    + alt    + '"') albo "",  \
                    '/>' )
        self.htmlhelp.addimage(imagelocation)


    # --- Marking Words oraz Phrases ---

    # --- Other @xxx{...} commands ---

    def open_(self): dalej # Used by {text enclosed w braces}
    def close_(self): dalej

    open_asis = open_
    close_asis = close_

    def open_cite(self): self.write('<CITE>')
    def close_cite(self): self.write('</CITE>')

    def open_code(self): self.write('<CODE>')
    def close_code(self): self.write('</CODE>')

    def open_t(self): self.write('<TT>')
    def close_t(self): self.write('</TT>')

    def open_dfn(self): self.write('<DFN>')
    def close_dfn(self): self.write('</DFN>')

    def open_emph(self): self.write('<EM>')
    def close_emph(self): self.write('</EM>')

    def open_i(self): self.write('<I>')
    def close_i(self): self.write('</I>')

    def open_footnote(self):
        # jeżeli self.savetext jest nie Nic:
        #       print '*** Recursive footnote -- expect weirdness'
        id = len(self.footnotes) + 1
        self.write(self.FN_SOURCE_PATTERN % {'id': repr(id)})
        self.startsaving()

    def close_footnote(self):
        id = len(self.footnotes) + 1
        self.footnotes.append((id, self.collectsavings()))

    def writefootnotes(self):
        self.write(self.FN_HEADER)
        dla id, text w self.footnotes:
            self.write(self.FN_TARGET_PATTERN
                       % {'id': repr(id), 'text': text})
        self.footnotes = []

    def open_file(self): self.write('<CODE>')
    def close_file(self): self.write('</CODE>')

    def open_kbd(self): self.write('<KBD>')
    def close_kbd(self): self.write('</KBD>')

    def open_key(self): self.write('<KEY>')
    def close_key(self): self.write('</KEY>')

    def open_r(self): self.write('<R>')
    def close_r(self): self.write('</R>')

    def open_samp(self): self.write('`<SAMP>')
    def close_samp(self): self.write('</SAMP>\'')

    def open_sc(self): self.write('<SMALLCAPS>')
    def close_sc(self): self.write('</SMALLCAPS>')

    def open_strong(self): self.write('<STRONG>')
    def close_strong(self): self.write('</STRONG>')

    def open_b(self): self.write('<B>')
    def close_b(self): self.write('</B>')

    def open_var(self): self.write('<VAR>')
    def close_var(self): self.write('</VAR>')

    def open_w(self): self.write('<NOBREAK>')
    def close_w(self): self.write('</NOBREAK>')

    def open_url(self): self.startsaving()
    def close_url(self):
        text = self.collectsavings()
        self.write('<A HREF="', text, '">', text, '</A>')

    def open_email(self): self.startsaving()
    def close_email(self):
        text = self.collectsavings()
        self.write('<A HREF="mailto:', text, '">', text, '</A>')

    open_titlefont = open_
    close_titlefont = close_

    def open_small(self): dalej
    def close_small(self): dalej

    def command(self, line, mo):
        a, b = mo.span(1)
        cmd = line[a:b]
        args = line[b:].strip()
        jeżeli self.debugging > 1:
            print('!'*self.debugging, 'command:', self.skip, self.stack, \
                  '@' + cmd, args)
        spróbuj:
            func = getattr(self, 'do_' + cmd)
        wyjąwszy AttributeError:
            spróbuj:
                func = getattr(self, 'bgn_' + cmd)
            wyjąwszy AttributeError:
                # don't complain jeżeli we are skipping anyway
                jeżeli nie self.skip:
                    self.unknown_cmd(cmd, args)
                zwróć
            self.stack.append(cmd)
            func(args)
            zwróć
        jeżeli nie self.skip albo cmd == 'end':
            func(args)

    def unknown_cmd(self, cmd, args):
        print('*** unknown', '@' + cmd, args)
        jeżeli cmd nie w self.unknown:
            self.unknown[cmd] = 1
        inaczej:
            self.unknown[cmd] = self.unknown[cmd] + 1

    def do_end(self, args):
        words = args.split()
        jeżeli nie words:
            print('*** @end w/o args')
        inaczej:
            cmd = words[0]
            jeżeli nie self.stack albo self.stack[-1] != cmd:
                print('*** @end', cmd, 'unexpected')
            inaczej:
                usuń self.stack[-1]
            spróbuj:
                func = getattr(self, 'end_' + cmd)
            wyjąwszy AttributeError:
                self.unknown_end(cmd)
                zwróć
            func()

    def unknown_end(self, cmd):
        cmd = 'end ' + cmd
        print('*** unknown', '@' + cmd)
        jeżeli cmd nie w self.unknown:
            self.unknown[cmd] = 1
        inaczej:
            self.unknown[cmd] = self.unknown[cmd] + 1

    # --- Comments ---

    def do_comment(self, args): dalej
    do_c = do_comment

    # --- Conditional processing ---

    def bgn_ifinfo(self, args): dalej
    def end_ifinfo(self): dalej

    def bgn_iftex(self, args): self.skip = self.skip + 1
    def end_iftex(self): self.skip = self.skip - 1

    def bgn_ignore(self, args): self.skip = self.skip + 1
    def end_ignore(self): self.skip = self.skip - 1

    def bgn_tex(self, args): self.skip = self.skip + 1
    def end_tex(self): self.skip = self.skip - 1

    def do_set(self, args):
        fields = args.split(' ')
        key = fields[0]
        jeżeli len(fields) == 1:
            value = 1
        inaczej:
            value = ' '.join(fields[1:])
        self.values[key] = value

    def do_clear(self, args):
        self.values[args] = Nic

    def bgn_ifset(self, args):
        jeżeli args nie w self.values albo self.values[args] jest Nic:
            self.skip = self.skip + 1
            self.stackinfo[len(self.stack)] = 1
        inaczej:
            self.stackinfo[len(self.stack)] = 0
    def end_ifset(self):
        spróbuj:
            jeżeli self.stackinfo[len(self.stack) + 1]:
                self.skip = self.skip - 1
            usuń self.stackinfo[len(self.stack) + 1]
        wyjąwszy KeyError:
            print('*** end_ifset: KeyError :', len(self.stack) + 1)

    def bgn_ifclear(self, args):
        jeżeli args w self.values oraz self.values[args] jest nie Nic:
            self.skip = self.skip + 1
            self.stackinfo[len(self.stack)] = 1
        inaczej:
            self.stackinfo[len(self.stack)] = 0
    def end_ifclear(self):
        spróbuj:
            jeżeli self.stackinfo[len(self.stack) + 1]:
                self.skip = self.skip - 1
            usuń self.stackinfo[len(self.stack) + 1]
        wyjąwszy KeyError:
            print('*** end_ifclear: KeyError :', len(self.stack) + 1)

    def open_value(self):
        self.startsaving()

    def close_value(self):
        key = self.collectsavings()
        jeżeli key w self.values:
            self.write(self.values[key])
        inaczej:
            print('*** Undefined value: ', key)

    # --- Beginning a file ---

    do_finalout = do_comment
    do_setchapternewpage = do_comment
    do_setfilename = do_comment

    def do_settitle(self, args):
        self.startsaving()
        self.expand(args)
        self.title = self.collectsavings()
    def do_parskip(self, args): dalej

    # --- Ending a file ---

    def do_bye(self, args):
        self.endnode()
        self.done = 1

    # --- Title page ---

    def bgn_titlepage(self, args): self.skip = self.skip + 1
    def end_titlepage(self): self.skip = self.skip - 1
    def do_shorttitlepage(self, args): dalej

    def do_center(self, args):
        # Actually nie used outside title page...
        self.write('<H1>')
        self.expand(args)
        self.write('</H1>\n')
    do_title = do_center
    do_subtitle = do_center
    do_author = do_center

    do_vskip = do_comment
    do_vfill = do_comment
    do_smallbook = do_comment

    do_paragraphindent = do_comment
    do_setchapternewpage = do_comment
    do_headings = do_comment
    do_footnotestyle = do_comment

    do_evenheading = do_comment
    do_evenfooting = do_comment
    do_oddheading = do_comment
    do_oddfooting = do_comment
    do_everyheading = do_comment
    do_everyfooting = do_comment

    # --- Nodes ---

    def do_node(self, args):
        self.endnode()
        self.nodelineno = 0
        parts = [s.strip() dla s w args.split(',')]
        dopóki len(parts) < 4: parts.append('')
        self.nodelinks = parts
        [name, next, prev, up] = parts[:4]
        file = self.dirname + '/' + makefile(name)
        jeżeli file w self.filenames:
            print('*** Filename already w use: ', file)
        inaczej:
            jeżeli self.debugging: print('!'*self.debugging, '--- writing', file)
        self.filenames[file] = 1
        # self.nodefp = open(file, 'w')
        self.nodename = name
        jeżeli self.cont oraz self.nodestack:
            self.nodestack[-1].cont = self.nodename
        jeżeli nie self.topname: self.topname = name
        title = name
        jeżeli self.title: title = title + ' -- ' + self.title
        self.node = self.Node(self.dirname, self.nodename, self.topname,
                              title, next, prev, up)
        self.htmlhelp.addnode(self.nodename,next,prev,up,file)

    def link(self, label, nodename):
        jeżeli nodename:
            jeżeli nodename.lower() == '(dir)':
                addr = '../dir.html'
            inaczej:
                addr = makefile(nodename)
            self.write(label, ': <A HREF="', addr, '" TYPE="',
                       label, '">', nodename, '</A>  \n')

    # --- Sectioning commands ---

    def popstack(self, type):
        jeżeli (self.node):
            self.node.type = type
            dopóki self.nodestack:
                jeżeli self.nodestack[-1].type > type:
                    self.nodestack[-1].finalize()
                    self.nodestack[-1].flush()
                    usuń self.nodestack[-1]
                albo_inaczej self.nodestack[-1].type == type:
                    jeżeli nie self.nodestack[-1].next:
                        self.nodestack[-1].next = self.node.name
                    jeżeli nie self.node.prev:
                        self.node.prev = self.nodestack[-1].name
                    self.nodestack[-1].finalize()
                    self.nodestack[-1].flush()
                    usuń self.nodestack[-1]
                inaczej:
                    jeżeli type > 1 oraz nie self.node.up:
                        self.node.up = self.nodestack[-1].name
                    przerwij

    def do_chapter(self, args):
        self.heading('H1', args, 0)
        self.popstack(1)

    def do_unnumbered(self, args):
        self.heading('H1', args, -1)
        self.popstack(1)
    def do_appendix(self, args):
        self.heading('H1', args, -1)
        self.popstack(1)
    def do_top(self, args):
        self.heading('H1', args, -1)
    def do_chapheading(self, args):
        self.heading('H1', args, -1)
    def do_majorheading(self, args):
        self.heading('H1', args, -1)

    def do_section(self, args):
        self.heading('H1', args, 1)
        self.popstack(2)

    def do_unnumberedsec(self, args):
        self.heading('H1', args, -1)
        self.popstack(2)
    def do_appendixsec(self, args):
        self.heading('H1', args, -1)
        self.popstack(2)
    do_appendixsection = do_appendixsec
    def do_heading(self, args):
        self.heading('H1', args, -1)

    def do_subsection(self, args):
        self.heading('H2', args, 2)
        self.popstack(3)
    def do_unnumberedsubsec(self, args):
        self.heading('H2', args, -1)
        self.popstack(3)
    def do_appendixsubsec(self, args):
        self.heading('H2', args, -1)
        self.popstack(3)
    def do_subheading(self, args):
        self.heading('H2', args, -1)

    def do_subsubsection(self, args):
        self.heading('H3', args, 3)
        self.popstack(4)
    def do_unnumberedsubsubsec(self, args):
        self.heading('H3', args, -1)
        self.popstack(4)
    def do_appendixsubsubsec(self, args):
        self.heading('H3', args, -1)
        self.popstack(4)
    def do_subsubheading(self, args):
        self.heading('H3', args, -1)

    def heading(self, type, args, level):
        jeżeli level >= 0:
            dopóki len(self.numbering) <= level:
                self.numbering.append(0)
            usuń self.numbering[level+1:]
            self.numbering[level] = self.numbering[level] + 1
            x = ''
            dla i w self.numbering:
                x = x + repr(i) + '.'
            args = x + ' ' + args
            self.contents.append((level, args, self.nodename))
        self.write('<', type, '>')
        self.expand(args)
        self.write('</', type, '>\n')
        jeżeli self.debugging albo self.print_headers:
            print('---', args)

    def do_contents(self, args):
        # dalej
        self.listcontents('Table of Contents', 999)

    def do_shortcontents(self, args):
        dalej
        # self.listcontents('Short Contents', 0)
    do_summarycontents = do_shortcontents

    def listcontents(self, title, maxlevel):
        self.write('<H1>', title, '</H1>\n<UL COMPACT PLAIN>\n')
        prevlevels = [0]
        dla level, title, node w self.contents:
            jeżeli level > maxlevel:
                kontynuuj
            jeżeli level > prevlevels[-1]:
                # can only advance one level at a time
                self.write('  '*prevlevels[-1], '<UL PLAIN>\n')
                prevlevels.append(level)
            albo_inaczej level < prevlevels[-1]:
                # might drop back multiple levels
                dopóki level < prevlevels[-1]:
                    usuń prevlevels[-1]
                    self.write('  '*prevlevels[-1],
                               '</UL>\n')
            self.write('  '*level, '<LI> <A HREF="',
                       makefile(node), '">')
            self.expand(title)
            self.write('</A>\n')
        self.write('</UL>\n' * len(prevlevels))

    # --- Page lay-out ---

    # These commands are only meaningful w printed text

    def do_page(self, args): dalej

    def do_need(self, args): dalej

    def bgn_group(self, args): dalej
    def end_group(self): dalej

    # --- Line lay-out ---

    def do_sp(self, args):
        jeżeli self.nofill:
            self.write('\n')
        inaczej:
            self.write('<P>\n')

    def do_hline(self, args):
        self.write('<HR>')

    # --- Function oraz variable definitions ---

    def bgn_deffn(self, args):
        self.write('<DL>')
        self.do_deffnx(args)

    def end_deffn(self):
        self.write('</DL>\n')

    def do_deffnx(self, args):
        self.write('<DT>')
        words = splitwords(args, 2)
        [category, name], rest = words[:2], words[2:]
        self.expand('@b{%s}' % name)
        dla word w rest: self.expand(' ' + makevar(word))
        #self.expand(' -- ' + category)
        self.write('\n<DD>')
        self.index('fn', name)

    def bgn_defun(self, args): self.bgn_deffn('Function ' + args)
    end_defun = end_deffn
    def do_defunx(self, args): self.do_deffnx('Function ' + args)

    def bgn_defmac(self, args): self.bgn_deffn('Macro ' + args)
    end_defmac = end_deffn
    def do_defmacx(self, args): self.do_deffnx('Macro ' + args)

    def bgn_defspec(self, args): self.bgn_deffn('{Special Form} ' + args)
    end_defspec = end_deffn
    def do_defspecx(self, args): self.do_deffnx('{Special Form} ' + args)

    def bgn_defvr(self, args):
        self.write('<DL>')
        self.do_defvrx(args)

    end_defvr = end_deffn

    def do_defvrx(self, args):
        self.write('<DT>')
        words = splitwords(args, 2)
        [category, name], rest = words[:2], words[2:]
        self.expand('@code{%s}' % name)
        # If there are too many arguments, show them
        dla word w rest: self.expand(' ' + word)
        #self.expand(' -- ' + category)
        self.write('\n<DD>')
        self.index('vr', name)

    def bgn_defvar(self, args): self.bgn_defvr('Variable ' + args)
    end_defvar = end_defvr
    def do_defvarx(self, args): self.do_defvrx('Variable ' + args)

    def bgn_defopt(self, args): self.bgn_defvr('{User Option} ' + args)
    end_defopt = end_defvr
    def do_defoptx(self, args): self.do_defvrx('{User Option} ' + args)

    # --- Ditto dla typed languages ---

    def bgn_deftypefn(self, args):
        self.write('<DL>')
        self.do_deftypefnx(args)

    end_deftypefn = end_deffn

    def do_deftypefnx(self, args):
        self.write('<DT>')
        words = splitwords(args, 3)
        [category, datatype, name], rest = words[:3], words[3:]
        self.expand('@code{%s} @b{%s}' % (datatype, name))
        dla word w rest: self.expand(' ' + makevar(word))
        #self.expand(' -- ' + category)
        self.write('\n<DD>')
        self.index('fn', name)


    def bgn_deftypefun(self, args): self.bgn_deftypefn('Function ' + args)
    end_deftypefun = end_deftypefn
    def do_deftypefunx(self, args): self.do_deftypefnx('Function ' + args)

    def bgn_deftypevr(self, args):
        self.write('<DL>')
        self.do_deftypevrx(args)

    end_deftypevr = end_deftypefn

    def do_deftypevrx(self, args):
        self.write('<DT>')
        words = splitwords(args, 3)
        [category, datatype, name], rest = words[:3], words[3:]
        self.expand('@code{%s} @b{%s}' % (datatype, name))
        # If there are too many arguments, show them
        dla word w rest: self.expand(' ' + word)
        #self.expand(' -- ' + category)
        self.write('\n<DD>')
        self.index('fn', name)

    def bgn_deftypevar(self, args):
        self.bgn_deftypevr('Variable ' + args)
    end_deftypevar = end_deftypevr
    def do_deftypevarx(self, args):
        self.do_deftypevrx('Variable ' + args)

    # --- Ditto dla object-oriented languages ---

    def bgn_defcv(self, args):
        self.write('<DL>')
        self.do_defcvx(args)

    end_defcv = end_deftypevr

    def do_defcvx(self, args):
        self.write('<DT>')
        words = splitwords(args, 3)
        [category, classname, name], rest = words[:3], words[3:]
        self.expand('@b{%s}' % name)
        # If there are too many arguments, show them
        dla word w rest: self.expand(' ' + word)
        #self.expand(' -- %s of @code{%s}' % (category, classname))
        self.write('\n<DD>')
        self.index('vr', '%s @r{on %s}' % (name, classname))

    def bgn_defivar(self, args):
        self.bgn_defcv('{Instance Variable} ' + args)
    end_defivar = end_defcv
    def do_defivarx(self, args):
        self.do_defcvx('{Instance Variable} ' + args)

    def bgn_defop(self, args):
        self.write('<DL>')
        self.do_defopx(args)

    end_defop = end_defcv

    def do_defopx(self, args):
        self.write('<DT>')
        words = splitwords(args, 3)
        [category, classname, name], rest = words[:3], words[3:]
        self.expand('@b{%s}' % name)
        dla word w rest: self.expand(' ' + makevar(word))
        #self.expand(' -- %s of @code{%s}' % (category, classname))
        self.write('\n<DD>')
        self.index('fn', '%s @r{on %s}' % (name, classname))

    def bgn_defmethod(self, args):
        self.bgn_defop('Method ' + args)
    end_defmethod = end_defop
    def do_defmethodx(self, args):
        self.do_defopx('Method ' + args)

    # --- Ditto dla data types ---

    def bgn_deftp(self, args):
        self.write('<DL>')
        self.do_deftpx(args)

    end_deftp = end_defcv

    def do_deftpx(self, args):
        self.write('<DT>')
        words = splitwords(args, 2)
        [category, name], rest = words[:2], words[2:]
        self.expand('@b{%s}' % name)
        dla word w rest: self.expand(' ' + word)
        #self.expand(' -- ' + category)
        self.write('\n<DD>')
        self.index('tp', name)

    # --- Making Lists oraz Tables

    def bgn_enumerate(self, args):
        jeżeli nie args:
            self.write('<OL>\n')
            self.stackinfo[len(self.stack)] = '</OL>\n'
        inaczej:
            self.itemnumber = args
            self.write('<UL>\n')
            self.stackinfo[len(self.stack)] = '</UL>\n'
    def end_enumerate(self):
        self.itemnumber = Nic
        self.write(self.stackinfo[len(self.stack) + 1])
        usuń self.stackinfo[len(self.stack) + 1]

    def bgn_itemize(self, args):
        self.itemarg = args
        self.write('<UL>\n')
    def end_itemize(self):
        self.itemarg = Nic
        self.write('</UL>\n')

    def bgn_table(self, args):
        self.itemarg = args
        self.write('<DL>\n')
    def end_table(self):
        self.itemarg = Nic
        self.write('</DL>\n')

    def bgn_ftable(self, args):
        self.itemindex = 'fn'
        self.bgn_table(args)
    def end_ftable(self):
        self.itemindex = Nic
        self.end_table()

    def bgn_vtable(self, args):
        self.itemindex = 'vr'
        self.bgn_table(args)
    def end_vtable(self):
        self.itemindex = Nic
        self.end_table()

    def do_item(self, args):
        jeżeli self.itemindex: self.index(self.itemindex, args)
        jeżeli self.itemarg:
            jeżeli self.itemarg[0] == '@' oraz self.itemarg[1] oraz \
                            self.itemarg[1] w string.ascii_letters:
                args = self.itemarg + '{' + args + '}'
            inaczej:
                # some other character, e.g. '-'
                args = self.itemarg + ' ' + args
        jeżeli self.itemnumber jest nie Nic:
            args = self.itemnumber + '. ' + args
            self.itemnumber = increment(self.itemnumber)
        jeżeli self.stack oraz self.stack[-1] == 'table':
            self.write('<DT>')
            self.expand(args)
            self.write('\n<DD>')
        albo_inaczej self.stack oraz self.stack[-1] == 'multitable':
            self.write('<TR><TD>')
            self.expand(args)
            self.write('</TD>\n</TR>\n')
        inaczej:
            self.write('<LI>')
            self.expand(args)
            self.write('  ')
    do_itemx = do_item # XXX Should suppress leading blank line

    # rpyron 2002-05-07  multitable support
    def bgn_multitable(self, args):
        self.itemarg = Nic     # should be handled by columnfractions
        self.write('<TABLE BORDER="">\n')
    def end_multitable(self):
        self.itemarg = Nic
        self.write('</TABLE>\n<BR>\n')
    def handle_columnfractions(self):
        # It would be better to handle this, but dla now it's w the way...
        self.itemarg = Nic
    def handle_tab(self):
        self.write('</TD>\n    <TD>')

    # --- Enumerations, displays, quotations ---
    # XXX Most of these should increase the indentation somehow

    def bgn_quotation(self, args): self.write('<BLOCKQUOTE>')
    def end_quotation(self): self.write('</BLOCKQUOTE>\n')

    def bgn_example(self, args):
        self.nofill = self.nofill + 1
        self.write('<PRE>')
    def end_example(self):
        self.write('</PRE>\n')
        self.nofill = self.nofill - 1

    bgn_lisp = bgn_example # Synonym when contents are executable lisp code
    end_lisp = end_example

    bgn_smallexample = bgn_example # XXX Should use smaller font
    end_smallexample = end_example

    bgn_smalllisp = bgn_lisp # Ditto
    end_smalllisp = end_lisp

    bgn_display = bgn_example
    end_display = end_example

    bgn_format = bgn_display
    end_format = end_display

    def do_exdent(self, args): self.expand(args + '\n')
    # XXX Should really mess przy indentation

    def bgn_flushleft(self, args):
        self.nofill = self.nofill + 1
        self.write('<PRE>\n')
    def end_flushleft(self):
        self.write('</PRE>\n')
        self.nofill = self.nofill - 1

    def bgn_flushright(self, args):
        self.nofill = self.nofill + 1
        self.write('<ADDRESS COMPACT>\n')
    def end_flushright(self):
        self.write('</ADDRESS>\n')
        self.nofill = self.nofill - 1

    def bgn_menu(self, args):
        self.write('<DIR>\n')
        self.write('  <STRONG><EM>Menu</EM></STRONG><P>\n')
        self.htmlhelp.beginmenu()
    def end_menu(self):
        self.write('</DIR>\n')
        self.htmlhelp.endmenu()

    def bgn_cartouche(self, args): dalej
    def end_cartouche(self): dalej

    # --- Indices ---

    def resetindex(self):
        self.noncodeindices = ['cp']
        self.indextitle = {}
        self.indextitle['cp'] = 'Concept'
        self.indextitle['fn'] = 'Function'
        self.indextitle['ky'] = 'Keyword'
        self.indextitle['pg'] = 'Program'
        self.indextitle['tp'] = 'Type'
        self.indextitle['vr'] = 'Variable'
        #
        self.whichindex = {}
        dla name w self.indextitle:
            self.whichindex[name] = []

    def user_index(self, name, args):
        jeżeli name w self.whichindex:
            self.index(name, args)
        inaczej:
            print('*** No index named', repr(name))

    def do_cindex(self, args): self.index('cp', args)
    def do_findex(self, args): self.index('fn', args)
    def do_kindex(self, args): self.index('ky', args)
    def do_pindex(self, args): self.index('pg', args)
    def do_tindex(self, args): self.index('tp', args)
    def do_vindex(self, args): self.index('vr', args)

    def index(self, name, args):
        self.whichindex[name].append((args, self.nodename))
        self.htmlhelp.index(args, self.nodename)

    def do_synindex(self, args):
        words = args.split()
        jeżeli len(words) != 2:
            print('*** bad @synindex', args)
            zwróć
        [old, new] = words
        jeżeli old nie w self.whichindex albo \
                  new nie w self.whichindex:
            print('*** bad key(s) w @synindex', args)
            zwróć
        jeżeli old != new oraz \
                  self.whichindex[old] jest nie self.whichindex[new]:
            inew = self.whichindex[new]
            inew[len(inew):] = self.whichindex[old]
            self.whichindex[old] = inew
    do_syncodeindex = do_synindex # XXX Should use code font

    def do_printindex(self, args):
        words = args.split()
        dla name w words:
            jeżeli name w self.whichindex:
                self.prindex(name)
            inaczej:
                print('*** No index named', repr(name))

    def prindex(self, name):
        iscodeindex = (name nie w self.noncodeindices)
        index = self.whichindex[name]
        jeżeli nie index: zwróć
        jeżeli self.debugging:
            print('!'*self.debugging, '--- Generating', \
                  self.indextitle[name], 'index')
        #  The node already provides a title
        index1 = []
        junkprog = re.compile('^(@[a-z]+)?{')
        dla key, node w index:
            sortkey = key.lower()
            # Remove leading `@cmd{' z sort key
            # -- don't bother about the matching `}'
            oldsortkey = sortkey
            dopóki 1:
                mo = junkprog.match(sortkey)
                jeżeli nie mo:
                    przerwij
                i = mo.end()
                sortkey = sortkey[i:]
            index1.append((sortkey, key, node))
        usuń index[:]
        index1.sort()
        self.write('<DL COMPACT>\n')
        prevkey = prevnode = Nic
        dla sortkey, key, node w index1:
            jeżeli (key, node) == (prevkey, prevnode):
                kontynuuj
            jeżeli self.debugging > 1: print('!'*self.debugging, key, ':', node)
            self.write('<DT>')
            jeżeli iscodeindex: key = '@code{' + key + '}'
            jeżeli key != prevkey:
                self.expand(key)
            self.write('\n<DD><A HREF="%s">%s</A>\n' % (makefile(node), node))
            prevkey, prevnode = key, node
        self.write('</DL>\n')

    # --- Final error reports ---

    def report(self):
        jeżeli self.unknown:
            print('--- Unrecognized commands ---')
            cmds = sorted(self.unknown.keys())
            dla cmd w cmds:
                print(cmd.ljust(20), self.unknown[cmd])


klasa TexinfoParserHTML3(TexinfoParser):

    COPYRIGHT_SYMBOL = "&copy;"
    FN_ID_PATTERN = "[%(id)s]"
    FN_SOURCE_PATTERN = '<A ID=footnoteref%(id)s ' \
                        'HREF="#footnotetext%(id)s">' + FN_ID_PATTERN + '</A>'
    FN_TARGET_PATTERN = '<FN ID=footnotetext%(id)s>\n' \
                        '<P><A HREF="#footnoteref%(id)s">' + FN_ID_PATTERN \
                        + '</A>\n%(text)s</P></FN>\n'
    FN_HEADER = '<DIV CLASS=footnotes>\n  <HR NOSHADE WIDTH=200>\n' \
                '  <STRONG><EM>Footnotes</EM></STRONG>\n  <P>\n'

    Node = HTML3Node

    def bgn_quotation(self, args): self.write('<BQ>')
    def end_quotation(self): self.write('</BQ>\n')

    def bgn_example(self, args):
        # this use of <CODE> would nie be legal w HTML 2.0,
        # but jest w more recent DTDs.
        self.nofill = self.nofill + 1
        self.write('<PRE CLASS=example><CODE>')
    def end_example(self):
        self.write("</CODE></PRE>\n")
        self.nofill = self.nofill - 1

    def bgn_flushleft(self, args):
        self.nofill = self.nofill + 1
        self.write('<PRE CLASS=flushleft>\n')

    def bgn_flushright(self, args):
        self.nofill = self.nofill + 1
        self.write('<DIV ALIGN=right CLASS=flushright><ADDRESS COMPACT>\n')
    def end_flushright(self):
        self.write('</ADDRESS></DIV>\n')
        self.nofill = self.nofill - 1

    def bgn_menu(self, args):
        self.write('<UL PLAIN CLASS=menu>\n')
        self.write('  <LH>Menu</LH>\n')
    def end_menu(self):
        self.write('</UL>\n')


# rpyron 2002-05-07
klasa HTMLHelp:
    """
    This klasa encapsulates support dla HTML Help. Node names,
    file names, menu items, index items, oraz image file names are
    accumulated until a call to finalize(). At that time, three
    output files are created w the current directory:

        `helpbase`.hhp  jest a HTML Help Workshop project file.
                        It contains various information, some of
                        which I do nie understand; I just copied
                        the default project info z a fresh
                        installation.
        `helpbase`.hhc  jest the Contents file dla the project.
        `helpbase`.hhk  jest the Index file dla the project.

    When these files are used jako input to HTML Help Workshop,
    the resulting file will be named:

        `helpbase`.chm

    If none of the defaults w `helpbase`.hhp are changed,
    the .CHM file will have Contents, Index, Search, oraz
    Favorites tabs.
    """

    codeprog = re.compile('@code{(.*?)}')

    def __init__(self,helpbase,dirname):
        self.helpbase    = helpbase
        self.dirname     = dirname
        self.projectfile = Nic
        self.contentfile = Nic
        self.indexfile   = Nic
        self.nodelist    = []
        self.nodenames   = {}         # nodename : index
        self.nodeindex   = {}
        self.filenames   = {}         # filename : filename
        self.indexlist   = []         # (args,nodename) == (key,location)
        self.current     = ''
        self.menudict    = {}
        self.dumped      = {}


    def addnode(self,name,next,prev,up,filename):
        node = (name,next,prev,up,filename)
        # add this file to dict
        # retrieve list przy self.filenames.values()
        self.filenames[filename] = filename
        # add this node to nodelist
        self.nodeindex[name] = len(self.nodelist)
        self.nodelist.append(node)
        # set 'current' dla menu items
        self.current = name
        self.menudict[self.current] = []

    def menuitem(self,nodename):
        menu = self.menudict[self.current]
        menu.append(nodename)


    def addimage(self,imagename):
        self.filenames[imagename] = imagename

    def index(self, args, nodename):
        self.indexlist.append((args,nodename))

    def beginmenu(self):
        dalej

    def endmenu(self):
        dalej

    def finalize(self):
        jeżeli nie self.helpbase:
            zwróć

        # generate interesting filenames
        resultfile   = self.helpbase + '.chm'
        projectfile  = self.helpbase + '.hhp'
        contentfile  = self.helpbase + '.hhc'
        indexfile    = self.helpbase + '.hhk'

        # generate a reasonable title
        title        = self.helpbase

        # get the default topic file
        (topname,topnext,topprev,topup,topfile) = self.nodelist[0]
        defaulttopic = topfile

        # PROJECT FILE
        spróbuj:
            fp = open(projectfile,'w')
            print('[OPTIONS]', file=fp)
            print('Auto Index=Yes', file=fp)
            print('Binary TOC=No', file=fp)
            print('Binary Index=Yes', file=fp)
            print('Compatibility=1.1', file=fp)
            print('Compiled file=' + resultfile + '', file=fp)
            print('Contents file=' + contentfile + '', file=fp)
            print('Default topic=' + defaulttopic + '', file=fp)
            print('Error log file=ErrorLog.log', file=fp)
            print('Index file=' + indexfile + '', file=fp)
            print('Title=' + title + '', file=fp)
            print('Display compile progress=Yes', file=fp)
            print('Full-text search=Yes', file=fp)
            print('Default window=main', file=fp)
            print('', file=fp)
            print('[WINDOWS]', file=fp)
            print('main=,"' + contentfile + '","' + indexfile
                        + '","","",,,,,0x23520,222,0x1046,[10,10,780,560],'
                        '0xB0000,,,,,,0', file=fp)
            print('', file=fp)
            print('[FILES]', file=fp)
            print('', file=fp)
            self.dumpfiles(fp)
            fp.close()
        wyjąwszy IOError jako msg:
            print(projectfile, ':', msg)
            sys.exit(1)

        # CONTENT FILE
        spróbuj:
            fp = open(contentfile,'w')
            print('<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">', file=fp)
            print('<!-- This file defines the table of contents -->', file=fp)
            print('<HTML>', file=fp)
            print('<HEAD>', file=fp)
            print('<meta name="GENERATOR"'
                        'content="Microsoft&reg; HTML Help Workshop 4.1">', file=fp)
            print('<!-- Sitemap 1.0 -->', file=fp)
            print('</HEAD>', file=fp)
            print('<BODY>', file=fp)
            print('   <OBJECT type="text/site properties">', file=fp)
            print('     <param name="Window Styles" value="0x800025">', file=fp)
            print('     <param name="comment" value="title:">', file=fp)
            print('     <param name="comment" value="base:">', file=fp)
            print('   </OBJECT>', file=fp)
            self.dumpnodes(fp)
            print('</BODY>', file=fp)
            print('</HTML>', file=fp)
            fp.close()
        wyjąwszy IOError jako msg:
            print(contentfile, ':', msg)
            sys.exit(1)

        # INDEX FILE
        spróbuj:
            fp = open(indexfile  ,'w')
            print('<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">', file=fp)
            print('<!-- This file defines the index -->', file=fp)
            print('<HTML>', file=fp)
            print('<HEAD>', file=fp)
            print('<meta name="GENERATOR"'
                        'content="Microsoft&reg; HTML Help Workshop 4.1">', file=fp)
            print('<!-- Sitemap 1.0 -->', file=fp)
            print('</HEAD>', file=fp)
            print('<BODY>', file=fp)
            print('<OBJECT type="text/site properties">', file=fp)
            print('</OBJECT>', file=fp)
            self.dumpindex(fp)
            print('</BODY>', file=fp)
            print('</HTML>', file=fp)
            fp.close()
        wyjąwszy IOError jako msg:
            print(indexfile  , ':', msg)
            sys.exit(1)

    def dumpfiles(self, outfile=sys.stdout):
        filelist = sorted(self.filenames.values())
        dla filename w filelist:
            print(filename, file=outfile)

    def dumpnodes(self, outfile=sys.stdout):
        self.dumped = {}
        jeżeli self.nodelist:
            nodename, dummy, dummy, dummy, dummy = self.nodelist[0]
            self.topnode = nodename

        print('<UL>', file=outfile)
        dla node w self.nodelist:
            self.dumpnode(node,0,outfile)
        print('</UL>', file=outfile)

    def dumpnode(self, node, indent=0, outfile=sys.stdout):
        jeżeli node:
            # Retrieve info dla this node
            (nodename,next,prev,up,filename) = node
            self.current = nodename

            # Have we been dumped already?
            jeżeli nodename w self.dumped:
                zwróć
            self.dumped[nodename] = 1

            # Print info dla this node
            print(' '*indent, end=' ', file=outfile)
            print('<LI><OBJECT type="text/sitemap">', end=' ', file=outfile)
            print('<param name="Name" value="' + nodename +'">', end=' ', file=outfile)
            print('<param name="Local" value="'+ filename +'">', end=' ', file=outfile)
            print('</OBJECT>', file=outfile)

            # Does this node have menu items?
            spróbuj:
                menu = self.menudict[nodename]
                self.dumpmenu(menu,indent+2,outfile)
            wyjąwszy KeyError:
                dalej

    def dumpmenu(self, menu, indent=0, outfile=sys.stdout):
        jeżeli menu:
            currentnode = self.current
            jeżeli currentnode != self.topnode:    # XXX this jest a hack
                print(' '*indent + '<UL>', file=outfile)
                indent += 2
            dla item w menu:
                menunode = self.getnode(item)
                self.dumpnode(menunode,indent,outfile)
            jeżeli currentnode != self.topnode:    # XXX this jest a hack
                print(' '*indent + '</UL>', file=outfile)
                indent -= 2

    def getnode(self, nodename):
        spróbuj:
            index = self.nodeindex[nodename]
            zwróć self.nodelist[index]
        wyjąwszy KeyError:
            zwróć Nic
        wyjąwszy IndexError:
            zwróć Nic

    # (args,nodename) == (key,location)
    def dumpindex(self, outfile=sys.stdout):
        print('<UL>', file=outfile)
        dla (key,location) w self.indexlist:
            key = self.codeexpand(key)
            location = makefile(location)
            location = self.dirname + '/' + location
            print('<LI><OBJECT type="text/sitemap">', end=' ', file=outfile)
            print('<param name="Name" value="' + key + '">', end=' ', file=outfile)
            print('<param name="Local" value="' + location + '">', end=' ', file=outfile)
            print('</OBJECT>', file=outfile)
        print('</UL>', file=outfile)

    def codeexpand(self, line):
        co = self.codeprog.match(line)
        jeżeli nie co:
            zwróć line
        bgn, end = co.span(0)
        a, b = co.span(1)
        line = line[:bgn] + line[a:b] + line[end:]
        zwróć line


# Put @var{} around alphabetic substrings
def makevar(str):
    zwróć '@var{'+str+'}'


# Split a string w "words" according to findwordend
def splitwords(str, minlength):
    words = []
    i = 0
    n = len(str)
    dopóki i < n:
        dopóki i < n oraz str[i] w ' \t\n': i = i+1
        jeżeli i >= n: przerwij
        start = i
        i = findwordend(str, i, n)
        words.append(str[start:i])
    dopóki len(words) < minlength: words.append('')
    zwróć words


# Find the end of a "word", matching braces oraz interpreting @@ @{ @}
fwprog = re.compile('[@{} ]')
def findwordend(str, i, n):
    level = 0
    dopóki i < n:
        mo = fwprog.search(str, i)
        jeżeli nie mo:
            przerwij
        i = mo.start()
        c = str[i]; i = i+1
        jeżeli c == '@': i = i+1 # Next character jest nie special
        albo_inaczej c == '{': level = level+1
        albo_inaczej c == '}': level = level-1
        albo_inaczej c == ' ' oraz level <= 0: zwróć i-1
    zwróć n


# Convert a node name into a file name
def makefile(nodename):
    nodename = nodename.strip()
    zwróć fixfunnychars(nodename) + '.html'


# Characters that are perfectly safe w filenames oraz hyperlinks
goodchars = string.ascii_letters + string.digits + '!@-=+.'

# Replace characters that aren't perfectly safe by dashes
# Underscores are bad since Cern HTTPD treats them jako delimiters for
# encoding times, so you get mismatches jeżeli you compress your files:
# a.html.gz will map to a_b.html.gz
def fixfunnychars(addr):
    i = 0
    dopóki i < len(addr):
        c = addr[i]
        jeżeli c nie w goodchars:
            c = '-'
            addr = addr[:i] + c + addr[i+1:]
        i = i + len(c)
    zwróć addr


# Increment a string used jako an enumeration
def increment(s):
    jeżeli nie s:
        zwróć '1'
    dla sequence w string.digits, string.ascii_lowercase, string.ascii_uppercase:
        lastc = s[-1]
        jeżeli lastc w sequence:
            i = sequence.index(lastc) + 1
            jeżeli i >= len(sequence):
                jeżeli len(s) == 1:
                    s = sequence[0]*2
                    jeżeli s == '00':
                        s = '10'
                inaczej:
                    s = increment(s[:-1]) + sequence[0]
            inaczej:
                s = s[:-1] + sequence[i]
            zwróć s
    zwróć s # Don't increment


def test():
    zaimportuj sys
    debugging = 0
    print_headers = 0
    cont = 0
    html3 = 0
    htmlhelp = ''

    dopóki sys.argv[1] == ['-d']:
        debugging = debugging + 1
        usuń sys.argv[1]
    jeżeli sys.argv[1] == '-p':
        print_headers = 1
        usuń sys.argv[1]
    jeżeli sys.argv[1] == '-c':
        cont = 1
        usuń sys.argv[1]
    jeżeli sys.argv[1] == '-3':
        html3 = 1
        usuń sys.argv[1]
    jeżeli sys.argv[1] == '-H':
        helpbase = sys.argv[2]
        usuń sys.argv[1:3]
    jeżeli len(sys.argv) != 3:
        print('usage: texi2hh [-d [-d]] [-p] [-c] [-3] [-H htmlhelp]', \
              'inputfile outputdirectory')
        sys.exit(2)

    jeżeli html3:
        parser = TexinfoParserHTML3()
    inaczej:
        parser = TexinfoParser()
    parser.cont = cont
    parser.debugging = debugging
    parser.print_headers = print_headers

    file = sys.argv[1]
    dirname  = sys.argv[2]
    parser.setdirname(dirname)
    parser.setincludedir(os.path.dirname(file))

    htmlhelp = HTMLHelp(helpbase, dirname)
    parser.sethtmlhelp(htmlhelp)

    spróbuj:
        fp = open(file, 'r')
    wyjąwszy IOError jako msg:
        print(file, ':', msg)
        sys.exit(1)

    parser.parse(fp)
    fp.close()
    parser.report()

    htmlhelp.finalize()


jeżeli __name__ == "__main__":
    test()
