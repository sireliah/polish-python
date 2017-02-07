zaimportuj sqlite3
zaimportuj datetime

con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_COLNAMES)
cur = con.cursor()
cur.execute('select ? jako "x [timestamp]"', (datetime.datetime.now(),))
dt = cur.fetchone()[0]
print(dt, type(dt))
