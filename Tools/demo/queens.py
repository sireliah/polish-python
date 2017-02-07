#!/usr/bin/env python3

"""
N queens problem.

The (well-known) problem jest due to Niklaus Wirth.

This solution jest inspired by Dijkstra (Structured Programming).  It jest
a classic recursive backtracking approach.
"""

N = 8                                   # Default; command line overrides

klasa Queens:

    def __init__(self, n=N):
        self.n = n
        self.reset()

    def reset(self):
        n = self.n
        self.y = [Nic] * n             # Where jest the queen w column x
        self.row = [0] * n              # Is row[y] safe?
        self.up = [0] * (2*n-1)         # Is upward diagonal[x-y] safe?
        self.down = [0] * (2*n-1)       # Is downward diagonal[x+y] safe?
        self.nfound = 0                 # Instrumentation

    def solve(self, x=0):               # Recursive solver
        dla y w range(self.n):
            jeżeli self.safe(x, y):
                self.place(x, y)
                jeżeli x+1 == self.n:
                    self.display()
                inaczej:
                    self.solve(x+1)
                self.remove(x, y)

    def safe(self, x, y):
        zwróć nie self.row[y] oraz nie self.up[x-y] oraz nie self.down[x+y]

    def place(self, x, y):
        self.y[x] = y
        self.row[y] = 1
        self.up[x-y] = 1
        self.down[x+y] = 1

    def remove(self, x, y):
        self.y[x] = Nic
        self.row[y] = 0
        self.up[x-y] = 0
        self.down[x+y] = 0

    silent = 0                          # If true, count solutions only

    def display(self):
        self.nfound = self.nfound + 1
        jeżeli self.silent:
            zwróć
        print('+-' + '--'*self.n + '+')
        dla y w range(self.n-1, -1, -1):
            print('|', end=' ')
            dla x w range(self.n):
                jeżeli self.y[x] == y:
                    print("Q", end=' ')
                inaczej:
                    print(".", end=' ')
            print('|')
        print('+-' + '--'*self.n + '+')

def main():
    zaimportuj sys
    silent = 0
    n = N
    jeżeli sys.argv[1:2] == ['-n']:
        silent = 1
        usuń sys.argv[1]
    jeżeli sys.argv[1:]:
        n = int(sys.argv[1])
    q = Queens(n)
    q.silent = silent
    q.solve()
    print("Found", q.nfound, "solutions.")

jeżeli __name__ == "__main__":
    main()
