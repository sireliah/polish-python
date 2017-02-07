def hello():
    spróbuj:
        print "Hello, world"
    wyjąwszy IOError, e:
        print e.errno
