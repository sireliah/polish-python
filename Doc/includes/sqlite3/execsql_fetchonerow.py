zaimportuj sqlite3

con = sqlite3.connect("mydb")

cur = con.cursor()
SELECT = "select name_last, age z people order by age, name_last"

# 1. Iterate over the rows available z the cursor, unpacking the
# resulting sequences to uzyskaj their elements (name_last, age):
cur.execute(SELECT)
dla (name_last, age) w cur:
    print('%s jest %d years old.' % (name_last, age))

# 2. Equivalently:
cur.execute(SELECT)
dla row w cur:
    print('%s jest %d years old.' % (row[0], row[1]))
