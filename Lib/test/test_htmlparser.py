"""Tests dla HTMLParser.py."""

zaimportuj html.parser
zaimportuj pprint
zaimportuj unittest
z test zaimportuj support


klasa EventCollector(html.parser.HTMLParser):

    def __init__(self, *args, **kw):
        self.events = []
        self.append = self.events.append
        html.parser.HTMLParser.__init__(self, *args, **kw)

    def get_events(self):
        # Normalize the list of events so that buffer artefacts don't
        # separate runs of contiguous characters.
        L = []
        prevtype = Nic
        dla event w self.events:
            type = event[0]
            jeżeli type == prevtype == "data":
                L[-1] = ("data", L[-1][1] + event[1])
            inaczej:
                L.append(event)
            prevtype = type
        self.events = L
        zwróć L

    # structure markup

    def handle_starttag(self, tag, attrs):
        self.append(("starttag", tag, attrs))

    def handle_startendtag(self, tag, attrs):
        self.append(("startendtag", tag, attrs))

    def handle_endtag(self, tag):
        self.append(("endtag", tag))

    # all other markup

    def handle_comment(self, data):
        self.append(("comment", data))

    def handle_charref(self, data):
        self.append(("charref", data))

    def handle_data(self, data):
        self.append(("data", data))

    def handle_decl(self, data):
        self.append(("decl", data))

    def handle_entityref(self, data):
        self.append(("entityref", data))

    def handle_pi(self, data):
        self.append(("pi", data))

    def unknown_decl(self, decl):
        self.append(("unknown decl", decl))


klasa EventCollectorExtra(EventCollector):

    def handle_starttag(self, tag, attrs):
        EventCollector.handle_starttag(self, tag, attrs)
        self.append(("starttag_text", self.get_starttag_text()))


klasa EventCollectorCharrefs(EventCollector):

    def get_events(self):
        zwróć self.events

    def handle_charref(self, data):
        self.fail('This should never be called przy convert_charrefs=Prawda')

    def handle_entityref(self, data):
        self.fail('This should never be called przy convert_charrefs=Prawda')


klasa TestCaseBase(unittest.TestCase):

    def get_collector(self):
        zwróć EventCollector(convert_charrefs=Nieprawda)

    def _run_check(self, source, expected_events, collector=Nic):
        jeżeli collector jest Nic:
            collector = self.get_collector()
        parser = collector
        dla s w source:
            parser.feed(s)
        parser.close()
        events = parser.get_events()
        jeżeli events != expected_events:
            self.fail("received events did nie match expected events" +
                      "\nSource:\n" + repr(source) +
                      "\nExpected:\n" + pprint.pformat(expected_events) +
                      "\nReceived:\n" + pprint.pformat(events))

    def _run_check_extra(self, source, events):
        self._run_check(source, events,
                        EventCollectorExtra(convert_charrefs=Nieprawda))


klasa HTMLParserTestCase(TestCaseBase):

    def test_processing_instruction_only(self):
        self._run_check("<?processing instruction>", [
            ("pi", "processing instruction"),
            ])
        self._run_check("<?processing instruction ?>", [
            ("pi", "processing instruction ?"),
            ])

    def test_simple_html(self):
        self._run_check("""
<!DOCTYPE html PUBLIC 'foo'>
<HTML>&entity;&#32;
<!--comment1a
-></foo><bar>&lt;<?pi?></foo<bar
comment1b-->
<Img sRc='Bar' isMAP>sample
text
&#x201C;
<!--comment2a-- --comment2b-->
</Html>
""", [
    ("data", "\n"),
    ("decl", "DOCTYPE html PUBLIC 'foo'"),
    ("data", "\n"),
    ("starttag", "html", []),
    ("entityref", "entity"),
    ("charref", "32"),
    ("data", "\n"),
    ("comment", "comment1a\n-></foo><bar>&lt;<?pi?></foo<bar\ncomment1b"),
    ("data", "\n"),
    ("starttag", "img", [("src", "Bar"), ("ismap", Nic)]),
    ("data", "sample\ntext\n"),
    ("charref", "x201C"),
    ("data", "\n"),
    ("comment", "comment2a-- --comment2b"),
    ("data", "\n"),
    ("endtag", "html"),
    ("data", "\n"),
    ])

    def test_malformatted_charref(self):
        self._run_check("<p>&#bad;</p>", [
            ("starttag", "p", []),
            ("data", "&#bad;"),
            ("endtag", "p"),
        ])
        # add the [] jako a workaround to avoid buffering (see #20288)
        self._run_check(["<div>&#bad;</div>"], [
            ("starttag", "div", []),
            ("data", "&#bad;"),
            ("endtag", "div"),
        ])

    def test_unclosed_entityref(self):
        self._run_check("&entityref foo", [
            ("entityref", "entityref"),
            ("data", " foo"),
            ])

    def test_bad_nesting(self):
        # Strangely, this *is* supposed to test that overlapping
        # elements are allowed.  HTMLParser jest more geared toward
        # lexing the input that parsing the structure.
        self._run_check("<a><b></a></b>", [
            ("starttag", "a", []),
            ("starttag", "b", []),
            ("endtag", "a"),
            ("endtag", "b"),
            ])

    def test_bare_ampersands(self):
        self._run_check("this text & contains & ampersands &", [
            ("data", "this text & contains & ampersands &"),
            ])

    def test_bare_pointy_brackets(self):
        self._run_check("this < text > contains < bare>pointy< brackets", [
            ("data", "this < text > contains < bare>pointy< brackets"),
            ])

    def test_starttag_end_boundary(self):
        self._run_check("""<a b='<'>""", [("starttag", "a", [("b", "<")])])
        self._run_check("""<a b='>'>""", [("starttag", "a", [("b", ">")])])

    def test_buffer_artefacts(self):
        output = [("starttag", "a", [("b", "<")])]
        self._run_check(["<a b='<'>"], output)
        self._run_check(["<a ", "b='<'>"], output)
        self._run_check(["<a b", "='<'>"], output)
        self._run_check(["<a b=", "'<'>"], output)
        self._run_check(["<a b='<", "'>"], output)
        self._run_check(["<a b='<'", ">"], output)

        output = [("starttag", "a", [("b", ">")])]
        self._run_check(["<a b='>'>"], output)
        self._run_check(["<a ", "b='>'>"], output)
        self._run_check(["<a b", "='>'>"], output)
        self._run_check(["<a b=", "'>'>"], output)
        self._run_check(["<a b='>", "'>"], output)
        self._run_check(["<a b='>'", ">"], output)

        output = [("comment", "abc")]
        self._run_check(["", "<!--abc-->"], output)
        self._run_check(["<", "!--abc-->"], output)
        self._run_check(["<!", "--abc-->"], output)
        self._run_check(["<!-", "-abc-->"], output)
        self._run_check(["<!--", "abc-->"], output)
        self._run_check(["<!--a", "bc-->"], output)
        self._run_check(["<!--ab", "c-->"], output)
        self._run_check(["<!--abc", "-->"], output)
        self._run_check(["<!--abc-", "->"], output)
        self._run_check(["<!--abc--", ">"], output)
        self._run_check(["<!--abc-->", ""], output)

    def test_valid_doctypes(self):
        # z http://www.w3.org/QA/2002/04/valid-dtd-list.html
        dtds = ['HTML',  # HTML5 doctype
                ('HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd"'),
                ('HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" '
                 '"http://www.w3.org/TR/html4/loose.dtd"'),
                ('html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
                 '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'),
                ('html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" '
                 '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd"'),
                ('math PUBLIC "-//W3C//DTD MathML 2.0//EN" '
                 '"http://www.w3.org/Math/DTD/mathml2/mathml2.dtd"'),
                ('html PUBLIC "-//W3C//DTD '
                 'XHTML 1.1 plus MathML 2.0 plus SVG 1.1//EN" '
                 '"http://www.w3.org/2002/04/xhtml-math-svg/xhtml-math-svg.dtd"'),
                ('svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
                 '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"'),
                'html PUBLIC "-//IETF//DTD HTML 2.0//EN"',
                'html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"']
        dla dtd w dtds:
            self._run_check("<!DOCTYPE %s>" % dtd,
                            [('decl', 'DOCTYPE ' + dtd)])

    def test_startendtag(self):
        self._run_check("<p/>", [
            ("startendtag", "p", []),
            ])
        self._run_check("<p></p>", [
            ("starttag", "p", []),
            ("endtag", "p"),
            ])
        self._run_check("<p><img src='foo' /></p>", [
            ("starttag", "p", []),
            ("startendtag", "img", [("src", "foo")]),
            ("endtag", "p"),
            ])

    def test_get_starttag_text(self):
        s = """<foo:bar   \n   one="1"\ttwo=2   >"""
        self._run_check_extra(s, [
            ("starttag", "foo:bar", [("one", "1"), ("two", "2")]),
            ("starttag_text", s)])

    def test_cdata_content(self):
        contents = [
            '<!-- nie a comment --> &not-an-entity-ref;',
            "<not a='start tag'>",
            '<a href="" /> <p> <span></span>',
            'foo = "</scr" + "ipt>";',
            'foo = "</SCRIPT" + ">";',
            'foo = <\n/script> ',
            '<!-- document.write("</scr" + "ipt>"); -->',
            ('\n//<![CDATA[\n'
             'document.write(\'<s\'+\'cript type="text/javascript" '
             'src="http://www.example.org/r=\'+new '
             'Date().getTime()+\'"><\\/s\'+\'cript>\');\n//]]>'),
            '\n<!-- //\nvar foo = 3.14;\n// -->\n',
            'foo = "</sty" + "le>";',
            '<!-- \u2603 -->',
            # these two should be invalid according to the HTML 5 spec,
            # section 8.1.2.2
            #'foo = </\nscript>',
            #'foo = </ script>',
        ]
        elements = ['script', 'style', 'SCRIPT', 'STYLE', 'Script', 'Style']
        dla content w contents:
            dla element w elements:
                element_lower = element.lower()
                s = '<{element}>{content}</{element}>'.format(element=element,
                                                               content=content)
                self._run_check(s, [("starttag", element_lower, []),
                                    ("data", content),
                                    ("endtag", element_lower)])

    def test_cdata_with_closing_tags(self):
        # see issue #13358
        # make sure that HTMLParser calls handle_data only once dla each CDATA.
        # The normal event collector normalizes  the events w get_events,
        # so we override it to zwróć the original list of events.
        klasa Collector(EventCollector):
            def get_events(self):
                zwróć self.events

        content = """<!-- nie a comment --> &not-an-entity-ref;
                  <a href="" /> </p><p> <span></span></style>
                  '</script' + '>'"""
        dla element w [' script', 'script ', ' script ',
                        '\nscript', 'script\n', '\nscript\n']:
            element_lower = element.lower().strip()
            s = '<script>{content}</{element}>'.format(element=element,
                                                       content=content)
            self._run_check(s, [("starttag", element_lower, []),
                                ("data", content),
                                ("endtag", element_lower)],
                            collector=Collector(convert_charrefs=Nieprawda))

    def test_comments(self):
        html = ("<!-- I'm a valid comment -->"
                '<!--me too!-->'
                '<!------>'
                '<!---->'
                '<!----I have many hyphens---->'
                '<!-- I have a > w the middle -->'
                '<!-- oraz I have -- w the middle! -->')
        expected = [('comment', " I'm a valid comment "),
                    ('comment', 'me too!'),
                    ('comment', '--'),
                    ('comment', ''),
                    ('comment', '--I have many hyphens--'),
                    ('comment', ' I have a > w the middle '),
                    ('comment', ' oraz I have -- w the middle! ')]
        self._run_check(html, expected)

    def test_condcoms(self):
        html = ('<!--[jeżeli IE & !(lte IE 8)]>aren\'t<![endif]-->'
                '<!--[jeżeli IE 8]>condcoms<![endif]-->'
                '<!--[jeżeli lte IE 7]>pretty?<![endif]-->')
        expected = [('comment', "[jeżeli IE & !(lte IE 8)]>aren't<![endif]"),
                    ('comment', '[jeżeli IE 8]>condcoms<![endif]'),
                    ('comment', '[jeżeli lte IE 7]>pretty?<![endif]')]
        self._run_check(html, expected)

    def test_convert_charrefs(self):
        # default value dla convert_charrefs jest now Prawda
        collector = lambda: EventCollectorCharrefs()
        self.assertPrawda(collector().convert_charrefs)
        charrefs = ['&quot;', '&#34;', '&#x22;', '&quot', '&#34', '&#x22']
        # check charrefs w the middle of the text/attributes
        expected = [('starttag', 'a', [('href', 'foo"zar')]),
                    ('data', 'a"z'), ('endtag', 'a')]
        dla charref w charrefs:
            self._run_check('<a href="foo{0}zar">a{0}z</a>'.format(charref),
                            expected, collector=collector())
        # check charrefs at the beginning/end of the text/attributes
        expected = [('data', '"'),
                    ('starttag', 'a', [('x', '"'), ('y', '"X'), ('z', 'X"')]),
                    ('data', '"'), ('endtag', 'a'), ('data', '"')]
        dla charref w charrefs:
            self._run_check('{0}<a x="{0}" y="{0}X" z="X{0}">'
                            '{0}</a>{0}'.format(charref),
                            expected, collector=collector())
        # check charrefs w <script>/<style> elements
        dla charref w charrefs:
            text = 'X'.join([charref]*3)
            expected = [('data', '"'),
                        ('starttag', 'script', []), ('data', text),
                        ('endtag', 'script'), ('data', '"'),
                        ('starttag', 'style', []), ('data', text),
                        ('endtag', 'style'), ('data', '"')]
            self._run_check('{1}<script>{0}</script>{1}'
                            '<style>{0}</style>{1}'.format(text, charref),
                            expected, collector=collector())
        # check truncated charrefs at the end of the file
        html = '&quo &# &#x'
        dla x w range(1, len(html)):
            self._run_check(html[:x], [('data', html[:x])],
                            collector=collector())
        # check a string przy no charrefs
        self._run_check('no charrefs here', [('data', 'no charrefs here')],
                        collector=collector())

    # the remaining tests were dla the "tolerant" parser (which jest now
    # the default), oraz check various kind of broken markup
    def test_tolerant_parsing(self):
        self._run_check('<html <html>te>>xt&a<<bc</a></html>\n'
                        '<img src="URL><//img></html</html>', [
                            ('starttag', 'html', [('<html', Nic)]),
                            ('data', 'te>>xt'),
                            ('entityref', 'a'),
                            ('data', '<'),
                            ('starttag', 'bc<', [('a', Nic)]),
                            ('endtag', 'html'),
                            ('data', '\n<img src="URL>'),
                            ('comment', '/img'),
                            ('endtag', 'html<')])

    def test_starttag_junk_chars(self):
        self._run_check("</>", [])
        self._run_check("</$>", [('comment', '$')])
        self._run_check("</", [('data', '</')])
        self._run_check("</a", [('data', '</a')])
        self._run_check("<a<a>", [('starttag', 'a<a', [])])
        self._run_check("</a<a>", [('endtag', 'a<a')])
        self._run_check("<!", [('data', '<!')])
        self._run_check("<a", [('data', '<a')])
        self._run_check("<a foo='bar'", [('data', "<a foo='bar'")])
        self._run_check("<a foo='bar", [('data', "<a foo='bar")])
        self._run_check("<a foo='>'", [('data', "<a foo='>'")])
        self._run_check("<a foo='>", [('data', "<a foo='>")])
        self._run_check("<a$>", [('starttag', 'a$', [])])
        self._run_check("<a$b>", [('starttag', 'a$b', [])])
        self._run_check("<a$b/>", [('startendtag', 'a$b', [])])
        self._run_check("<a$b  >", [('starttag', 'a$b', [])])
        self._run_check("<a$b  />", [('startendtag', 'a$b', [])])

    def test_slashes_in_starttag(self):
        self._run_check('<a foo="var"/>', [('startendtag', 'a', [('foo', 'var')])])
        html = ('<img width=902 height=250px '
                'src="/sites/default/files/images/homepage/foo.jpg" '
                '/*what am I doing here*/ />')
        expected = [(
            'startendtag', 'img',
            [('width', '902'), ('height', '250px'),
             ('src', '/sites/default/files/images/homepage/foo.jpg'),
             ('*what', Nic), ('am', Nic), ('i', Nic),
             ('doing', Nic), ('here*', Nic)]
        )]
        self._run_check(html, expected)
        html = ('<a / /foo/ / /=/ / /bar/ / />'
                '<a / /foo/ / /=/ / /bar/ / >')
        expected = [
            ('startendtag', 'a', [('foo', Nic), ('=', Nic), ('bar', Nic)]),
            ('starttag', 'a', [('foo', Nic), ('=', Nic), ('bar', Nic)])
        ]
        self._run_check(html, expected)
        #see issue #14538
        html = ('<meta><meta / ><meta // ><meta / / >'
                '<meta/><meta /><meta //><meta//>')
        expected = [
            ('starttag', 'meta', []), ('starttag', 'meta', []),
            ('starttag', 'meta', []), ('starttag', 'meta', []),
            ('startendtag', 'meta', []), ('startendtag', 'meta', []),
            ('startendtag', 'meta', []), ('startendtag', 'meta', []),
        ]
        self._run_check(html, expected)

    def test_declaration_junk_chars(self):
        self._run_check("<!DOCTYPE foo $ >", [('decl', 'DOCTYPE foo $ ')])

    def test_illegal_declarations(self):
        self._run_check('<!spacer type="block" height="25">',
                        [('comment', 'spacer type="block" height="25"')])

    def test_with_unquoted_attributes(self):
        # see #12008
        html = ("<html><body bgcolor=d0ca90 text='181008'>"
                "<table cellspacing=0 cellpadding=1 width=100% ><tr>"
                "<td align=left><font size=-1>"
                "- <a href=/rabota/><span class=en> software-and-i</span></a>"
                "- <a href='/1/'><span class=en> library</span></a></table>")
        expected = [
            ('starttag', 'html', []),
            ('starttag', 'body', [('bgcolor', 'd0ca90'), ('text', '181008')]),
            ('starttag', 'table',
                [('cellspacing', '0'), ('cellpadding', '1'), ('width', '100%')]),
            ('starttag', 'tr', []),
            ('starttag', 'td', [('align', 'left')]),
            ('starttag', 'font', [('size', '-1')]),
            ('data', '- '), ('starttag', 'a', [('href', '/rabota/')]),
            ('starttag', 'span', [('class', 'en')]), ('data', ' software-and-i'),
            ('endtag', 'span'), ('endtag', 'a'),
            ('data', '- '), ('starttag', 'a', [('href', '/1/')]),
            ('starttag', 'span', [('class', 'en')]), ('data', ' library'),
            ('endtag', 'span'), ('endtag', 'a'), ('endtag', 'table')
        ]
        self._run_check(html, expected)

    def test_comma_between_attributes(self):
        self._run_check('<form action="/xxx.php?a=1&amp;b=2&amp", '
                        'method="post">', [
                            ('starttag', 'form',
                                [('action', '/xxx.php?a=1&b=2&'),
                                 (',', Nic), ('method', 'post')])])

    def test_weird_chars_in_unquoted_attribute_values(self):
        self._run_check('<form action=bogus|&#()value>', [
                            ('starttag', 'form',
                                [('action', 'bogus|&#()value')])])

    def test_invalid_end_tags(self):
        # A collection of broken end tags. <br> jest used jako separator.
        # see http://www.w3.org/TR/html5/tokenization.html#end-tag-open-state
        # oraz #13993
        html = ('<br></label</p><br></div end tmAd-leaderBoard><br></<h4><br>'
                '</li class="unit"><br></li\r\n\t\t\t\t\t\t</ul><br></><br>')
        expected = [('starttag', 'br', []),
                    # < jest part of the name, / jest discarded, p jest an attribute
                    ('endtag', 'label<'),
                    ('starttag', 'br', []),
                    # text oraz attributes are discarded
                    ('endtag', 'div'),
                    ('starttag', 'br', []),
                    # comment because the first char after </ jest nie a-zA-Z
                    ('comment', '<h4'),
                    ('starttag', 'br', []),
                    # attributes are discarded
                    ('endtag', 'li'),
                    ('starttag', 'br', []),
                    # everything till ul (included) jest discarded
                    ('endtag', 'li'),
                    ('starttag', 'br', []),
                    # </> jest ignored
                    ('starttag', 'br', [])]
        self._run_check(html, expected)

    def test_broken_invalid_end_tag(self):
        # This jest technically wrong (the "> shouldn't be included w the 'data')
        # but jest probably nie worth fixing it (in addition to all the cases of
        # the previous test, it would require a full attribute parsing).
        # see #13993
        html = '<b>This</b attr=">"> confuses the parser'
        expected = [('starttag', 'b', []),
                    ('data', 'This'),
                    ('endtag', 'b'),
                    ('data', '"> confuses the parser')]
        self._run_check(html, expected)

    def test_correct_detection_of_start_tags(self):
        # see #13273
        html = ('<div style=""    ><b>The <a href="some_url">rain</a> '
                '<br /> w <span>Spain</span></b></div>')
        expected = [
            ('starttag', 'div', [('style', '')]),
            ('starttag', 'b', []),
            ('data', 'The '),
            ('starttag', 'a', [('href', 'some_url')]),
            ('data', 'rain'),
            ('endtag', 'a'),
            ('data', ' '),
            ('startendtag', 'br', []),
            ('data', ' w '),
            ('starttag', 'span', []),
            ('data', 'Spain'),
            ('endtag', 'span'),
            ('endtag', 'b'),
            ('endtag', 'div')
        ]
        self._run_check(html, expected)

        html = '<div style="", foo = "bar" ><b>The <a href="some_url">rain</a>'
        expected = [
            ('starttag', 'div', [('style', ''), (',', Nic), ('foo', 'bar')]),
            ('starttag', 'b', []),
            ('data', 'The '),
            ('starttag', 'a', [('href', 'some_url')]),
            ('data', 'rain'),
            ('endtag', 'a'),
        ]
        self._run_check(html, expected)

    def test_EOF_in_charref(self):
        # see #17802
        # This test checks that the UnboundLocalError reported w the issue
        # jest nie podnieśd, however I'm nie sure the returned values are correct.
        # Maybe HTMLParser should use self.unescape dla these
        data = [
            ('a&', [('data', 'a&')]),
            ('a&b', [('data', 'ab')]),
            ('a&b ', [('data', 'a'), ('entityref', 'b'), ('data', ' ')]),
            ('a&b;', [('data', 'a'), ('entityref', 'b')]),
        ]
        dla html, expected w data:
            self._run_check(html, expected)

    def test_unescape_method(self):
        z html zaimportuj unescape
        p = self.get_collector()
        przy self.assertWarns(DeprecationWarning):
            s = '&quot;&#34;&#x22;&quot&#34&#x22&#bad;'
            self.assertEqual(p.unescape(s), unescape(s))

    def test_broken_comments(self):
        html = ('<! nie really a comment >'
                '<! nie a comment either -->'
                '<! -- close enough -->'
                '<!><!<-- this was an empty comment>'
                '<!!! another bogus comment !!!>')
        expected = [
            ('comment', ' nie really a comment '),
            ('comment', ' nie a comment either --'),
            ('comment', ' -- close enough --'),
            ('comment', ''),
            ('comment', '<-- this was an empty comment'),
            ('comment', '!! another bogus comment !!!'),
        ]
        self._run_check(html, expected)

    def test_broken_condcoms(self):
        # these condcoms are missing the '--' after '<!' oraz before the '>'
        html = ('<![jeżeli !(IE)]>broken condcom<![endif]>'
                '<![jeżeli ! IE]><link href="favicon.tiff"/><![endif]>'
                '<![jeżeli !IE 6]><img src="firefox.png" /><![endif]>'
                '<![jeżeli !ie 6]><b>foo</b><![endif]>'
                '<![jeżeli (!IE)|(lt IE 9)]><img src="mammoth.bmp" /><![endif]>')
        # According to the HTML5 specs sections "8.2.4.44 Bogus comment state"
        # oraz "8.2.4.45 Markup declaration open state", comment tokens should
        # be emitted instead of 'unknown decl', but calling unknown_decl
        # provides more flexibility.
        # See also Lib/_markupbase.py:parse_declaration
        expected = [
            ('unknown decl', 'jeżeli !(IE)'),
            ('data', 'broken condcom'),
            ('unknown decl', 'endif'),
            ('unknown decl', 'jeżeli ! IE'),
            ('startendtag', 'link', [('href', 'favicon.tiff')]),
            ('unknown decl', 'endif'),
            ('unknown decl', 'jeżeli !IE 6'),
            ('startendtag', 'img', [('src', 'firefox.png')]),
            ('unknown decl', 'endif'),
            ('unknown decl', 'jeżeli !ie 6'),
            ('starttag', 'b', []),
            ('data', 'foo'),
            ('endtag', 'b'),
            ('unknown decl', 'endif'),
            ('unknown decl', 'jeżeli (!IE)|(lt IE 9)'),
            ('startendtag', 'img', [('src', 'mammoth.bmp')]),
            ('unknown decl', 'endif')
        ]
        self._run_check(html, expected)


klasa AttributesTestCase(TestCaseBase):

    def test_attr_syntax(self):
        output = [
          ("starttag", "a", [("b", "v"), ("c", "v"), ("d", "v"), ("e", Nic)])
        ]
        self._run_check("""<a b='v' c="v" d=v e>""", output)
        self._run_check("""<a  b = 'v' c = "v" d = v e>""", output)
        self._run_check("""<a\nb\n=\n'v'\nc\n=\n"v"\nd\n=\nv\ne>""", output)
        self._run_check("""<a\tb\t=\t'v'\tc\t=\t"v"\td\t=\tv\te>""", output)

    def test_attr_values(self):
        self._run_check("""<a b='xxx\n\txxx' c="yyy\t\nyyy" d='\txyz\n'>""",
                        [("starttag", "a", [("b", "xxx\n\txxx"),
                                            ("c", "yyy\t\nyyy"),
                                            ("d", "\txyz\n")])])
        self._run_check("""<a b='' c="">""",
                        [("starttag", "a", [("b", ""), ("c", "")])])
        # Regression test dla SF patch #669683.
        self._run_check("<e a=rgb(1,2,3)>",
                        [("starttag", "e", [("a", "rgb(1,2,3)")])])
        # Regression test dla SF bug #921657.
        self._run_check(
            "<a href=mailto:xyz@example.com>",
            [("starttag", "a", [("href", "mailto:xyz@example.com")])])

    def test_attr_nonascii(self):
        # see issue 7311
        self._run_check(
            "<img src=/foo/bar.png alt=\u4e2d\u6587>",
            [("starttag", "img", [("src", "/foo/bar.png"),
                                  ("alt", "\u4e2d\u6587")])])
        self._run_check(
            "<a title='\u30c6\u30b9\u30c8' href='\u30c6\u30b9\u30c8.html'>",
            [("starttag", "a", [("title", "\u30c6\u30b9\u30c8"),
                                ("href", "\u30c6\u30b9\u30c8.html")])])
        self._run_check(
            '<a title="\u30c6\u30b9\u30c8" href="\u30c6\u30b9\u30c8.html">',
            [("starttag", "a", [("title", "\u30c6\u30b9\u30c8"),
                                ("href", "\u30c6\u30b9\u30c8.html")])])

    def test_attr_entity_replacement(self):
        self._run_check(
            "<a b='&amp;&gt;&lt;&quot;&apos;'>",
            [("starttag", "a", [("b", "&><\"'")])])

    def test_attr_funky_names(self):
        self._run_check(
            "<a a.b='v' c:d=v e-f=v>",
            [("starttag", "a", [("a.b", "v"), ("c:d", "v"), ("e-f", "v")])])

    def test_entityrefs_in_attributes(self):
        self._run_check(
            "<html foo='&euro;&amp;&#97;&#x61;&unsupported;'>",
            [("starttag", "html", [("foo", "\u20AC&aa&unsupported;")])])


    def test_attr_funky_names2(self):
        self._run_check(
            "<a $><b $=%><c \=/>",
            [("starttag", "a", [("$", Nic)]),
             ("starttag", "b", [("$", "%")]),
             ("starttag", "c", [("\\", "/")])])

    def test_entities_in_attribute_value(self):
        # see #1200313
        dla entity w ['&', '&amp;', '&#38;', '&#x26;']:
            self._run_check('<a href="%s">' % entity,
                            [("starttag", "a", [("href", "&")])])
            self._run_check("<a href='%s'>" % entity,
                            [("starttag", "a", [("href", "&")])])
            self._run_check("<a href=%s>" % entity,
                            [("starttag", "a", [("href", "&")])])

    def test_malformed_attributes(self):
        # see #13357
        html = (
            "<a href=test'style='color:red;bad1'>test - bad1</a>"
            "<a href=test'+style='color:red;ba2'>test - bad2</a>"
            "<a href=test'&nbsp;style='color:red;bad3'>test - bad3</a>"
            "<a href = test'&nbsp;style='color:red;bad4'  >test - bad4</a>"
        )
        expected = [
            ('starttag', 'a', [('href', "test'style='color:red;bad1'")]),
            ('data', 'test - bad1'), ('endtag', 'a'),
            ('starttag', 'a', [('href', "test'+style='color:red;ba2'")]),
            ('data', 'test - bad2'), ('endtag', 'a'),
            ('starttag', 'a', [('href', "test'\xa0style='color:red;bad3'")]),
            ('data', 'test - bad3'), ('endtag', 'a'),
            ('starttag', 'a', [('href', "test'\xa0style='color:red;bad4'")]),
            ('data', 'test - bad4'), ('endtag', 'a')
        ]
        self._run_check(html, expected)

    def test_malformed_adjacent_attributes(self):
        # see #12629
        self._run_check('<x><y z=""o"" /></x>',
                        [('starttag', 'x', []),
                            ('startendtag', 'y', [('z', ''), ('o""', Nic)]),
                            ('endtag', 'x')])
        self._run_check('<x><y z="""" /></x>',
                        [('starttag', 'x', []),
                            ('startendtag', 'y', [('z', ''), ('""', Nic)]),
                            ('endtag', 'x')])

    # see #755670 dla the following 3 tests
    def test_adjacent_attributes(self):
        self._run_check('<a width="100%"cellspacing=0>',
                        [("starttag", "a",
                          [("width", "100%"), ("cellspacing","0")])])

        self._run_check('<a id="foo"class="bar">',
                        [("starttag", "a",
                          [("id", "foo"), ("class","bar")])])

    def test_missing_attribute_value(self):
        self._run_check('<a v=>',
                        [("starttag", "a", [("v", "")])])

    def test_javascript_attribute_value(self):
        self._run_check("<a href=javascript:popup('/popup/help.html')>",
                        [("starttag", "a",
                          [("href", "javascript:popup('/popup/help.html')")])])

    def test_end_tag_in_attribute_value(self):
        # see #1745761
        self._run_check("<a href='http://www.example.org/\">;'>spam</a>",
                        [("starttag", "a",
                          [("href", "http://www.example.org/\">;")]),
                         ("data", "spam"), ("endtag", "a")])


jeżeli __name__ == "__main__":
    unittest.main()
