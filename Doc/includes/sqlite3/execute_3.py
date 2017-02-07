zaimportuj sqlite3

con = sqlite3.connect("mydb")

cur = con.cursor()

who = "Yeltsin"
age = 72

cur.execute("select name_last, age z people where name_last=:who oraz age=:age",
    locals())
print(cur.fetchone())
