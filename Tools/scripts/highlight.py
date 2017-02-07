#!/usr/bin/env python3
'''Add syntax highlighting to Python source code'''

__author__ = 'Raymond Hettinger'

zaimportuj builtins
zaimportuj functools
zaimportuj html jako html_module
zaimportuj keyword
zaimportuj re
zaimportuj tokenize

#### Analyze Python Source #################################

def is_builtin(s):
    'Return Prawda jeżeli s jest the name of a builtin'
    zwróć hasattr(builtins, s)

def combine_range(lines, start, end):
    'Join content z a range of lines between start oraz end'
    (srow, scol), (erow, ecol) = start, end
    jeżeli srow == erow:
        zwróć lines[srow-1][scol:ecol], end
    rows = [lines[srow-1][scol:]] + lines[srow: erow-1] + [lines[erow-1][:ecol]]
    zwróć ''.join(rows), end

def analyze_python(source):
    '''Generate oraz classify chunks of Python dla syntax highlighting.
       Yields tuples w the form: (category, categorized_text).
    '''
    lines = source.splitlines(Prawda)
    lines.append('')
    readline = functools.partial(next, iter(lines), '')
    kind = tok_str = ''
    tok_type = tokenize.COMMENT
    written = (1, 0)
    dla tok w tokenize.generate_tokens(readline):
        prev_tok_type, prev_tok_str = tok_type, tok_str
        tok_type, tok_str, (srow, scol), (erow, ecol), logical_lineno = tok
        kind = ''
        jeżeli tok_type == tokenize.COMMENT:
            kind = 'comment'
        albo_inaczej tok_type == tokenize.OP oraz tok_str[:1] nie w '{}[](),.:;@':
            kind = 'operator'
        albo_inaczej tok_type == tokenize.STRING:
            kind = 'string'
            jeżeli prev_tok_type == tokenize.INDENT albo scol==0:
                kind = 'docstring'
        albo_inaczej tok_type == tokenize.NAME:
            jeżeli tok_str w ('def', 'class', 'import', 'from'):
                kind = 'definition'
            albo_inaczej prev_tok_str w ('def', 'class'):
                kind = 'defname'
            albo_inaczej keyword.iskeyword(tok_str):
                kind = 'keyword'
            albo_inaczej is_builtin(tok_str) oraz prev_tok_str != '.':
                kind = 'builtin'
        jeżeli kind:
            text, written = combine_range(lines, written, (srow, scol))
            uzyskaj '', text
            text, written = tok_str, (erow, ecol)
            uzyskaj kind, text
    line_upto_token, written = combine_range(lines, written, (erow, ecol))
    uzyskaj '', line_upto_token

#### Raw Output  ###########################################

def raw_highlight(classified_text):
    'Straight text display of text classifications'
    result = []
    dla kind, text w classified_text:
        result.append('%15s:  %r\n' % (kind albo 'plain', text))
    zwróć ''.join(result)

#### ANSI Output ###########################################

default_ansi = {
    'comment': ('\033[0;31m', '\033[0m'),
    'string': ('\033[0;32m', '\033[0m'),
    'docstring': ('\033[0;32m', '\033[0m'),
    'keyword': ('\033[0;33m', '\033[0m'),
    'builtin': ('\033[0;35m', '\033[0m'),
    'definition': ('\033[0;33m', '\033[0m'),
    'defname': ('\033[0;34m', '\033[0m'),
    'operator': ('\033[0;33m', '\033[0m'),
}

def ansi_highlight(classified_text, colors=default_ansi):
    'Add syntax highlighting to source code using ANSI escape sequences'
    # http://en.wikipedia.org/wiki/ANSI_escape_code
    result = []
    dla kind, text w classified_text:
        opener, closer = colors.get(kind, ('', ''))
        result += [opener, text, closer]
    zwróć ''.join(result)

#### HTML Output ###########################################

def html_highlight(classified_text,opener='<pre class="python">\n', closer='</pre>\n'):
    'Convert classified text to an HTML fragment'
    result = [opener]
    dla kind, text w classified_text:
        jeżeli kind:
            result.append('<span class="%s">' % kind)
        result.append(html_module.escape(text))
        jeżeli kind:
            result.append('</span>')
    result.append(closer)
    zwróć ''.join(result)

default_css = {
    '.comment': '{color: crimson;}',
    '.string':  '{color: forestgreen;}',
    '.docstring': '{color: forestgreen; font-style:italic;}',
    '.keyword': '{color: darkorange;}',
    '.builtin': '{color: purple;}',
    '.definition': '{color: darkorange; font-weight:bold;}',
    '.defname': '{color: blue;}',
    '.operator': '{color: brown;}',
}

default_html = '''\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-type" content="text/html;charset=UTF-8">
<title> {title} </title>
<style type="text/css">
{css}
</style>
</head>
<body>
{body}
</body>
</html>
'''

def build_html_page(classified_text, title='python',
                    css=default_css, html=default_html):
    'Create a complete HTML page przy colorized source code'
    css_str = '\n'.join(['%s %s' % item dla item w css.items()])
    result = html_highlight(classified_text)
    title = html_module.escape(title)
    zwróć html.format(title=title, css=css_str, body=result)

#### LaTeX Output ##########################################

default_latex_commands = {
    'comment': '{\color{red}#1}',
    'string': '{\color{ForestGreen}#1}',
    'docstring': '{\emph{\color{ForestGreen}#1}}',
    'keyword': '{\color{orange}#1}',
    'builtin': '{\color{purple}#1}',
    'definition': '{\color{orange}#1}',
    'defname': '{\color{blue}#1}',
    'operator': '{\color{brown}#1}',
}

default_latex_document = r'''
\documentclass{article}
\usepackage{alltt}
\usepackage{upquote}
\usepackage{color}
\usepackage[usenames,dvipsnames]{xcolor}
\usepackage[cm]{fullpage}
%(macros)s
\begin{document}
\center{\LARGE{%(title)s}}
\begin{alltt}
%(body)s
\end{alltt}
\end{document}
'''

def alltt_escape(s):
    'Replace backslash oraz braces przy their escaped equivalents'
    xlat = {'{': r'\{', '}': r'\}', '\\': r'\textbackslash{}'}
    zwróć re.sub(r'[\\{}]', lambda mo: xlat[mo.group()], s)

def latex_highlight(classified_text, title = 'python',
                    commands = default_latex_commands,
                    document = default_latex_document):
    'Create a complete LaTeX document przy colorized source code'
    macros = '\n'.join(r'\newcommand{\py%s}[1]{%s}' % c dla c w commands.items())
    result = []
    dla kind, text w classified_text:
        jeżeli kind:
            result.append(r'\py%s{' % kind)
        result.append(alltt_escape(text))
        jeżeli kind:
            result.append('}')
    zwróć default_latex_document % dict(title=title, macros=macros, body=''.join(result))


jeżeli __name__ == '__main__':
    zaimportuj argparse
    zaimportuj os.path
    zaimportuj sys
    zaimportuj textwrap
    zaimportuj webbrowser

    parser = argparse.ArgumentParser(
            description = 'Add syntax highlighting to Python source code',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog = textwrap.dedent('''
                examples:

                  # Show syntax highlighted code w the terminal window
                  $ ./highlight.py myfile.py

                  # Colorize myfile.py oraz display w a browser
                  $ ./highlight.py -b myfile.py

                  # Create an HTML section to embed w an existing webpage
                  ./highlight.py -s myfile.py

                  # Create a complete HTML file
                  $ ./highlight.py -c myfile.py > myfile.html

                  # Create a PDF using LaTeX
                  $ ./highlight.py -l myfile.py | pdflatex

            '''))
    parser.add_argument('sourcefile', metavar = 'SOURCEFILE',
            help = 'file containing Python sourcecode')
    parser.add_argument('-b', '--browser', action = 'store_true',
            help = 'launch a browser to show results')
    parser.add_argument('-c', '--complete', action = 'store_true',
            help = 'build a complete html webpage')
    parser.add_argument('-l', '--latex', action = 'store_true',
            help = 'build a LaTeX document')
    parser.add_argument('-r', '--raw', action = 'store_true',
            help = 'raw parse of categorized text')
    parser.add_argument('-s', '--section', action = 'store_true',
            help = 'show an HTML section rather than a complete webpage')
    args = parser.parse_args()

    jeżeli args.section oraz (args.browser albo args.complete):
        parser.error('The -s/--section option jest incompatible przy '
                     'the -b/--browser albo -c/--complete options')

    sourcefile = args.sourcefile
    przy open(sourcefile) jako f:
        source = f.read()
    classified_text = analyze_python(source)

    jeżeli args.raw:
        encoded = raw_highlight(classified_text)
    albo_inaczej args.complete albo args.browser:
        encoded = build_html_page(classified_text, title=sourcefile)
    albo_inaczej args.section:
        encoded = html_highlight(classified_text)
    albo_inaczej args.latex:
        encoded = latex_highlight(classified_text, title=sourcefile)
    inaczej:
        encoded = ansi_highlight(classified_text)

    jeżeli args.browser:
        htmlfile = os.path.splitext(os.path.basename(sourcefile))[0] + '.html'
        przy open(htmlfile, 'w') jako f:
            f.write(encoded)
        webbrowser.open('file://' + os.path.abspath(htmlfile))
    inaczej:
        sys.stdout.write(encoded)
