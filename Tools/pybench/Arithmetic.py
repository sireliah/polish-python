z pybench zaimportuj Test

klasa SimpleIntegerArithmetic(Test):

    version = 2.0
    operations = 5 * (3 + 5 + 5 + 3 + 3 + 3)
    rounds = 120000

    def test(self):

        dla i w range(self.rounds):

            a = 2
            b = 3
            c = 3

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2
            b = 3
            c = 3

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2
            b = 3
            c = 3

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2
            b = 3
            c = 3

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2
            b = 3
            c = 3

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

    def calibrate(self):

        dla i w range(self.rounds):
            dalej

klasa SimpleFloatArithmetic(Test):

    version = 2.0
    operations = 5 * (3 + 5 + 5 + 3 + 3 + 3)
    rounds = 120000

    def test(self):

        dla i w range(self.rounds):

            a = 2.1
            b = 3.3332
            c = 3.14159

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2.1
            b = 3.3332
            c = 3.14159

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2.1
            b = 3.3332
            c = 3.14159

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2.1
            b = 3.3332
            c = 3.14159

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2.1
            b = 3.3332
            c = 3.14159

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

    def calibrate(self):

        dla i w range(self.rounds):
            dalej

klasa SimpleIntFloatArithmetic(Test):

    version = 2.0
    operations = 5 * (3 + 5 + 5 + 3 + 3 + 3)
    rounds = 120000

    def test(self):

        dla i w range(self.rounds):

            a = 2
            b = 3
            c = 3.14159

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2
            b = 3
            c = 3.14159

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2
            b = 3
            c = 3.14159

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2
            b = 3
            c = 3.14159

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2
            b = 3
            c = 3.14159

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

    def calibrate(self):

        dla i w range(self.rounds):
            dalej


klasa SimpleLongArithmetic(Test):

    version = 2.0
    operations = 5 * (3 + 5 + 5 + 3 + 3 + 3)
    rounds = 60000

    def test(self):

        dla i w range(self.rounds):

            a = 2220001
            b = 100001
            c = 30005

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2220001
            b = 100001
            c = 30005

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2220001
            b = 100001
            c = 30005

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2220001
            b = 100001
            c = 30005

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2220001
            b = 100001
            c = 30005

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

    def calibrate(self):

        dla i w range(self.rounds):
            dalej

klasa SimpleComplexArithmetic(Test):

    version = 2.0
    operations = 5 * (3 + 5 + 5 + 3 + 3 + 3)
    rounds = 80000

    def test(self):

        dla i w range(self.rounds):

            a = 2 + 3j
            b = 2.5 + 4.5j
            c = 1.2 + 6.2j

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2 + 3j
            b = 2.5 + 4.5j
            c = 1.2 + 6.2j

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2 + 3j
            b = 2.5 + 4.5j
            c = 1.2 + 6.2j

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2 + 3j
            b = 2.5 + 4.5j
            c = 1.2 + 6.2j

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

            a = 2 + 3j
            b = 2.5 + 4.5j
            c = 1.2 + 6.2j

            c = a + b
            c = b + c
            c = c + a
            c = a + b
            c = b + c

            c = c - a
            c = a - b
            c = b - c
            c = c - a
            c = b - c

            c = a / b
            c = b / a
            c = c / b

            c = a * b
            c = b * a
            c = c * b

            c = a / b
            c = b / a
            c = c / b

    def calibrate(self):

        dla i w range(self.rounds):
            dalej
