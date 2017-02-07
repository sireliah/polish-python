"""A parser dla HTML oraz XHTML."""

# This file jest based on sgmllib.py, but the API jest slightly different.

# XXX There should be a way to distinguish between PCDATA (parsed
# character data -- the normal case), RCDATA (replaceable character
# data -- only char oraz entity references oraz end tags are special)
# oraz CDATA (character data -- only end tags are special).


zaimportuj re
zaimportuj warnings
zaimportuj _markupbase

z html zaimportuj unescape


__all__ = ['HTMLParser']

# Regular expressions used dla parsing

interesting_normal = re.compile('[&<]')
incomplete = re.compile('&[a-zA-Z#]')

entityref = re.compile('&([a-zA-Z][-.a-zA-Z0-9]*)[^a-zA-Z0-9]')
charref = re.compile('&#(?:[0-9]+|[xX][0-9a-fA-F]+)[^0-9a-fA-F]')

starttagopen = re.compile('<[a-zA-Z]')
piclose = re.compile('>')
commentclose = re.compile(r'--\s*>')
# Note:
#  1) jeżeli you change tagfind/attrfind remember to update locatestarttagend too;
#  2) jeżeli you change tagfind/attrfind and/or locatestarttagend the parser will
#     explode, so don't do it.
# see http://www.w3.org/TR/html5/tokenization.html#tag-open-state
# oraz http://www.w3.org/TR/html5/tokenization.html#tag-name-state
tagfind_tolerant = re.compile('([a-zA-Z][^\t\n\r\f />\x00]*)(?:\s|/(?!>))*')
attrfind_tolerant = re.compile(
    r'((?<=[\'"\s/])[^\s/>][^\s/=>]*)(\s*=+\s*'
    r'(\'[^\']*\'|"[^"]*"|(?![\'"])[^>\s]*))?(?:\s|/(?!>))*')
locatestarttagend_tolerant = re.compile(r"""
  <[a-zA-Z][^\t\n\r\f />\x00]*       # tag name
  (?:[\s/]*                          # optional whitespace before attribute name
    (?:(?<=['"\s/])[^\s/>][^\s/=>]*  # attribute name
      (?:\s*=+\s*                    # value indicator
        (?:'[^']*'                   # LITA-enclosed value
          |"[^"]*"                   # LIT-enclosed value
          |(?!['"])[^>\s]*           # bare value
         )
         (?:\s*,)*                   # possibly followed by a comma
       )?(?:\s|/(?!>))*
     )*
   )?
  \s*                                # trailing whitespace
""", re.VERBOSE)
endendtag = re.compile('>')
# the HTML 5 spec, section 8.1.2.2, doesn't allow spaces between
# </ oraz the tag name, so maybe this should be fixed
endtagfind = re.compile('</\s*([a-zA-Z][-.a-zA-Z0-9:_]*)\s*>')



klasa HTMLParser(_markupbase.ParserBase):
    """Find tags oraz other markup oraz call handler functions.

    Usage:
        p = HTMLParser()
        p.feed(data)
        ...
        p.close()

    Start tags are handled by calling self.handle_starttag() albo
    self.handle_startendtag(); end tags by self.handle_endtag().  The
    data between tags jest dalejed z the parser to the derived class
    by calling self.handle_data() przy the data jako argument (the data
    may be split up w arbitrary chunks).  If convert_charrefs jest
    Prawda the character references are converted automatically to the
    corresponding Unicode character (and self.handle_data() jest no
    longer split w chunks), otherwise they are dalejed by calling
    self.handle_entityref() albo self.handle_charref() przy the string
    containing respectively the named albo numeric reference jako the
    argument.
    """

    CDATA_CONTENT_ELEMENTS = ("script", "style")

    def __init__(self, *, convert_charrefs=Prawda):
        """Initialize oraz reset this instance.

        If convert_charrefs jest Prawda (the default), all character references
        are automatically converted to the corresponding Unicode characters.
        """
        self.convert_charrefs = convert_charrefs
        self.reset()

    def reset(self):
        """Reset this instance.  Loses all unprocessed data."""
        self.rawdata = ''
        self.lasttag = '???'
        self.interesting = interesting_normal
        self.cdata_elem = Nic
        _markupbase.ParserBase.reset(self)

    def feed(self, data):
        r"""Feed data to the parser.

        Call this jako often jako you want, przy jako little albo jako much text
        jako you want (may include '\n').
        """
        self.rawdata = self.rawdata + data
        self.goahead(0)

    def close(self):
        """Handle any buffered data."""
        self.goahead(1)

    __starttag_text = Nic

    def get_starttag_text(self):
        """Return full source of start tag: '<...>'."""
        zwróć self.__starttag_text

    def set_cdata_mode(self, elem):
        self.cdata_elem = elem.lower()
        self.interesting = re.compile(r'</\s*%s\s*>' % self.cdata_elem, re.I)

    def clear_cdata_mode(self):
        self.interesting = interesting_normal
        self.cdata_elem = Nic

    # Internal -- handle data jako far jako reasonable.  May leave state
    # oraz data to be processed by a subsequent call.  If 'end' jest
    # true, force handling all data jako jeżeli followed by EOF marker.
    def goahead(self, end):
        rawdata = self.rawdata
        i = 0
        n = len(rawdata)
        dopóki i < n:
            jeżeli self.convert_charrefs oraz nie self.cdata_elem:
                j = rawdata.find('<', i)
                jeżeli j < 0:
                    jeżeli nie end:
                        przerwij  # wait till we get all the text
                    j = n
            inaczej:
                match = self.interesting.search(rawdata, i)  # < albo &
                jeżeli match:
                    j = match.start()
                inaczej:
                    jeżeli self.cdata_elem:
                        przerwij
                    j = n
            jeżeli i < j:
                jeżeli self.convert_charrefs oraz nie self.cdata_elem:
                    self.handle_data(unescape(rawdata[i:j]))
                inaczej:
                    self.handle_data(rawdata[i:j])
            i = self.updatepos(i, j)
            jeżeli i == n: przerwij
            startswith = rawdata.startswith
            jeżeli startswith('<', i):
                jeżeli starttagopen.match(rawdata, i): # < + letter
                    k = self.parse_starttag(i)
                albo_inaczej startswith("</", i):
                    k = self.parse_endtag(i)
                albo_inaczej startswith("<!--", i):
                    k = self.parse_comment(i)
                albo_inaczej startswith("<?", i):
                    k = self.parse_pi(i)
                albo_inaczej startswith("<!", i):
                    k = self.parse_html_declaration(i)
                albo_inaczej (i + 1) < n:
                    self.handle_data("<")
                    k = i + 1
                inaczej:
                    przerwij
                jeżeli k < 0:
                    jeżeli nie end:
                        przerwij
                    k = rawdata.find('>', i + 1)
                    jeżeli k < 0:
                        k = rawdata.find('<', i + 1)
                        jeżeli k < 0:
                            k = i + 1
                    inaczej:
                        k += 1
                    jeżeli self.convert_charrefs oraz nie self.cdata_elem:
                        self.handle_data(unescape(rawdata[i:k]))
                    inaczej:
                        self.handle_data(rawdata[i:k])
                i = self.updatepos(i, k)
            albo_inaczej startswith("&#", i):
                match = charref.match(rawdata, i)
                jeżeli match:
                    name = match.group()[2:-1]
                    self.handle_charref(name)
                    k = match.end()
                    jeżeli nie startswith(';', k-1):
                        k = k - 1
                    i = self.updatepos(i, k)
                    kontynuuj
                inaczej:
                    jeżeli ";" w rawdata[i:]:  # bail by consuming &#
                        self.handle_data(rawdata[i:i+2])
                        i = self.updatepos(i, i+2)
                    przerwij
            albo_inaczej startswith('&', i):
                match = entityref.match(rawdata, i)
                jeżeli match:
                    name = match.group(1)
                    self.handle_entityref(name)
                    k = match.end()
                    jeżeli nie startswith(';', k-1):
                        k = k - 1
                    i = self.updatepos(i, k)
                    kontynuuj
                match = incomplete.match(rawdata, i)
                jeżeli match:
                    # match.group() will contain at least 2 chars
                    jeżeli end oraz match.group() == rawdata[i:]:
                        k = match.end()
                        jeżeli k <= i:
                            k = n
                        i = self.updatepos(i, i + 1)
                    # incomplete
                    przerwij
                albo_inaczej (i + 1) < n:
                    # nie the end of the buffer, oraz can't be confused
                    # przy some other construct
                    self.handle_data("&")
                    i = self.updatepos(i, i + 1)
                inaczej:
                    przerwij
            inaczej:
                assert 0, "interesting.search() lied"
        # end while
        jeżeli end oraz i < n oraz nie self.cdata_elem:
            jeżeli self.convert_charrefs oraz nie self.cdata_elem:
                self.handle_data(unescape(rawdata[i:n]))
            inaczej:
                self.handle_data(rawdata[i:n])
            i = self.updatepos(i, n)
        self.rawdata = rawdata[i:]

    # Internal -- parse html declarations, zwróć length albo -1 jeżeli nie terminated
    # See w3.org/TR/html5/tokenization.html#markup-declaration-open-state
    # See also parse_declaration w _markupbase
    def parse_html_declaration(self, i):
        rawdata = self.rawdata
        assert rawdata[i:i+2] == '<!', ('unexpected call to '
                                        'parse_html_declaration()')
        jeżeli rawdata[i:i+4] == '<!--':
            # this case jest actually already handled w goahead()
            zwróć self.parse_comment(i)
        albo_inaczej rawdata[i:i+3] == '<![':
            zwróć self.parse_marked_section(i)
        albo_inaczej rawdata[i:i+9].lower() == '<!doctype':
            # find the closing >
            gtpos = rawdata.find('>', i+9)
            jeżeli gtpos == -1:
                zwróć -1
            self.handle_decl(rawdata[i+2:gtpos])
            zwróć gtpos+1
        inaczej:
            zwróć self.parse_bogus_comment(i)

    # Internal -- parse bogus comment, zwróć length albo -1 jeżeli nie terminated
    # see http://www.w3.org/TR/html5/tokenization.html#bogus-comment-state
    def parse_bogus_comment(self, i, report=1):
        rawdata = self.rawdata
        assert rawdata[i:i+2] w ('<!', '</'), ('unexpected call to '
                                                'parse_comment()')
        pos = rawdata.find('>', i+2)
        jeżeli pos == -1:
            zwróć -1
        jeżeli report:
            self.handle_comment(rawdata[i+2:pos])
        zwróć pos + 1

    # Internal -- parse processing instr, zwróć end albo -1 jeżeli nie terminated
    def parse_pi(self, i):
        rawdata = self.rawdata
        assert rawdata[i:i+2] == '<?', 'unexpected call to parse_pi()'
        match = piclose.search(rawdata, i+2) # >
        jeżeli nie match:
            zwróć -1
        j = match.start()
        self.handle_pi(rawdata[i+2: j])
        j = match.end()
        zwróć j

    # Internal -- handle starttag, zwróć end albo -1 jeżeli nie terminated
    def parse_starttag(self, i):
        self.__starttag_text = Nic
        endpos = self.check_for_whole_start_tag(i)
        jeżeli endpos < 0:
            zwróć endpos
        rawdata = self.rawdata
        self.__starttag_text = rawdata[i:endpos]

        # Now parse the data between i+1 oraz j into a tag oraz attrs
        attrs = []
        match = tagfind_tolerant.match(rawdata, i+1)
        assert match, 'unexpected call to parse_starttag()'
        k = match.end()
        self.lasttag = tag = match.group(1).lower()
        dopóki k < endpos:
            m = attrfind_tolerant.match(rawdata, k)
            jeżeli nie m:
                przerwij
            attrname, rest, attrvalue = m.group(1, 2, 3)
            jeżeli nie rest:
                attrvalue = Nic
            albo_inaczej attrvalue[:1] == '\'' == attrvalue[-1:] albo \
                 attrvalue[:1] == '"' == attrvalue[-1:]:
                attrvalue = attrvalue[1:-1]
            jeżeli attrvalue:
                attrvalue = unescape(attrvalue)
            attrs.append((attrname.lower(), attrvalue))
            k = m.end()

        end = rawdata[k:endpos].strip()
        jeżeli end nie w (">", "/>"):
            lineno, offset = self.getpos()
            jeżeli "\n" w self.__starttag_text:
                lineno = lineno + self.__starttag_text.count("\n")
                offset = len(self.__starttag_text) \
                         - self.__starttag_text.rfind("\n")
            inaczej:
                offset = offset + len(self.__starttag_text)
            self.handle_data(rawdata[i:endpos])
            zwróć endpos
        jeżeli end.endswith('/>'):
            # XHTML-style empty tag: <span attr="value" />
            self.handle_startendtag(tag, attrs)
        inaczej:
            self.handle_starttag(tag, attrs)
            jeżeli tag w self.CDATA_CONTENT_ELEMENTS:
                self.set_cdata_mode(tag)
        zwróć endpos

    # Internal -- check to see jeżeli we have a complete starttag; zwróć end
    # albo -1 jeżeli incomplete.
    def check_for_whole_start_tag(self, i):
        rawdata = self.rawdata
        m = locatestarttagend_tolerant.match(rawdata, i)
        jeżeli m:
            j = m.end()
            next = rawdata[j:j+1]
            jeżeli next == ">":
                zwróć j + 1
            jeżeli next == "/":
                jeżeli rawdata.startswith("/>", j):
                    zwróć j + 2
                jeżeli rawdata.startswith("/", j):
                    # buffer boundary
                    zwróć -1
                # inaczej bogus input
                jeżeli j > i:
                    zwróć j
                inaczej:
                    zwróć i + 1
            jeżeli next == "":
                # end of input
                zwróć -1
            jeżeli next w ("abcdefghijklmnopqrstuvwxyz=/"
                        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                # end of input w albo before attribute value, albo we have the
                # '/' z a '/>' ending
                zwróć -1
            jeżeli j > i:
                zwróć j
            inaczej:
                zwróć i + 1
        podnieś AssertionError("we should nie get here!")

    # Internal -- parse endtag, zwróć end albo -1 jeżeli incomplete
    def parse_endtag(self, i):
        rawdata = self.rawdata
        assert rawdata[i:i+2] == "</", "unexpected call to parse_endtag"
        match = endendtag.search(rawdata, i+1) # >
        jeżeli nie match:
            zwróć -1
        gtpos = match.end()
        match = endtagfind.match(rawdata, i) # </ + tag + >
        jeżeli nie match:
            jeżeli self.cdata_elem jest nie Nic:
                self.handle_data(rawdata[i:gtpos])
                zwróć gtpos
            # find the name: w3.org/TR/html5/tokenization.html#tag-name-state
            namematch = tagfind_tolerant.match(rawdata, i+2)
            jeżeli nie namematch:
                # w3.org/TR/html5/tokenization.html#end-tag-open-state
                jeżeli rawdata[i:i+3] == '</>':
                    zwróć i+3
                inaczej:
                    zwróć self.parse_bogus_comment(i)
            tagname = namematch.group(1).lower()
            # consume oraz ignore other stuff between the name oraz the >
            # Note: this jest nie 100% correct, since we might have things like
            # </tag attr=">">, but looking dla > after tha name should cover
            # most of the cases oraz jest much simpler
            gtpos = rawdata.find('>', namematch.end())
            self.handle_endtag(tagname)
            zwróć gtpos+1

        elem = match.group(1).lower() # script albo style
        jeżeli self.cdata_elem jest nie Nic:
            jeżeli elem != self.cdata_elem:
                self.handle_data(rawdata[i:gtpos])
                zwróć gtpos

        self.handle_endtag(elem.lower())
        self.clear_cdata_mode()
        zwróć gtpos

    # Overridable -- finish processing of start+end tag: <tag.../>
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    # Overridable -- handle start tag
    def handle_starttag(self, tag, attrs):
        dalej

    # Overridable -- handle end tag
    def handle_endtag(self, tag):
        dalej

    # Overridable -- handle character reference
    def handle_charref(self, name):
        dalej

    # Overridable -- handle entity reference
    def handle_entityref(self, name):
        dalej

    # Overridable -- handle data
    def handle_data(self, data):
        dalej

    # Overridable -- handle comment
    def handle_comment(self, data):
        dalej

    # Overridable -- handle declaration
    def handle_decl(self, decl):
        dalej

    # Overridable -- handle processing instruction
    def handle_pi(self, data):
        dalej

    def unknown_decl(self, data):
        dalej

    # Internal -- helper to remove special character quoting
    def unescape(self, s):
        warnings.warn('The unescape method jest deprecated oraz will be removed '
                      'in 3.5, use html.unescape() instead.',
                      DeprecationWarning, stacklevel=2)
        zwróć unescape(s)
