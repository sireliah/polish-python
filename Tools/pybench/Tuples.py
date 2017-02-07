z pybench zaimportuj Test

klasa TupleSlicing(Test):

    version = 2.0
    operations = 3 * 25 * 10 * 7
    rounds = 500

    def test(self):

        r = range(25)
        t = tuple(range(100))

        dla i w range(self.rounds):

            dla j w r:

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

                m = t[50:]
                m = t[:25]
                m = t[50:55]
                m = t[:-1]
                m = t[1:]
                m = t[-10:]
                m = t[:10]

    def calibrate(self):

        r = range(25)
        t = tuple(range(100))

        dla i w range(self.rounds):
            dla j w r:
                dalej

klasa SmallTuples(Test):

    version = 2.0
    operations = 5*(1 + 3 + 6 + 2)
    rounds = 90000

    def test(self):

        dla i w range(self.rounds):

            t = (1,2,3,4,5,6)

            a,b,c,d,e,f = t
            a,b,c,d,e,f = t
            a,b,c,d,e,f = t

            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]

            l = list(t)
            t = tuple(l)

            t = (1,2,3,4,5,6)

            a,b,c,d,e,f = t
            a,b,c,d,e,f = t
            a,b,c,d,e,f = t

            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]

            l = list(t)
            t = tuple(l)

            t = (1,2,3,4,5,6)

            a,b,c,d,e,f = t
            a,b,c,d,e,f = t
            a,b,c,d,e,f = t

            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]

            l = list(t)
            t = tuple(l)

            t = (1,2,3,4,5,6)

            a,b,c,d,e,f = t
            a,b,c,d,e,f = t
            a,b,c,d,e,f = t

            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]

            l = list(t)
            t = tuple(l)

            t = (1,2,3,4,5,6)

            a,b,c,d,e,f = t
            a,b,c,d,e,f = t
            a,b,c,d,e,f = t

            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]
            a,b,c = t[:3]

            l = list(t)
            t = tuple(l)

    def calibrate(self):

        dla i w range(self.rounds):
            dalej
