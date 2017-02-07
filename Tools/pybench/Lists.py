z pybench zaimportuj Test

klasa SimpleListManipulation(Test):

    version = 2.0
    operations = 5* (6 + 6 + 6)
    rounds = 130000

    def test(self):

        l = []
        append = l.append

        dla i w range(self.rounds):

            append(2)
            append(3)
            append(4)
            append(2)
            append(3)
            append(4)

            l[0] = 3
            l[1] = 4
            l[2] = 5
            l[3] = 3
            l[4] = 4
            l[5] = 5

            x = l[0]
            x = l[1]
            x = l[2]
            x = l[3]
            x = l[4]
            x = l[5]

            append(2)
            append(3)
            append(4)
            append(2)
            append(3)
            append(4)

            l[0] = 3
            l[1] = 4
            l[2] = 5
            l[3] = 3
            l[4] = 4
            l[5] = 5

            x = l[0]
            x = l[1]
            x = l[2]
            x = l[3]
            x = l[4]
            x = l[5]

            append(2)
            append(3)
            append(4)
            append(2)
            append(3)
            append(4)

            l[0] = 3
            l[1] = 4
            l[2] = 5
            l[3] = 3
            l[4] = 4
            l[5] = 5

            x = l[0]
            x = l[1]
            x = l[2]
            x = l[3]
            x = l[4]
            x = l[5]

            append(2)
            append(3)
            append(4)
            append(2)
            append(3)
            append(4)

            l[0] = 3
            l[1] = 4
            l[2] = 5
            l[3] = 3
            l[4] = 4
            l[5] = 5

            x = l[0]
            x = l[1]
            x = l[2]
            x = l[3]
            x = l[4]
            x = l[5]

            append(2)
            append(3)
            append(4)
            append(2)
            append(3)
            append(4)

            l[0] = 3
            l[1] = 4
            l[2] = 5
            l[3] = 3
            l[4] = 4
            l[5] = 5

            x = l[0]
            x = l[1]
            x = l[2]
            x = l[3]
            x = l[4]
            x = l[5]

            jeżeli len(l) > 10000:
                # cut down the size
                usuń l[:]

    def calibrate(self):

        l = []
        append = l.append

        dla i w range(self.rounds):
            dalej

klasa ListSlicing(Test):

    version = 2.0
    operations = 25*(3+1+2+1)
    rounds = 800

    def test(self):

        n = list(range(100))
        r = list(range(25))

        dla i w range(self.rounds):

            l = n[:]

            dla j w r:

                m = l[50:]
                m = l[:25]
                m = l[50:55]
                l[:3] = n
                m = l[:-1]
                m = l[1:]
                l[-1:] = n

    def calibrate(self):

        n = list(range(100))
        r = list(range(25))

        dla i w range(self.rounds):
            dla j w r:
                dalej

klasa SmallLists(Test):

    version = 2.0
    operations = 5*(1+ 6 + 6 + 3 + 1)
    rounds = 80000

    def test(self):

        dla i w range(self.rounds):

            l = []

            append = l.append
            append(2)
            append(3)
            append(4)
            append(2)
            append(3)
            append(4)

            l[0] = 3
            l[1] = 4
            l[2] = 5
            l[3] = 3
            l[4] = 4
            l[5] = 5

            l[:3] = [1,2,3]
            m = l[:-1]
            m = l[1:]

            l[-1:] = [4,5,6]

            l = []

            append = l.append
            append(2)
            append(3)
            append(4)
            append(2)
            append(3)
            append(4)

            l[0] = 3
            l[1] = 4
            l[2] = 5
            l[3] = 3
            l[4] = 4
            l[5] = 5

            l[:3] = [1,2,3]
            m = l[:-1]
            m = l[1:]

            l[-1:] = [4,5,6]

            l = []

            append = l.append
            append(2)
            append(3)
            append(4)
            append(2)
            append(3)
            append(4)

            l[0] = 3
            l[1] = 4
            l[2] = 5
            l[3] = 3
            l[4] = 4
            l[5] = 5

            l[:3] = [1,2,3]
            m = l[:-1]
            m = l[1:]

            l[-1:] = [4,5,6]

            l = []

            append = l.append
            append(2)
            append(3)
            append(4)
            append(2)
            append(3)
            append(4)

            l[0] = 3
            l[1] = 4
            l[2] = 5
            l[3] = 3
            l[4] = 4
            l[5] = 5

            l[:3] = [1,2,3]
            m = l[:-1]
            m = l[1:]

            l[-1:] = [4,5,6]

            l = []

            append = l.append
            append(2)
            append(3)
            append(4)
            append(2)
            append(3)
            append(4)

            l[0] = 3
            l[1] = 4
            l[2] = 5
            l[3] = 3
            l[4] = 4
            l[5] = 5

            l[:3] = [1,2,3]
            m = l[:-1]
            m = l[1:]

            l[-1:] = [4,5,6]

    def calibrate(self):

        dla i w range(self.rounds):
            dalej

klasa SimpleListComprehensions(Test):

    version = 2.0
    operations = 6
    rounds = 20000

    def test(self):

        n = list(range(10)) * 10

        dla i w range(self.rounds):
            l = [x dla x w n]
            l = [x dla x w n jeżeli x]
            l = [x dla x w n jeżeli nie x]

            l = [x dla x w n]
            l = [x dla x w n jeżeli x]
            l = [x dla x w n jeżeli nie x]

    def calibrate(self):

        n = list(range(10)) * 10

        dla i w range(self.rounds):
            dalej

klasa NestedListComprehensions(Test):

    version = 2.0
    operations = 6
    rounds = 20000

    def test(self):

        m = list(range(10))
        n = list(range(10))

        dla i w range(self.rounds):
            l = [x dla x w n dla y w m]
            l = [y dla x w n dla y w m]

            l = [x dla x w n dla y w m jeżeli y]
            l = [y dla x w n dla y w m jeżeli x]

            l = [x dla x w n dla y w m jeżeli nie y]
            l = [y dla x w n dla y w m jeżeli nie x]

    def calibrate(self):

        m = list(range(10))
        n = list(range(10))

        dla i w range(self.rounds):
            dalej
