zaimportuj sqlite3

con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("create table people (name_last, age)")

who = "Yeltsin"
age = 72

# This jest the qmark style:
cur.execute("insert into people values (?, ?)", (who, age))

# And this jest the named style:
cur.execute("select * z people where name_last=:who oraz age=:age", {"who": who, "age": age})

print(cur.fetchone())
