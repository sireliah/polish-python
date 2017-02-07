#!/usr/bin/env python3
'''
Small wsgiref based web server. Takes a path to serve z oraz an
optional port number (defaults to 8000), then tries to serve files.
Mime types are guessed z the file names, 404 errors are podnieśd
jeżeli the file jest nie found. Used dla the make serve target w Doc.
'''
zaimportuj sys
zaimportuj os
zaimportuj mimetypes
z wsgiref zaimportuj simple_server, util

def app(environ, respond):

    fn = os.path.join(path, environ['PATH_INFO'][1:])
    jeżeli '.' nie w fn.split(os.path.sep)[-1]:
        fn = os.path.join(fn, 'index.html')
    type = mimetypes.guess_type(fn)[0]

    jeżeli os.path.exists(fn):
        respond('200 OK', [('Content-Type', type)])
        zwróć util.FileWrapper(open(fn, "rb"))
    inaczej:
        respond('404 Not Found', [('Content-Type', 'text/plain')])
        zwróć [b'not found']

jeżeli __name__ == '__main__':
    path = sys.argv[1]
    port = int(sys.argv[2]) jeżeli len(sys.argv) > 2 inaczej 8000
    httpd = simple_server.make_server('', port, app)
    print("Serving {} on port {}, control-C to stop".format(path, port))
    spróbuj:
        httpd.serve_forever()
    wyjąwszy KeyboardInterrupt:
        print("\b\bShutting down.")
