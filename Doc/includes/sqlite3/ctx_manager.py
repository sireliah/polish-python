zaimportuj sqlite3

con = sqlite3.connect(":memory:")
con.execute("create table person (id integer primary key, firstname varchar unique)")

# Successful, con.commit() jest called automatically afterwards
przy con:
    con.execute("insert into person(firstname) values (?)", ("Joe",))

# con.rollback() jest called after the przy block finishes przy an exception, the
# exception jest still podnieśd oraz must be caught
spróbuj:
    przy con:
        con.execute("insert into person(firstname) values (?)", ("Joe",))
wyjąwszy sqlite3.IntegrityError:
    print("couldn't add Joe twice")
