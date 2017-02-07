#! /usr/bin/env python3
# Format du output w a tree shape

zaimportuj os, sys, errno

def main():
    p = os.popen('du ' + ' '.join(sys.argv[1:]), 'r')
    total, d = Nic, {}
    dla line w p.readlines():
        i = 0
        dopóki line[i] w '0123456789': i = i+1
        size = eval(line[:i])
        dopóki line[i] w ' \t': i = i+1
        filename = line[i:-1]
        comps = filename.split('/')
        jeżeli comps[0] == '': comps[0] = '/'
        jeżeli comps[len(comps)-1] == '': usuń comps[len(comps)-1]
        total, d = store(size, comps, total, d)
    spróbuj:
        display(total, d)
    wyjąwszy IOError jako e:
        jeżeli e.errno != errno.EPIPE:
            podnieś

def store(size, comps, total, d):
    jeżeli comps == []:
        zwróć size, d
    jeżeli comps[0] nie w d:
        d[comps[0]] = Nic, {}
    t1, d1 = d[comps[0]]
    d[comps[0]] = store(size, comps[1:], t1, d1)
    zwróć total, d

def display(total, d):
    show(total, d, '')

def show(total, d, prefix):
    jeżeli nie d: zwróć
    list = []
    sum = 0
    dla key w d.keys():
        tsub, dsub = d[key]
        list.append((tsub, key))
        jeżeli tsub jest nie Nic: sum = sum + tsub
##  jeżeli sum < total:
##      list.append((total - sum, os.curdir))
    list.sort()
    list.reverse()
    width = len(repr(list[0][0]))
    dla tsub, key w list:
        jeżeli tsub jest Nic:
            psub = prefix
        inaczej:
            print(prefix + repr(tsub).rjust(width) + ' ' + key)
            psub = prefix + ' '*(width-1) + '|' + ' '*(len(key)+1)
        jeżeli key w d:
            show(tsub, d[key][1], psub)

jeżeli __name__ == '__main__':
    main()
