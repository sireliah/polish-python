# Simple example presenting how persistent ID can be used to pickle
# external objects by reference.

zaimportuj pickle
zaimportuj sqlite3
z collections zaimportuj namedtuple

# Simple klasa representing a record w our database.
MemoRecord = namedtuple("MemoRecord", "key, task")

klasa DBPickler(pickle.Pickler):

    def persistent_id(self, obj):
        # Instead of pickling MemoRecord jako a regular klasa instance, we emit a
        # persistent ID.
        jeżeli isinstance(obj, MemoRecord):
            # Here, our persistent ID jest simply a tuple, containing a tag oraz a
            # key, which refers to a specific record w the database.
            zwróć ("MemoRecord", obj.key)
        inaczej:
            # If obj does nie have a persistent ID, zwróć Nic. This means obj
            # needs to be pickled jako usual.
            zwróć Nic


klasa DBUnpickler(pickle.Unpickler):

    def __init__(self, file, connection):
        super().__init__(file)
        self.connection = connection

    def persistent_load(self, pid):
        # This method jest invoked whenever a persistent ID jest encountered.
        # Here, pid jest the tuple returned by DBPickler.
        cursor = self.connection.cursor()
        type_tag, key_id = pid
        jeżeli type_tag == "MemoRecord":
            # Fetch the referenced record z the database oraz zwróć it.
            cursor.execute("SELECT * FROM memos WHERE key=?", (str(key_id),))
            key, task = cursor.fetchone()
            zwróć MemoRecord(key, task)
        inaczej:
            # Always podnieśs an error jeżeli you cannot zwróć the correct object.
            # Otherwise, the unpickler will think Nic jest the object referenced
            # by the persistent ID.
            podnieś pickle.UnpicklingError("unsupported persistent object")


def main():
    zaimportuj io
    zaimportuj pprint

    # Initialize oraz populate our database.
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE memos(key INTEGER PRIMARY KEY, task TEXT)")
    tasks = (
        'give food to fish',
        'prepare group meeting',
        'fight przy a zebra',
        )
    dla task w tasks:
        cursor.execute("INSERT INTO memos VALUES(NULL, ?)", (task,))

    # Fetch the records to be pickled.
    cursor.execute("SELECT * FROM memos")
    memos = [MemoRecord(key, task) dla key, task w cursor]
    # Save the records using our custom DBPickler.
    file = io.BytesIO()
    DBPickler(file).dump(memos)

    print("Pickled records:")
    pprint.pprint(memos)

    # Update a record, just dla good measure.
    cursor.execute("UPDATE memos SET task='learn italian' WHERE key=1")

    # Load the records z the pickle data stream.
    file.seek(0)
    memos = DBUnpickler(file, conn).load()

    print("Unpickled records:")
    pprint.pprint(memos)


jeżeli __name__ == '__main__':
    main()
