#! /usr/bin/env python3

"""Script to synchronize two source trees.

Invoke przy two arguments:

python treesync.py slave master

The assumption jest that "master" contains CVS administration while
slave doesn't.  All files w the slave tree that have a CVS/Entries
entry w the master tree are synchronized.  This means:

    If the files differ:
        jeżeli the slave file jest newer:
            normalize the slave file
            jeżeli the files still differ:
                copy the slave to the master
        inaczej (the master jest newer):
            copy the master to the slave

    normalizing the slave means replacing CRLF przy LF when the master
    doesn't use CRLF

"""

zaimportuj os, sys, stat, getopt

# Interactivity options
default_answer = "ask"
create_files = "yes"
create_directories = "no"
write_slave = "ask"
write_master = "ask"

def main():
    global always_no, always_yes
    global create_directories, write_master, write_slave
    opts, args = getopt.getopt(sys.argv[1:], "nym:s:d:f:a:")
    dla o, a w opts:
        jeżeli o == '-y':
            default_answer = "yes"
        jeżeli o == '-n':
            default_answer = "no"
        jeżeli o == '-s':
            write_slave = a
        jeżeli o == '-m':
            write_master = a
        jeżeli o == '-d':
            create_directories = a
        jeżeli o == '-f':
            create_files = a
        jeżeli o == '-a':
            create_files = create_directories = write_slave = write_master = a
    spróbuj:
        [slave, master] = args
    wyjąwszy ValueError:
        print("usage: python", sys.argv[0] albo "treesync.py", end=' ')
        print("[-n] [-y] [-m y|n|a] [-s y|n|a] [-d y|n|a] [-f n|y|a]", end=' ')
        print("slavedir masterdir")
        zwróć
    process(slave, master)

def process(slave, master):
    cvsdir = os.path.join(master, "CVS")
    jeżeli nie os.path.isdir(cvsdir):
        print("skipping master subdirectory", master)
        print("-- nie under CVS")
        zwróć
    print("-"*40)
    print("slave ", slave)
    print("master", master)
    jeżeli nie os.path.isdir(slave):
        jeżeli nie okay("create slave directory %s?" % slave,
                    answer=create_directories):
            print("skipping master subdirectory", master)
            print("-- no corresponding slave", slave)
            zwróć
        print("creating slave directory", slave)
        spróbuj:
            os.mkdir(slave)
        wyjąwszy OSError jako msg:
            print("can't make slave directory", slave, ":", msg)
            zwróć
        inaczej:
            print("made slave directory", slave)
    cvsdir = Nic
    subdirs = []
    names = os.listdir(master)
    dla name w names:
        mastername = os.path.join(master, name)
        slavename = os.path.join(slave, name)
        jeżeli name == "CVS":
            cvsdir = mastername
        inaczej:
            jeżeli os.path.isdir(mastername) oraz nie os.path.islink(mastername):
                subdirs.append((slavename, mastername))
    jeżeli cvsdir:
        entries = os.path.join(cvsdir, "Entries")
        dla e w open(entries).readlines():
            words = e.split('/')
            jeżeli words[0] == '' oraz words[1:]:
                name = words[1]
                s = os.path.join(slave, name)
                m = os.path.join(master, name)
                compare(s, m)
    dla (s, m) w subdirs:
        process(s, m)

def compare(slave, master):
    spróbuj:
        sf = open(slave, 'r')
    wyjąwszy IOError:
        sf = Nic
    spróbuj:
        mf = open(master, 'rb')
    wyjąwszy IOError:
        mf = Nic
    jeżeli nie sf:
        jeżeli nie mf:
            print("Neither master nor slave exists", master)
            zwróć
        print("Creating missing slave", slave)
        copy(master, slave, answer=create_files)
        zwróć
    jeżeli nie mf:
        print("Not updating missing master", master)
        zwróć
    jeżeli sf oraz mf:
        jeżeli identical(sf, mf):
            zwróć
    sft = mtime(sf)
    mft = mtime(mf)
    jeżeli mft > sft:
        # Master jest newer -- copy master to slave
        sf.close()
        mf.close()
        print("Master             ", master)
        print("is newer than slave", slave)
        copy(master, slave, answer=write_slave)
        zwróć
    # Slave jest newer -- copy slave to master
    print("Slave is", sft-mft, "seconds newer than master")
    # But first check what to do about CRLF
    mf.seek(0)
    fun = funnychars(mf)
    mf.close()
    sf.close()
    jeżeli fun:
        print("***UPDATING MASTER (BINARY COPY)***")
        copy(slave, master, "rb", answer=write_master)
    inaczej:
        print("***UPDATING MASTER***")
        copy(slave, master, "r", answer=write_master)

BUFSIZE = 16*1024

def identical(sf, mf):
    dopóki 1:
        sd = sf.read(BUFSIZE)
        md = mf.read(BUFSIZE)
        jeżeli sd != md: zwróć 0
        jeżeli nie sd: przerwij
    zwróć 1

def mtime(f):
    st = os.fstat(f.fileno())
    zwróć st[stat.ST_MTIME]

def funnychars(f):
    dopóki 1:
        buf = f.read(BUFSIZE)
        jeżeli nie buf: przerwij
        jeżeli '\r' w buf albo '\0' w buf: zwróć 1
    zwróć 0

def copy(src, dst, rmode="rb", wmode="wb", answer='ask'):
    print("copying", src)
    print("     to", dst)
    jeżeli nie okay("okay to copy? ", answer):
        zwróć
    f = open(src, rmode)
    g = open(dst, wmode)
    dopóki 1:
        buf = f.read(BUFSIZE)
        jeżeli nie buf: przerwij
        g.write(buf)
    f.close()
    g.close()

def raw_input(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    zwróć sys.stdin.readline()

def okay(prompt, answer='ask'):
    answer = answer.strip().lower()
    jeżeli nie answer albo answer[0] nie w 'ny':
        answer = input(prompt)
        answer = answer.strip().lower()
        jeżeli nie answer:
            answer = default_answer
    jeżeli answer[:1] == 'y':
        zwróć 1
    jeżeli answer[:1] == 'n':
        zwróć 0
    print("Yes albo No please -- try again:")
    zwróć okay(prompt)

jeżeli __name__ == '__main__':
    main()
