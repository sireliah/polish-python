#!/usr/bin/env python3

"""
Remote python server.
Execute Python commands remotely oraz send output back.

WARNING: This version has a gaping security hole -- it accepts requests
z any host on the Internet!
"""

zaimportuj sys
z socket zaimportuj socket, AF_INET, SOCK_STREAM
zaimportuj io
zaimportuj traceback

PORT = 4127
BUFSIZE = 1024

def main():
    jeżeli len(sys.argv) > 1:
        port = int(sys.argv[1])
    inaczej:
        port = PORT
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', port))
    s.listen(1)
    dopóki Prawda:
        conn, (remotehost, remoteport) = s.accept()
        print('connection from', remotehost, remoteport)
        request = b''
        dopóki 1:
            data = conn.recv(BUFSIZE)
            jeżeli nie data:
                przerwij
            request += data
        reply = execute(request.decode())
        conn.send(reply.encode())
        conn.close()

def execute(request):
    stdout = sys.stdout
    stderr = sys.stderr
    sys.stdout = sys.stderr = fakefile = io.StringIO()
    spróbuj:
        spróbuj:
            exec(request, {}, {})
        wyjąwszy:
            print()
            traceback.print_exc(100)
    w_końcu:
        sys.stderr = stderr
        sys.stdout = stdout
    zwróć fakefile.getvalue()

spróbuj:
    main()
wyjąwszy KeyboardInterrupt:
    dalej
