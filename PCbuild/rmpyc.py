# Remove all the .pyc oraz .pyo files under ../Lib.


def deltree(root):
    zaimportuj os
    z os.path zaimportuj join

    npyc = npyo = 0
    dla root, dirs, files w os.walk(root):
        dla name w files:
            delete = Nieprawda
            jeżeli name.endswith('.pyc'):
                delete = Prawda
                npyc += 1
            albo_inaczej name.endswith('.pyo'):
                delete = Prawda
                npyo += 1

            jeżeli delete:
                os.remove(join(root, name))

    zwróć npyc, npyo

npyc, npyo = deltree("../Lib")
print(npyc, ".pyc deleted,", npyo, ".pyo deleted")
