"""Shared support dla scanning document type declarations w HTML oraz XHTML.

This module jest used jako a foundation dla the html.parser module.  It has no
documented public API oraz should nie be used directly.

"""

zaimportuj re

_declname_match = re.compile(r'[a-zA-Z][-_.a-zA-Z0-9]*\s*').match
_declstringlit_match = re.compile(r'(\'[^\']*\'|"[^"]*")\s*').match
_commentclose = re.compile(r'--\s*>')
_markedsectionclose = re.compile(r']\s*]\s*>')

# An analysis of the MS-Word extensions jest available at
# http://www.planetpublish.com/xmlarena/xap/Thursday/WordtoXML.pdf

_msmarkedsectionclose = re.compile(r']\s*>')

usuń re


klasa ParserBase:
    """Parser base klasa which provides some common support methods used
    by the SGML/HTML oraz XHTML parsers."""

    def __init__(self):
        jeżeli self.__class__ jest ParserBase:
            podnieś RuntimeError(
                "_markupbase.ParserBase must be subclassed")

    def error(self, message):
        podnieś NotImplementedError(
            "subclasses of ParserBase must override error()")

    def reset(self):
        self.lineno = 1
        self.offset = 0

    def getpos(self):
        """Return current line number oraz offset."""
        zwróć self.lineno, self.offset

    # Internal -- update line number oraz offset.  This should be
    # called dla each piece of data exactly once, w order -- w other
    # words the concatenation of all the input strings to this
    # function should be exactly the entire input.
    def updatepos(self, i, j):
        jeżeli i >= j:
            zwróć j
        rawdata = self.rawdata
        nlines = rawdata.count("\n", i, j)
        jeżeli nlines:
            self.lineno = self.lineno + nlines
            pos = rawdata.rindex("\n", i, j) # Should nie fail
            self.offset = j-(pos+1)
        inaczej:
            self.offset = self.offset + j-i
        zwróć j

    _decl_otherchars = ''

    # Internal -- parse declaration (dla use by subclasses).
    def parse_declaration(self, i):
        # This jest some sort of declaration; w "HTML as
        # deployed," this should only be the document type
        # declaration ("<!DOCTYPE html...>").
        # ISO 8879:1986, however, has more complex
        # declaration syntax dla elements w <!...>, including:
        # --comment--
        # [marked section]
        # name w the following list: ENTITY, DOCTYPE, ELEMENT,
        # ATTLIST, NOTATION, SHORTREF, USEMAP,
        # LINKTYPE, LINK, IDLINK, USELINK, SYSTEM
        rawdata = self.rawdata
        j = i + 2
        assert rawdata[i:j] == "<!", "unexpected call to parse_declaration"
        jeżeli rawdata[j:j+1] == ">":
            # the empty comment <!>
            zwróć j + 1
        jeżeli rawdata[j:j+1] w ("-", ""):
            # Start of comment followed by buffer boundary,
            # albo just a buffer boundary.
            zwróć -1
        # A simple, practical version could look like: ((name|stringlit) S*) + '>'
        n = len(rawdata)
        jeżeli rawdata[j:j+2] == '--': #comment
            # Locate --.*-- jako the body of the comment
            zwróć self.parse_comment(i)
        albo_inaczej rawdata[j] == '[': #marked section
            # Locate [statusWord [...arbitrary SGML...]] jako the body of the marked section
            # Where statusWord jest one of TEMP, CDATA, IGNORE, INCLUDE, RCDATA
            # Note that this jest extended by Microsoft Office "Save jako Web" function
            # to include [if...] oraz [endif].
            zwróć self.parse_marked_section(i)
        inaczej: #all other declaration elements
            decltype, j = self._scan_name(j, i)
        jeżeli j < 0:
            zwróć j
        jeżeli decltype == "doctype":
            self._decl_otherchars = ''
        dopóki j < n:
            c = rawdata[j]
            jeżeli c == ">":
                # end of declaration syntax
                data = rawdata[i+2:j]
                jeżeli decltype == "doctype":
                    self.handle_decl(data)
                inaczej:
                    # According to the HTML5 specs sections "8.2.4.44 Bogus
                    # comment state" oraz "8.2.4.45 Markup declaration open
                    # state", a comment token should be emitted.
                    # Calling unknown_decl provides more flexibility though.
                    self.unknown_decl(data)
                zwróć j + 1
            jeżeli c w "\"'":
                m = _declstringlit_match(rawdata, j)
                jeżeli nie m:
                    zwróć -1 # incomplete
                j = m.end()
            albo_inaczej c w "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
                name, j = self._scan_name(j, i)
            albo_inaczej c w self._decl_otherchars:
                j = j + 1
            albo_inaczej c == "[":
                # this could be handled w a separate doctype parser
                jeżeli decltype == "doctype":
                    j = self._parse_doctype_subset(j + 1, i)
                albo_inaczej decltype w {"attlist", "linktype", "link", "element"}:
                    # must tolerate []'d groups w a content mousuń w an element declaration
                    # also w data attribute specifications of attlist declaration
                    # also link type declaration subsets w linktype declarations
                    # also link attribute specification lists w link declarations
                    self.error("unsupported '[' char w %s declaration" % decltype)
                inaczej:
                    self.error("unexpected '[' char w declaration")
            inaczej:
                self.error(
                    "unexpected %r char w declaration" % rawdata[j])
            jeżeli j < 0:
                zwróć j
        zwróć -1 # incomplete

    # Internal -- parse a marked section
    # Override this to handle MS-word extension syntax <![jeżeli word]>content<![endif]>
    def parse_marked_section(self, i, report=1):
        rawdata= self.rawdata
        assert rawdata[i:i+3] == '<![', "unexpected call to parse_marked_section()"
        sectName, j = self._scan_name( i+3, i )
        jeżeli j < 0:
            zwróć j
        jeżeli sectName w {"temp", "cdata", "ignore", "include", "rcdata"}:
            # look dla standard ]]> ending
            match= _markedsectionclose.search(rawdata, i+3)
        albo_inaczej sectName w {"if", "inaczej", "endif"}:
            # look dla MS Office ]> ending
            match= _msmarkedsectionclose.search(rawdata, i+3)
        inaczej:
            self.error('unknown status keyword %r w marked section' % rawdata[i+3:j])
        jeżeli nie match:
            zwróć -1
        jeżeli report:
            j = match.start(0)
            self.unknown_decl(rawdata[i+3: j])
        zwróć match.end(0)

    # Internal -- parse comment, zwróć length albo -1 jeżeli nie terminated
    def parse_comment(self, i, report=1):
        rawdata = self.rawdata
        jeżeli rawdata[i:i+4] != '<!--':
            self.error('unexpected call to parse_comment()')
        match = _commentclose.search(rawdata, i+4)
        jeżeli nie match:
            zwróć -1
        jeżeli report:
            j = match.start(0)
            self.handle_comment(rawdata[i+4: j])
        zwróć match.end(0)

    # Internal -- scan past the internal subset w a <!DOCTYPE declaration,
    # returning the index just past any whitespace following the trailing ']'.
    def _parse_doctype_subset(self, i, declstartpos):
        rawdata = self.rawdata
        n = len(rawdata)
        j = i
        dopóki j < n:
            c = rawdata[j]
            jeżeli c == "<":
                s = rawdata[j:j+2]
                jeżeli s == "<":
                    # end of buffer; incomplete
                    zwróć -1
                jeżeli s != "<!":
                    self.updatepos(declstartpos, j + 1)
                    self.error("unexpected char w internal subset (in %r)" % s)
                jeżeli (j + 2) == n:
                    # end of buffer; incomplete
                    zwróć -1
                jeżeli (j + 4) > n:
                    # end of buffer; incomplete
                    zwróć -1
                jeżeli rawdata[j:j+4] == "<!--":
                    j = self.parse_comment(j, report=0)
                    jeżeli j < 0:
                        zwróć j
                    kontynuuj
                name, j = self._scan_name(j + 2, declstartpos)
                jeżeli j == -1:
                    zwróć -1
                jeżeli name nie w {"attlist", "element", "entity", "notation"}:
                    self.updatepos(declstartpos, j + 2)
                    self.error(
                        "unknown declaration %r w internal subset" % name)
                # handle the individual names
                meth = getattr(self, "_parse_doctype_" + name)
                j = meth(j, declstartpos)
                jeżeli j < 0:
                    zwróć j
            albo_inaczej c == "%":
                # parameter entity reference
                jeżeli (j + 1) == n:
                    # end of buffer; incomplete
                    zwróć -1
                s, j = self._scan_name(j + 1, declstartpos)
                jeżeli j < 0:
                    zwróć j
                jeżeli rawdata[j] == ";":
                    j = j + 1
            albo_inaczej c == "]":
                j = j + 1
                dopóki j < n oraz rawdata[j].isspace():
                    j = j + 1
                jeżeli j < n:
                    jeżeli rawdata[j] == ">":
                        zwróć j
                    self.updatepos(declstartpos, j)
                    self.error("unexpected char after internal subset")
                inaczej:
                    zwróć -1
            albo_inaczej c.isspace():
                j = j + 1
            inaczej:
                self.updatepos(declstartpos, j)
                self.error("unexpected char %r w internal subset" % c)
        # end of buffer reached
        zwróć -1

    # Internal -- scan past <!ELEMENT declarations
    def _parse_doctype_element(self, i, declstartpos):
        name, j = self._scan_name(i, declstartpos)
        jeżeli j == -1:
            zwróć -1
        # style content model; just skip until '>'
        rawdata = self.rawdata
        jeżeli '>' w rawdata[j:]:
            zwróć rawdata.find(">", j) + 1
        zwróć -1

    # Internal -- scan past <!ATTLIST declarations
    def _parse_doctype_attlist(self, i, declstartpos):
        rawdata = self.rawdata
        name, j = self._scan_name(i, declstartpos)
        c = rawdata[j:j+1]
        jeżeli c == "":
            zwróć -1
        jeżeli c == ">":
            zwróć j + 1
        dopóki 1:
            # scan a series of attribute descriptions; simplified:
            #   name type [value] [#constraint]
            name, j = self._scan_name(j, declstartpos)
            jeżeli j < 0:
                zwróć j
            c = rawdata[j:j+1]
            jeżeli c == "":
                zwróć -1
            jeżeli c == "(":
                # an enumerated type; look dla ')'
                jeżeli ")" w rawdata[j:]:
                    j = rawdata.find(")", j) + 1
                inaczej:
                    zwróć -1
                dopóki rawdata[j:j+1].isspace():
                    j = j + 1
                jeżeli nie rawdata[j:]:
                    # end of buffer, incomplete
                    zwróć -1
            inaczej:
                name, j = self._scan_name(j, declstartpos)
            c = rawdata[j:j+1]
            jeżeli nie c:
                zwróć -1
            jeżeli c w "'\"":
                m = _declstringlit_match(rawdata, j)
                jeżeli m:
                    j = m.end()
                inaczej:
                    zwróć -1
                c = rawdata[j:j+1]
                jeżeli nie c:
                    zwróć -1
            jeżeli c == "#":
                jeżeli rawdata[j:] == "#":
                    # end of buffer
                    zwróć -1
                name, j = self._scan_name(j + 1, declstartpos)
                jeżeli j < 0:
                    zwróć j
                c = rawdata[j:j+1]
                jeżeli nie c:
                    zwróć -1
            jeżeli c == '>':
                # all done
                zwróć j + 1

    # Internal -- scan past <!NOTATION declarations
    def _parse_doctype_notation(self, i, declstartpos):
        name, j = self._scan_name(i, declstartpos)
        jeżeli j < 0:
            zwróć j
        rawdata = self.rawdata
        dopóki 1:
            c = rawdata[j:j+1]
            jeżeli nie c:
                # end of buffer; incomplete
                zwróć -1
            jeżeli c == '>':
                zwróć j + 1
            jeżeli c w "'\"":
                m = _declstringlit_match(rawdata, j)
                jeżeli nie m:
                    zwróć -1
                j = m.end()
            inaczej:
                name, j = self._scan_name(j, declstartpos)
                jeżeli j < 0:
                    zwróć j

    # Internal -- scan past <!ENTITY declarations
    def _parse_doctype_entity(self, i, declstartpos):
        rawdata = self.rawdata
        jeżeli rawdata[i:i+1] == "%":
            j = i + 1
            dopóki 1:
                c = rawdata[j:j+1]
                jeżeli nie c:
                    zwróć -1
                jeżeli c.isspace():
                    j = j + 1
                inaczej:
                    przerwij
        inaczej:
            j = i
        name, j = self._scan_name(j, declstartpos)
        jeżeli j < 0:
            zwróć j
        dopóki 1:
            c = self.rawdata[j:j+1]
            jeżeli nie c:
                zwróć -1
            jeżeli c w "'\"":
                m = _declstringlit_match(rawdata, j)
                jeżeli m:
                    j = m.end()
                inaczej:
                    zwróć -1    # incomplete
            albo_inaczej c == ">":
                zwróć j + 1
            inaczej:
                name, j = self._scan_name(j, declstartpos)
                jeżeli j < 0:
                    zwróć j

    # Internal -- scan a name token oraz the new position oraz the token, albo
    # zwróć -1 jeżeli we've reached the end of the buffer.
    def _scan_name(self, i, declstartpos):
        rawdata = self.rawdata
        n = len(rawdata)
        jeżeli i == n:
            zwróć Nic, -1
        m = _declname_match(rawdata, i)
        jeżeli m:
            s = m.group()
            name = s.strip()
            jeżeli (i + len(s)) == n:
                zwróć Nic, -1  # end of buffer
            zwróć name.lower(), m.end()
        inaczej:
            self.updatepos(declstartpos, i)
            self.error("expected name token at %r"
                       % rawdata[declstartpos:declstartpos+20])

    # To be overridden -- handlers dla unknown objects
    def unknown_decl(self, data):
        dalej
