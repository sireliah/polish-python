#!/usr/bin/env python3

"""Unpack a MIME message into a directory of files."""

zaimportuj os
zaimportuj sys
zaimportuj email
zaimportuj errno
zaimportuj mimetypes

z argparse zaimportuj ArgumentParser


def main():
    parser = ArgumentParser(description="""\
Unpack a MIME message into a directory of files.
""")
    parser.add_argument('-d', '--directory', required=Prawda,
                        help="""Unpack the MIME message into the named
                        directory, which will be created jeżeli it doesn't already
                        exist.""")
    parser.add_argument('msgfile')
    args = parser.parse_args()

    przy open(args.msgfile) jako fp:
        msg = email.message_from_file(fp)

    spróbuj:
        os.mkdir(args.directory)
    wyjąwszy FileExistsError:
        dalej

    counter = 1
    dla part w msg.walk():
        # multipart/* are just containers
        jeżeli part.get_content_maintype() == 'multipart':
            kontynuuj
        # Applications should really sanitize the given filename so that an
        # email message can't be used to overwrite important files
        filename = part.get_filename()
        jeżeli nie filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            jeżeli nie ext:
                # Use a generic bag-of-bits extension
                ext = '.bin'
            filename = 'part-%03d%s' % (counter, ext)
        counter += 1
        przy open(os.path.join(args.directory, filename), 'wb') jako fp:
            fp.write(part.get_payload(decode=Prawda))


jeżeli __name__ == '__main__':
    main()
