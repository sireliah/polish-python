#! /usr/bin/env python3
"Replace CRLF przy LF w argument files.  Print names of changed files."

zaimportuj sys, os

def main():
    dla filename w sys.argv[1:]:
        jeżeli os.path.isdir(filename):
            print(filename, "Directory!")
            kontynuuj
        przy open(filename, "rb") jako f:
            data = f.read()
        jeżeli b'\0' w data:
            print(filename, "Binary!")
            kontynuuj
        newdata = data.replace(b"\r\n", b"\n")
        jeżeli newdata != data:
            print(filename)
            przy open(filename, "wb") jako f:
                f.write(newdata)

jeżeli __name__ == '__main__':
    main()
