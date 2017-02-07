zaimportuj sqlite3
zaimportuj string

def char_generator():
    dla c w string.ascii_lowercase:
        uzyskaj (c,)

con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("create table characters(c)")

cur.executemany("insert into characters(c) values (?)", char_generator())

cur.execute("select c z characters")
print(cur.fetchall())
