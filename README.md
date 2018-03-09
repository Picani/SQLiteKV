SQLiteKV
========

SQLiteKV is a simple, single-file [key-value store][1] based on [SQLite 3][2].


Why?
----

I wanted to have an OS and language independent single-file key-value
database. By language independent, I mean at least the languages I use,
*i.e.* Python and Go. After using a bit [GDBM][3], it appears that it's not 
well supported by Go, and has some issue with the Anaconda environment.
SQLite was the only engine to be equally well supported everywhere.


How?
----

The database has two tables.

* `keys` that obviously contains the keys, and a foreign key to the
  corresponding value.

* `vals` that only contains the values.

The `key` column of the `keys` table is indexed, which guarantees a fast
finding, while slowing down the insertions. Having the keys and the values
in separated tables guarantees the database to not be too big if there are
far more keys than values, while complicating a bit the queries (and maybe
slowing down a bit the value retrieving).

Naming the tables always like this allows to make the store
language-independent.

Then, we follow the KISS philosophy: one file by programming language with
the same three functions.

* `get` to retrieve an a value from a key.
* `put` to add a key-value association.
* `del` to remove a key-value association.

However, this do not prevent from adding some language specific code to make
the interface more idiomatic.


Schema
------

The `keys` table:

~~~SQL
CREATE TABLE keys(
  key TEXT UNIQUE NOT NULL,
  valueID INTEGER NOT NULL,
  FOREIGN KEY(valueID) REFERENCES vals(ID))
~~~

The `vals` table:

~~~SQL
CREATE TABLE vals(
  ID INTEGER PRIMARY KEY ASC,
  value TEXT UNIQUE NOT NULL)
~~~

The `keys` index:

~~~SQL
CREATE UNIQUE INDEX idx_keys ON keys(key);
~~~


Simple Query
------------

To retrieve the value associated with the key *plop*:

~~~SQL
SELECT keys.key, vals.value FROM keys
INNER JOIN vals ON vals.ID=keys.valueID
WHERE keys.key='plop'
~~~


Licence
-------

Copyright © 2018 Sylvain PULICANI <picani@laposte.net>

This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the COPYING file for more details.

---

[1]: https://en.wikipedia.org/wiki/Key-value_database
[2]: https://www.sqlite.org/index.html
[3]: https://www.gnu.org.ua/software/gdbm/

