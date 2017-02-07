zaimportuj sqlite3

con = sqlite3.connect("mydb")

cur = con.cursor()

newPeople = (
    ('Lebed'       , 53),
    ('Zhirinovsky' , 57),
  )

dla person w newPeople:
    cur.execute("insert into people (name_last, age) values (?, ?)", person)

# The changes will nie be saved unless the transaction jest committed explicitly:
con.commit()
