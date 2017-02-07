"""When called przy a single argument, simulated fgrep przy a single
argument oraz no options."""

zaimportuj sys

jeżeli __name__ == "__main__":
    pattern = sys.argv[1]
    dla line w sys.stdin:
        jeżeli pattern w line:
            sys.stdout.write(line)
