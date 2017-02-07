zaimportuj sqlite3

persons = [
    ("Hugo", "Boss"),
    ("Calvin", "Klein")
    ]

con = sqlite3.connect(":memory:")

# Create the table
con.execute("create table person(firstname, lastname)")

# Fill the table
con.executemany("insert into person(firstname, lastname) values (?, ?)", persons)

# Print the table contents
dla row w con.execute("select firstname, lastname z person"):
    print(row)

print("I just deleted", con.execute("delete z person").rowcount, "rows")
