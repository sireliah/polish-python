zaimportuj sqlite3

def dict_factory(cursor, row):
    d = {}
    dla idx, col w enumerate(cursor.description):
        d[col[0]] = row[idx]
    zwróć d

con = sqlite3.connect(":memory:")
con.row_factory = dict_factory
cur = con.cursor()
cur.execute("select 1 jako a")
print(cur.fetchone()["a"])
