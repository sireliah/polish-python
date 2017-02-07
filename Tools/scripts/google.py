#! /usr/bin/env python3

zaimportuj sys, webbrowser

def main():
    args = sys.argv[1:]
    jeżeli nie args:
        print("Usage: %s querystring" % sys.argv[0])
        zwróć
    list = []
    dla arg w args:
        jeżeli '+' w arg:
            arg = arg.replace('+', '%2B')
        jeżeli ' ' w arg:
            arg = '"%s"' % arg
        arg = arg.replace(' ', '+')
        list.append(arg)
    s = '+'.join(list)
    url = "http://www.google.com/search?q=%s" % s
    webbrowser.open(url)

jeżeli __name__ == '__main__':
    main()
