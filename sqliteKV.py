# Copyright © 2018 Sylvain PULICANI <picani@laposte.net>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See the COPYING file for more details.

# sqlite_kv.py
#
# Python implementation of the SQLiteKV store.

import sqlite3


class KV:
    """
    Python implementation of the SQLiteKV store, with additionnal methods
    to make it more pythonic.

    ..Warning::
      * The `close` method has to be called after use.
      * The `delete` method is not yet implementated.
    """
    def __init__(self, dbfile):
        """
        Open a connection to the SQLite file. If it doesn't exists, create it
        and add the needed tables.
        """
        self.conn = None
        self.conn = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row

        tables = [dict(r)['name'] for r in self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")]

        if 'vals' not in tables:
            self.conn.execute("""CREATE TABLE vals(
                              ID INTEGER NOT NULL,
                              value TEXT,
                              PRIMARY KEY(ID))""")

            if 'keys' not in tables:
                self.conn.execute("""CREATE TABLE keys(
                                  key TEXT, valueID INTEGER,
                                  FOREIGN KEY(valueID) REFERENCES vals(ID))""")
                self.conn.execute("CREATE UNIQUE INDEX keys_index ON keys(key)")


    def close(self):
        """
        Properly close the database.
        """
        if self.conn is not None:
            self.conn.close()


    def __getitem__(self, key):
        rows = self.conn.execute("""SELECT keys.key, vals.value FROM keys
                               INNER JOIN vals ON vals.ID=keys.valueID
                               WHERE keys.key=(?)""", (key, ))
        row = rows.fetchone()
        if row is None:
            raise KeyError(key)
        return row['value']


    def get(self, key, default=None):
        """
        Returns the value associated with key, or default if key is not
        present.

        Can also be used with the dict-like notation:

            db[key]

        However, please note that this will raise `KeyError` if the key is
        not found.
        """
        rows = self.conn.execute("""SELECT keys.key, vals.value FROM keys
                               INNER JOIN vals ON vals.ID=keys.valueID
                               WHERE keys.key=(?)""", (key, ))
        row = rows.fetchone()
        if row is None:
            return default
        return row['value']


    def __setitem__(self, key, value):
        if self.get(key) is None:
            rows = self.conn.execute("""SELECT * FROM vals WHERE value=(?)""",
                                     (value, ))
            row = rows.fetchone()
            if row is None:
                self.conn.execute("INSERT INTO vals(value) VALUES (?)", (value, ))
                self.conn.commit()
                rows = self.conn.execute("""SELECT * FROM vals WHERE value=(?)""",
                                         (value, ))
                row = rows.fetchone()

            self.conn.execute("INSERT INTO keys(key, valueID) VALUES (?, ?)",
                         (key, row['ID']))
            self.conn.commit()


    def put(self, key, value):
        """
        Insert the key and the value, and associate them. If key is already
        present, then do nothing.

        Can also be used with the dict-like notation:

            db[key] = value
        """
        self[key] = value


    def delete(self, key):
        """
        Delete the key.
        """
        raise NotImplementedError
