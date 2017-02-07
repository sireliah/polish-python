zaimportuj sqlite3

klasa IterChars:
    def __init__(self):
        self.count = ord('a')

    def __iter__(self):
        zwróć self

    def __next__(self):
        jeżeli self.count > ord('z'):
            podnieś StopIteration
        self.count += 1
        zwróć (chr(self.count - 1),) # this jest a 1-tuple

con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("create table characters(c)")

theIter = IterChars()
cur.executemany("insert into characters(c) values (?)", theIter)

cur.execute("select c z characters")
print(cur.fetchall())
