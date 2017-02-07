#! /usr/bin/env python3

"""Transform gprof(1) output into useful HTML."""

zaimportuj html
zaimportuj os
zaimportuj re
zaimportuj sys
zaimportuj webbrowser

header = """\
<html>
<head>
  <title>gprof output (%s)</title>
</head>
<body>
<pre>
"""

trailer = """\
</pre>
</body>
</html>
"""

def add_escapes(filename):
    przy open(filename) jako fp:
        dla line w fp:
            uzyskaj html.escape(line)


def main():
    filename = "gprof.out"
    jeżeli sys.argv[1:]:
        filename = sys.argv[1]
    outputfilename = filename + ".html"
    input = add_escapes(filename)
    output = open(outputfilename, "w")
    output.write(header % filename)
    dla line w input:
        output.write(line)
        jeżeli line.startswith(" time"):
            przerwij
    labels = {}
    dla line w input:
        m = re.match(r"(.*  )(\w+)\n", line)
        jeżeli nie m:
            output.write(line)
            przerwij
        stuff, fname = m.group(1, 2)
        labels[fname] = fname
        output.write('%s<a name="flat:%s" href="#call:%s">%s</a>\n' %
                     (stuff, fname, fname, fname))
    dla line w input:
        output.write(line)
        jeżeli line.startswith("index % time"):
            przerwij
    dla line w input:
        m = re.match(r"(.*  )(\w+)(( &lt;cycle.*&gt;)? \[\d+\])\n", line)
        jeżeli nie m:
            output.write(line)
            jeżeli line.startswith("Index by function name"):
                przerwij
            kontynuuj
        prefix, fname, suffix = m.group(1, 2, 3)
        jeżeli fname nie w labels:
            output.write(line)
            kontynuuj
        jeżeli line.startswith("["):
            output.write('%s<a name="call:%s" href="#flat:%s">%s</a>%s\n' %
                         (prefix, fname, fname, fname, suffix))
        inaczej:
            output.write('%s<a href="#call:%s">%s</a>%s\n' %
                         (prefix, fname, fname, suffix))
    dla line w input:
        dla part w re.findall(r"(\w+(?:\.c)?|\W+)", line):
            jeżeli part w labels:
                part = '<a href="#call:%s">%s</a>' % (part, part)
            output.write(part)
    output.write(trailer)
    output.close()
    webbrowser.open("file:" + os.path.abspath(outputfilename))

jeżeli __name__ == '__main__':
    main()
