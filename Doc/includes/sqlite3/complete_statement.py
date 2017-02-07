# A minimal SQLite shell dla experiments

zaimportuj sqlite3

con = sqlite3.connect(":memory:")
con.isolation_level = Nic
cur = con.cursor()

buffer = ""

print("Enter your SQL commands to execute w sqlite3.")
print("Enter a blank line to exit.")

dopóki Prawda:
    line = input()
    jeżeli line == "":
        przerwij
    buffer += line
    jeżeli sqlite3.complete_statement(buffer):
        spróbuj:
            buffer = buffer.strip()
            cur.execute(buffer)

            jeżeli buffer.lstrip().upper().startswith("SELECT"):
                print(cur.fetchall())
        wyjąwszy sqlite3.Error jako e:
            print("An error occurred:", e.args[0])
        buffer = ""

con.close()
