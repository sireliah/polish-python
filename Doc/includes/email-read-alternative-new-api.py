zaimportuj os
zaimportuj sys
zaimportuj tempfile
zaimportuj mimetypes
zaimportuj webbrowser

# Import the email modules we'll need
z email zaimportuj policy
z email.parser zaimportuj BytesParser

# An imaginary module that would make this work oraz be safe.
z imaginary zaimportuj magic_html_parser

# In a real program you'd get the filename z the arguments.
przy open('outgoing.msg', 'rb') jako fp:
    msg = BytesParser(policy=policy.default).parse(fp)

# Now the header items can be accessed jako a dictionary, oraz any non-ASCII will
# be converted to unicode:
print('To:', msg['to'])
print('From:', msg['from'])
print('Subject:', msg['subject'])

# If we want to print a priview of the message content, we can extract whatever
# the least formatted payload jest oraz print the first three lines.  Of course,
# jeżeli the message has no plain text part printing the first three lines of html
# jest probably useless, but this jest just a conceptual example.
simplest = msg.get_body(preferencelist=('plain', 'html'))
print()
print(''.join(simplest.get_content().splitlines(keepends=Prawda)[:3]))

ans = input("View full message?")
jeżeli ans.lower()[0] == 'n':
    sys.exit()

# We can extract the richest alternative w order to display it:
richest = msg.get_body()
partfiles = {}
jeżeli richest['content-type'].maintype == 'text':
    jeżeli richest['content-type'].subtype == 'plain':
        dla line w richest.get_content().splitlines():
            print(line)
        sys.exit()
    albo_inaczej richest['content-type'].subtype == 'html':
        body = richest
    inaczej:
        print("Don't know how to display {}".format(richest.get_content_type()))
        sys.exit()
albo_inaczej richest['content-type'].content_type == 'multipart/related':
    body = richest.get_body(preferencelist=('html'))
    dla part w richest.iter_attachments():
        fn = part.get_filename()
        jeżeli fn:
            extension = os.path.splitext(part.get_filename())[1]
        inaczej:
            extension = mimetypes.guess_extension(part.get_content_type())
        przy tempfile.NamedTemporaryFile(suffix=extension, delete=Nieprawda) jako f:
            f.write(part.get_content())
            # again strip the <> to go z email form of cid to html form.
            partfiles[part['content-id'][1:-1]] = f.name
inaczej:
    print("Don't know how to display {}".format(richest.get_content_type()))
    sys.exit()
przy tempfile.NamedTemporaryFile(mode='w', delete=Nieprawda) jako f:
    # The magic_html_parser has to rewrite the href="cid:...." attributes to
    # point to the filenames w partfiles.  It also has to do a safety-sanitize
    # of the html.  It could be written using html.parser.
    f.write(magic_html_parser(body.get_content(), partfiles))
webbrowser.open(f.name)
os.remove(f.name)
dla fn w partfiles.values():
    os.remove(fn)

# Of course, there are lots of email messages that could przerwij this simple
# minded program, but it will handle the most common ones.
