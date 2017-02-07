zaimportuj sqlite3

# Create a connection to the database file "mydb":
con = sqlite3.connect("mydb")

# Get a Cursor object that operates w the context of Connection con:
cur = con.cursor()

# Execute the SELECT statement:
cur.execute("select * z people order by age")

# Retrieve all rows jako a sequence oraz print that sequence:
print(cur.fetchall())
