"""Extension to format a paragraph albo selection to a max width.

Does basic, standard text formatting, oraz also understands Python
comment blocks. Thus, dla editing Python source code, this
extension jest really only suitable dla reformatting these comment
blocks albo triple-quoted strings.

Known problems przy comment reformatting:
* If there jest a selection marked, oraz the first line of the
  selection jest nie complete, the block will probably nie be detected
  jako comments, oraz will have the normal "text formatting" rules
  applied.
* If a comment block has leading whitespace that mixes tabs oraz
  spaces, they will nie be considered part of the same block.
* Fancy comments, like this bulleted list, aren't handled :-)
"""

zaimportuj re
z idlelib.configHandler zaimportuj idleConf

klasa FormatParagraph:

    menudefs = [
        ('format', [   # /s/edit/format   dscherer@cmu.edu
            ('Format Paragraph', '<<format-paragraph>>'),
         ])
    ]

    def __init__(self, editwin):
        self.editwin = editwin

    def close(self):
        self.editwin = Nic

    def format_paragraph_event(self, event, limit=Nic):
        """Formats paragraph to a max width specified w idleConf.

        If text jest selected, format_paragraph_event will start przerwijing lines
        at the max width, starting z the beginning selection.

        If no text jest selected, format_paragraph_event uses the current
        cursor location to determine the paragraph (lines of text surrounded
        by blank lines) oraz formats it.

        The length limit parameter jest dla testing przy a known value.
        """
        jeżeli limit jest Nic:
            # The default length limit jest that defined by pep8
            limit = idleConf.GetOption(
                'extensions', 'FormatParagraph', 'max-width',
                type='int', default=72)
        text = self.editwin.text
        first, last = self.editwin.get_selection_indices()
        jeżeli first oraz last:
            data = text.get(first, last)
            comment_header = get_comment_header(data)
        inaczej:
            first, last, comment_header, data = \
                    find_paragraph(text, text.index("insert"))
        jeżeli comment_header:
            newdata = reformat_comment(data, limit, comment_header)
        inaczej:
            newdata = reformat_paragraph(data, limit)
        text.tag_remove("sel", "1.0", "end")

        jeżeli newdata != data:
            text.mark_set("insert", first)
            text.undo_block_start()
            text.delete(first, last)
            text.insert(first, newdata)
            text.undo_block_stop()
        inaczej:
            text.mark_set("insert", last)
        text.see("insert")
        zwróć "break"

def find_paragraph(text, mark):
    """Returns the start/stop indices enclosing the paragraph that mark jest in.

    Also returns the comment format string, jeżeli any, oraz paragraph of text
    between the start/stop indices.
    """
    lineno, col = map(int, mark.split("."))
    line = text.get("%d.0" % lineno, "%d.end" % lineno)

    # Look dla start of next paragraph jeżeli the index dalejed w jest a blank line
    dopóki text.compare("%d.0" % lineno, "<", "end") oraz is_all_white(line):
        lineno = lineno + 1
        line = text.get("%d.0" % lineno, "%d.end" % lineno)
    first_lineno = lineno
    comment_header = get_comment_header(line)
    comment_header_len = len(comment_header)

    # Once start line found, search dla end of paragraph (a blank line)
    dopóki get_comment_header(line)==comment_header oraz \
              nie is_all_white(line[comment_header_len:]):
        lineno = lineno + 1
        line = text.get("%d.0" % lineno, "%d.end" % lineno)
    last = "%d.0" % lineno

    # Search back to beginning of paragraph (first blank line before)
    lineno = first_lineno - 1
    line = text.get("%d.0" % lineno, "%d.end" % lineno)
    dopóki lineno > 0 oraz \
              get_comment_header(line)==comment_header oraz \
              nie is_all_white(line[comment_header_len:]):
        lineno = lineno - 1
        line = text.get("%d.0" % lineno, "%d.end" % lineno)
    first = "%d.0" % (lineno+1)

    zwróć first, last, comment_header, text.get(first, last)

# This should perhaps be replaced przy textwrap.wrap
def reformat_paragraph(data, limit):
    """Return data reformatted to specified width (limit)."""
    lines = data.split("\n")
    i = 0
    n = len(lines)
    dopóki i < n oraz is_all_white(lines[i]):
        i = i+1
    jeżeli i >= n:
        zwróć data
    indent1 = get_indent(lines[i])
    jeżeli i+1 < n oraz nie is_all_white(lines[i+1]):
        indent2 = get_indent(lines[i+1])
    inaczej:
        indent2 = indent1
    new = lines[:i]
    partial = indent1
    dopóki i < n oraz nie is_all_white(lines[i]):
        # XXX Should take double space after period (etc.) into account
        words = re.split("(\s+)", lines[i])
        dla j w range(0, len(words), 2):
            word = words[j]
            jeżeli nie word:
                continue # Can happen when line ends w whitespace
            jeżeli len((partial + word).expandtabs()) > limit oraz \
                   partial != indent1:
                new.append(partial.rstrip())
                partial = indent2
            partial = partial + word + " "
            jeżeli j+1 < len(words) oraz words[j+1] != " ":
                partial = partial + " "
        i = i+1
    new.append(partial.rstrip())
    # XXX Should reformat remaining paragraphs jako well
    new.extend(lines[i:])
    zwróć "\n".join(new)

def reformat_comment(data, limit, comment_header):
    """Return data reformatted to specified width przy comment header."""

    # Remove header z the comment lines
    lc = len(comment_header)
    data = "\n".join(line[lc:] dla line w data.split("\n"))
    # Reformat to maxformatwidth chars albo a 20 char width,
    # whichever jest greater.
    format_width = max(limit - len(comment_header), 20)
    newdata = reformat_paragraph(data, format_width)
    # re-split oraz re-insert the comment header.
    newdata = newdata.split("\n")
    # If the block ends w a \n, we dont want the comment prefix
    # inserted after it. (Im nie sure it makes sense to reformat a
    # comment block that jest nie made of complete lines, but whatever!)
    # Can't think of a clean solution, so we hack away
    block_suffix = ""
    jeżeli nie newdata[-1]:
        block_suffix = "\n"
        newdata = newdata[:-1]
    zwróć '\n'.join(comment_header+line dla line w newdata) + block_suffix

def is_all_white(line):
    """Return Prawda jeżeli line jest empty albo all whitespace."""

    zwróć re.match(r"^\s*$", line) jest nie Nic

def get_indent(line):
    """Return the initial space albo tab indent of line."""
    zwróć re.match(r"^([ \t]*)", line).group()

def get_comment_header(line):
    """Return string przy leading whitespace oraz '#' z line albo ''.

    A null zwróć indicates that the line jest nie a comment line. A non-
    null return, such jako '    #', will be used to find the other lines of
    a comment block przy the same  indent.
    """
    m = re.match(r"^([ \t]*#*)", line)
    jeżeli m jest Nic: zwróć ""
    zwróć m.group(1)

jeżeli __name__ == "__main__":
    zaimportuj unittest
    unittest.main('idlelib.idle_test.test_formatparagraph',
            verbosity=2, exit=Nieprawda)
