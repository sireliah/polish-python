zaimportuj sqlite3

def collate_reverse(string1, string2):
    jeżeli string1 == string2:
        zwróć 0
    albo_inaczej string1 < string2:
        zwróć 1
    inaczej:
        zwróć -1

con = sqlite3.connect(":memory:")
con.create_collation("reverse", collate_reverse)

cur = con.cursor()
cur.execute("create table test(x)")
cur.executemany("insert into test(x) values (?)", [("a",), ("b",)])
cur.execute("select x z test order by x collate reverse")
dla row w cur:
    print(row)
con.close()
