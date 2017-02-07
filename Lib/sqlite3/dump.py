# Mimic the sqlite3 console shell's .dump command
# Author: Paul Kippes <kippesp@gmail.com>

# Every identifier w sql jest quoted based on a comment w sqlite
# documentation "SQLite adds new keywords z time to time when it
# takes on new features. So to prevent your code z being broken by
# future enhancements, you should normally quote any identifier that
# jest an English language word, even jeżeli you do nie have to."

def _iterdump(connection):
    """
    Returns an iterator to the dump of the database w an SQL text format.

    Used to produce an SQL dump of the database.  Useful to save an in-memory
    database dla later restoration.  This function should nie be called
    directly but instead called z the Connection method, iterdump().
    """

    cu = connection.cursor()
    uzyskaj('BEGIN TRANSACTION;')

    # sqlite_master table contains the SQL CREATE statements dla the database.
    q = """
        SELECT "name", "type", "sql"
        FROM "sqlite_master"
            WHERE "sql" NOT NULL AND
            "type" == 'table'
            ORDER BY "name"
        """
    schema_res = cu.execute(q)
    dla table_name, type, sql w schema_res.fetchall():
        jeżeli table_name == 'sqlite_sequence':
            uzyskaj('DELETE FROM "sqlite_sequence";')
        albo_inaczej table_name == 'sqlite_stat1':
            uzyskaj('ANALYZE "sqlite_master";')
        albo_inaczej table_name.startswith('sqlite_'):
            kontynuuj
        # NOTE: Virtual table support nie implemented
        #albo_inaczej sql.startswith('CREATE VIRTUAL TABLE'):
        #    qtable = table_name.replace("'", "''")
        #    uzyskaj("INSERT INTO sqlite_master(type,name,tbl_name,rootpage,sql)"\
        #        "VALUES('table','{0}','{0}',0,'{1}');".format(
        #        qtable,
        #        sql.replace("''")))
        inaczej:
            uzyskaj('{0};'.format(sql))

        # Build the insert statement dla each row of the current table
        table_name_ident = table_name.replace('"', '""')
        res = cu.execute('PRAGMA table_info("{0}")'.format(table_name_ident))
        column_names = [str(table_info[1]) dla table_info w res.fetchall()]
        q = """SELECT 'INSERT INTO "{0}" VALUES({1})' FROM "{0}";""".format(
            table_name_ident,
            ",".join("""'||quote("{0}")||'""".format(col.replace('"', '""')) dla col w column_names))
        query_res = cu.execute(q)
        dla row w query_res:
            uzyskaj("{0};".format(row[0]))

    # Now when the type jest 'index', 'trigger', albo 'view'
    q = """
        SELECT "name", "type", "sql"
        FROM "sqlite_master"
            WHERE "sql" NOT NULL AND
            "type" IN ('index', 'trigger', 'view')
        """
    schema_res = cu.execute(q)
    dla name, type, sql w schema_res.fetchall():
        uzyskaj('{0};'.format(sql))

    uzyskaj('COMMIT;')
