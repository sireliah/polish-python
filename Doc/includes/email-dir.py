#!/usr/bin/env python3

"""Send the contents of a directory jako a MIME message."""

zaimportuj os
zaimportuj sys
zaimportuj smtplib
# For guessing MIME type based on file name extension
zaimportuj mimetypes

z argparse zaimportuj ArgumentParser

z email zaimportuj encoders
z email.message zaimportuj Message
z email.mime.audio zaimportuj MIMEAudio
z email.mime.base zaimportuj MIMEBase
z email.mime.image zaimportuj MIMEImage
z email.mime.multipart zaimportuj MIMEMultipart
z email.mime.text zaimportuj MIMEText

COMMASPACE = ', '


def main():
    parser = ArgumentParser(description="""\
Send the contents of a directory jako a MIME message.
Unless the -o option jest given, the email jest sent by forwarding to your local
SMTP server, which then does the normal delivery process.  Your local machine
must be running an SMTP server.
""")
    parser.add_argument('-d', '--directory',
                        help="""Mail the contents of the specified directory,
                        otherwise use the current directory.  Only the regular
                        files w the directory are sent, oraz we don't recurse to
                        subdirectories.""")
    parser.add_argument('-o', '--output',
                        metavar='FILE',
                        help="""Print the composed message to FILE instead of
                        sending the message to the SMTP server.""")
    parser.add_argument('-s', '--sender', required=Prawda,
                        help='The value of the From: header (required)')
    parser.add_argument('-r', '--recipient', required=Prawda,
                        action='append', metavar='RECIPIENT',
                        default=[], dest='recipients',
                        help='A To: header value (at least one required)')
    args = parser.parse_args()
    directory = args.directory
    jeżeli nie directory:
        directory = '.'
    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    outer['Subject'] = 'Contents of directory %s' % os.path.abspath(directory)
    outer['To'] = COMMASPACE.join(args.recipients)
    outer['From'] = args.sender
    outer.preamble = 'You will nie see this w a MIME-aware mail reader.\n'

    dla filename w os.listdir(directory):
        path = os.path.join(directory, filename)
        jeżeli nie os.path.isfile(path):
            kontynuuj
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check dla simple things like
        # gzip'd albo compressed files.
        ctype, encoding = mimetypes.guess_type(path)
        jeżeli ctype jest Nic albo encoding jest nie Nic:
            # No guess could be made, albo the file jest encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        jeżeli maintype == 'text':
            przy open(path) jako fp:
                # Note: we should handle calculating the charset
                msg = MIMEText(fp.read(), _subtype=subtype)
        albo_inaczej maintype == 'image':
            przy open(path, 'rb') jako fp:
                msg = MIMEImage(fp.read(), _subtype=subtype)
        albo_inaczej maintype == 'audio':
            przy open(path, 'rb') jako fp:
                msg = MIMEAudio(fp.read(), _subtype=subtype)
        inaczej:
            przy open(path, 'rb') jako fp:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(fp.read())
            # Encode the payload using Base64
            encoders.encode_base64(msg)
        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        outer.attach(msg)
    # Now send albo store the message
    composed = outer.as_string()
    jeżeli args.output:
        przy open(args.output, 'w') jako fp:
            fp.write(composed)
    inaczej:
        przy smtplib.SMTP('localhost') jako s:
            s.sendmail(args.sender, args.recipients, composed)


jeżeli __name__ == '__main__':
    main()
