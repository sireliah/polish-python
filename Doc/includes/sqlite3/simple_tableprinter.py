zaimportuj sqlite3

FIELD_MAX_WIDTH = 20
TABLE_NAME = 'people'
SELECT = 'select * z %s order by age, name_last' % TABLE_NAME

con = sqlite3.connect("mydb")

cur = con.cursor()
cur.execute(SELECT)

# Print a header.
dla fieldDesc w cur.description:
    print(fieldDesc[0].ljust(FIELD_MAX_WIDTH), end=' ')
print() # Finish the header przy a newline.
print('-' * 78)

# For each row, print the value of each field left-justified within
# the maximum possible width of that field.
fieldIndices = range(len(cur.description))
dla row w cur:
    dla fieldIndex w fieldIndices:
        fieldValue = str(row[fieldIndex])
        print(fieldValue.ljust(FIELD_MAX_WIDTH), end=' ')

    print() # Finish the row przy a newline.
