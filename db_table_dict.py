# db_table_dict.py -- a dictionary emulator which maps to a database table
#
# Richard Brooksby, Ravenbrook Limited, 2004-01-22
#
# This is a dictionary class that can be instantiated as a way of accessing
# a table in a SQL database.  It can be applied to any database connection
# which complies to the "Python Database API Specification v2.0" [PEP 249].
#
# This is not a fully general mapping of a dictionary onto a table.  The
# dictionary must have keys which are tuples, and values which are tuples.
# The database table must have a primary key which corresponds to the
# elements of the key tuple.  Standard SQL apparently say that all tables
# have primary keys, but PostgreSQL, for example, doesn't enforce that.  To
# get a table that acts like a bag of relations in PostgreSQL, use the "oid"
# column as the key.
#
# See section 3.3.4, "Emulating container types" of "Python Reference Manual"
# [vanRossum 2002-03-29, s3.3.4]
# <http://www.python.org/doc/2.2p1/ref/sequence-types.html>.
#
#
# Supported operations:
#
# s[k]          __getitem__(k)
# s[k] = v      __setitem__(k, v)
# del s[k]      __delitem__(k)
# k in s        __contains__(k)
# k not in s    not __contains__(k)
#               has_key(k)
# len(s)        __len__(s)          The number of rows in the table
#               append(v)
#               index(v)
#               count(v)
#               keys()              List of keys (not necessarily unique)
#               values()            List of values (do.)
#               items()             List of (key, value) (do.)
#               iteritems()         Iterator over items (do.)
#               iterkeys()          Iterator over keys (do.)
# for k in s    __iter__()          Iterator over keys (do.)
#               itervalues()        Iterator over values (do.)
#               min(s)              The smallest key in the table
#               max(s)              The largest key in the table
#               get(k[, x])         Variant on __getitem__ with default value
#               clear()             DELETE FROM table
#               setdefault(k[, x])  Variant on __getitem__ which sets default value
#
# Not implemented yet:
#
# From "Mapping Types"
# <http://www.python.org/doc/2.2/lib/typesmapping.html>:
#
#               copy()              Create an anonymous temporary table?
#               update(t)           INSERT INTO table SELECT * FROM table?
#
# s + t?
# s * n, n * s?
#               popitem()
#
#
# NOTES
#
# 2. Is it possible to do any type checking?  Need to know correspondence
#    between SQL and Python types.  Perhaps DB-API spec v2.0 has something?
#
# 3. What about NULL column values?
#

import string
import types


class db_table_dict:

    # __init__ -- Initialize a new dictionary emulation
    #
    # The "name" argument is a string which is the name of the SQL table which
    # the emulation should access.  @@@@ What about funny names?  Quote?
    #
    # The "connection" argument is a "connection" object from a DB-API spec
    # v2.0 compliant database interface (see
    # <http://www.python.org/peps/pep-0249.html>).
    #
    # The "keys" and "values" arguments are pairs or lists of pairs.  Each pair
    # is (column, type) where column and type are strings.  The column is the
    # name of a column in the SQL table, and the type is its SQL type, as
    # would be specified to "CREATE TABLE" for that column.
    #
    # If the "keys" argument is a pair, then the keys of the dictionary will
    # be single values which are the value of the corresponding column in the
    # SQL table.  Similarly, if the "values" argument is a pair, then the
    # values in the dictionary will be single values.
    #
    # If the "keys" argument is a list of pairs, then the keys of the
    # dictionary will be tuples whose values are those of the columns in the
    # list, in order.  Similarly, if the "values" argument is a list of pairs,
    # then the values in the table will also be tuples.
    #
    # If the optional "create" keyword argument is true then attempt to create
    # a table described by the "name", "keys", and "values" arguments, with
    # the columns in "keys" as the primary key.
    #
    # The emulation does not insist that you specify _all_ the columns in the
    # table.  Read the comments on the various operations carefully to
    # understand what will happen if you don't.
    #
    # The emulation does not insist that the columns specified in the "keys"
    # argument are really the primary keys of the table, either.  Again,
    # read the comments to understand what will happen.

    def __init__(self, connection, name, keys, values, create = 0):

        self.connection = connection

        def quote_ident(string):
            return '"' + string.replace('"', '""') + '"'

        def quote_idents(list):
            # This may not be enough if the column name contains non-printing
            # characters.  Heaven forbid!
            return map(lambda(name, type): (quote_ident(name), type), list)

        name = quote_ident(name)
        self.table_name = name

        if isinstance(keys, types.ListType):
            self.single_key = 0
        elif isinstance(keys, types.TupleType):
            keys = [keys]
            self.single_key = 1
        keys = quote_idents(keys)
        self.key_columns = keys
            
        if isinstance(values, types.ListType):
            self.single_value = 0
        elif isinstance(values, types.TupleType):
            values = [values]
            self.single_value = 1
        values = quote_idents(values)
        self.value_columns = values

        self.create_query = (
            "CREATE TABLE " + self.table_name + " (" +
            string.join([
                "%s %s NOT NULL" % (name, type)
                for (name, type) in keys
            ], ", ") +
            ", PRIMARY KEY (" +
            string.join([name for (name, type) in keys], ", ") +
            "), " +
            string.join([
                "%s %s NOT NULL" % (name, type)
                for (name, type) in values
            ], ", ") +
           ");"
        )

        self.get_query = (
            "SELECT " +
            string.join([name for (name, type) in values], ", ") +
            " FROM " + self.table_name +
            " WHERE " +
            string.join([name + " = %s" for (name, type) in keys], " and ") +
            " LIMIT 1;" # @@@@ Should only be one?
        )

        self.insert_query = (
            "INSERT INTO " + self.table_name + " (" +
            string.join([name for (name, type) in keys + values], 
                        ", ") +
            ") VALUES (" +
            string.join(["%s" for (name, type) in keys + values],
                        ", ") +
            ");"
        )

        self.update_query = (
            "UPDATE " + self.table_name + " SET " +
            string.join([name + " = %s" for (name, type) in keys + values],
                        ", ") +
            " WHERE " +
            string.join([name + " = %s" for (name, type) in keys], " AND ") +
            ";"
        )

        self.delete_query = (
            "DELETE FROM " + self.table_name +
            " WHERE " +
            string.join([name + " = %s" for (name, type) in keys], " AND ") +
            ";"
        )            

        self.keys_query = (
            "SELECT " +
            string.join([name for (name, type) in keys], ", ") +
            " FROM " + self.table_name + ";"
        )

        self.values_query = (
            "SELECT " +
            string.join([name for (name, type) in values], ", ") +
            " FROM " + self.table_name + ";"
        )

        self.items_query = (
            "SELECT " +
            string.join([name for (name, type) in keys + values], ", ") +
            " FROM " + self.table_name + ";"
        )

        self.append_query = (
            "INSERT INTO " + self.table_name + " (" +
            string.join([name for (name, type) in values], 
                        ", ") +
            ") VALUES (" +
            string.join(["%s" for (name, type) in values],
                        ", ") +
            ");"
        )

        self.index_query = (
            "SELECT " +
            string.join([name for (name, type) in keys], ", ") +
            " FROM " + self.table_name +
            " WHERE " +
            string.join([name + " = %s" for (name, type) in values], " and ") +
            " ORDER BY " +
            string.join([name for (name, type) in keys], ", ") +
            " LIMIT 1;"
        )

        self.count_query = (
            "SELECT count(*) FROM " + self.table_name +
            " WHERE " +
            string.join([name + " = %s" for (name, type) in values], " and ") +
            ";"
        )

        self.len_query = "SELECT count(*) FROM " + self.table_name + ";"

        self.min_query = (
            "SELECT " +
            string.join([name for (name, type) in keys], ", ") +
            " FROM " + self.table_name +
            " ORDER BY " +
            string.join([name for (name, type) in keys], ", ") +
            " LIMIT 1;"
        )

        self.max_query = (
            "SELECT " +
            string.join([name for (name, type) in keys], ", ") +
            " FROM " + self.table_name +
            " ORDER BY " +
            string.join([name + " DESC" for (name, type) in keys], ", ") +
            " LIMIT 1;"
        )

        self.clear_query = "DELETE FROM " + self.table_name + ";"

        if create:
            cursor = self.connection.cursor()
            try:
                cursor.execute(self.create_query)
            except:
                self.connection.rollback()
                raise
            self.connection.commit()


    # check_key -- Check the types and layout of a key argument

    def check_key(self, key):
        if not isinstance(key, types.TupleType): raise IndexError, key
        if not len(key) == len(self.key_columns): raise IndexError, key
        # @@@@ Can't check types of keys?


    # check_value -- Check the types and layout of a value argument

    def check_value(self, value):
        if not isinstance(value, types.TupleType): raise ValueError, value
        if not len(value) == len(self.value_columns): raise ValueError, value
        # @@@@ Can't check types of values?


    # get_row -- Get a single row matching a key from the table

    def get_row(self, key):
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.get_query, key)
        except:
            self.connection.rollback()
            raise
        row = cursor.fetchone()
        if row != None:
            if self.single_value:
                return row[0]
            else:
                return tuple(row)
        return None


    # __len__ -- Return the number of rows in the table
    #
    # This is the implementation of len(s).
    # See <http://www.python.org/doc/2.2/ref/sequence-types.html>.

    def __len__(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.len_query)
        except:
            self.connection.rollback()
            raise
        row = cursor.fetchone()
        return int(row[0])


    # __getitem__ -- look up a value in the table
    #
    # The is the implementation of s[k].
    #
    # This only returns values from a random row where the key fields match
    # k, but if k was initialized to be a true key field then there should
    # only be one such row, by definition, and so the behaviour will be
    # more dictionary-like.

    def __getitem__(self, key):
        if self.single_key: key = (key,)
        self.check_key(key)
        row = self.get_row(key)
        if row == None: raise KeyError, key
        return row


    # get -- variant on __getitem__ with a default value
    #
    # I don't like the fact that the optional argument is called "x" but
    # that's what says at
    # <http://www.python.org/doc/2.2/lib/typesmapping.html>.

    def get(self, key, x = None):
        if self.single_key: key = (key,)
        if self.single_value:
            value = (x,)
        else:
            value = x
        self.check_key(key)
        self.check_value(value)
        row = self.get_row(key)
        if row == None: return x
        return row


    # setdefault -- variant on get which sets value if absent
    #
    # Unlike the specification at
    # <http://www.python.org/doc/2.2/lib/typesmapping.html>, the "x" argument
    # is not optional.  We can't set values to None in this implementation.
    #
    # A row will be added which maps the keys if one isn't found.
    #
    # We could just call __setitem__ but that would involve looking up the
    # row _again_, so we add it here.

    def setdefault(self, key, x):
        if self.single_key: key = (key,)
        if self.single_value:
            value = (x,)
        else:
            value = x
        self.check_key(key)
        self.check_value(value)
        row = self.get_row(key)
        if row == None:
            cursor = self.connection.cursor()
            try:
                cursor.execute(self.insert_query, key + value)
            except:
                self.connection.rollback()
                raise
            self.connection.commit()
            return x
        return row


    # __setitem__ -- insert or update row(s)
    #
    # This is the implementation of s[k] = v.
    #
    # If there is no row where the key fields match k, then insert a new row
    # using k and v.  Otherwise, update existing rows where the key fields
    # match k with values from v.  If k was initialized with a true key field
    # then there should only be one such row, by definition.
    #
    # If there are columns in the table other than those specified to __init__
    # then they will get their default values if a new row is inserted, and
    # be unaffected by updating.
    #
    # @@@@ Could this be more efficient by doing the update, then checking to
    # see if any rows were updated?  Can do it in PostgreSQL but not sure it's
    # portable.

    def __setitem__(self, key, value):
        if self.single_key: key = (key,)
        if self.single_value: value = (value,)
        self.check_key(key)
        self.check_value(value)
        row = self.get_row(key)
        cursor = self.connection.cursor()
        if row == None:
            try:
                cursor.execute(self.insert_query, key + value)
            except:
                self.connection.rollback()
                raise
            self.connection.commit()
        elif row != value:
            try:
                cursor.execute(self.update_query, key + value + key)
            except:
                self.connection.rollback()
                raise
            self.connection.commit()


    # __delitem__ -- delete rows matching key from the table
    #
    # This is the implementation of del s[k].
    #
    # All rows matching the key will be deleted.  If k was initialized with
    # a true key field then there will be at most one such row.
    
    def __delitem__(self, key):
        if self.single_key: key = (key,)
        self.check_key(key)
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.delete_query, key)
        except:
            self.connection.rollback()
            raise
        self.connection.commit()


    # has_key -- test whether any rows have key fields matching a key
    #
    # This is the implementation of k in s.
    #
    # Returns true iff there are some rows in the table whose key fields
    # match k.

    def has_key(self, key):
        if self.single_key: key = (key,)
        self.check_key(key)
        row = self.get_row(key)
        return row != None

    __contains__ = has_key


    # iterkeys -- return an iterator over all the keys in the table
    #
    # The is the implementation of for k in s.
    #
    # Returns an iterator object which will iterate over all the rows
    # in the table, returning the key fields for each row.  If k was
    # initialized with a true key field then each value will be unique.
    # 
    # See <http://www.python.org/doc/2.2/lib/typeiter.html> for a description
    # of iterator objects.

    def iterkeys(self):

        class db_table_iterkeys:

            def __init__(self, cursor, single_key):
                self.cursor = cursor
                self.single_key = single_key

            def __iter__(self): return self

            def next(self):
                row = self.cursor.fetchone()
                if row != None:
                    if self.single_key:
                        return row[0]
                    else:
                        return tuple(row)
                else:
                    raise StopIteration

        cursor = self.connection.cursor()
        cursor.execute(self.keys_query)
        return db_table_iterkeys(cursor, self.single_key)

    __iter__ = iterkeys

    
    # keys -- return a list of all the keys
    #
    # Be careful -- this function will extract every key from the table into
    # memory.
    
    def keys(self):
        list = []
        for key in self.iterkeys():
            list.append(key)
        return list


    # itervalues -- return an iterator over all the values in the table
    #
    # Returns an iterator object which will iterate over all the rows
    # in the table, returning the value fields for each row.  There is
    # no guarantee of uniqueness.
    # 
    # See <http://www.python.org/doc/2.2/lib/typeiter.html> for a description
    # of iterator objects.

    def itervalues(self):

        class db_table_itervalues:

            def __init__(self, cursor, single_value):
                self.cursor = cursor
                self.single_value = single_value

            def __iter__(self): return self

            def next(self):
                row = self.cursor.fetchone()
                if row != None:
                    if self.single_value:
                        return row[0]
                    else:
                        return tuple(row)
                else:
                    raise StopIteration

        cursor = self.connection.cursor()
        cursor.execute(self.values_query)
        return db_table_itervalues(cursor, self.single_value)

    
    # values -- return a list of all the values
    #
    # Be careful -- this function will extract every value from the table into
    # memory.
    
    def values(self):
        list = []
        for value in self.itervalues():
            list.append(value)
        return list


    # iteritems -- return an iterator over all the items in the table
    #
    # Returns an iterator object which will iterate over all the rows
    # in the table, returning pairs of the keys and values for each row.
    # There is no guarantee of uniqueness.
    # 
    # See <http://www.python.org/doc/2.2/lib/typeiter.html> for a description
    # of iterator objects.

    def iteritems(self):

        class db_table_iteritems:

            def __init__(self,
                         cursor,
                         single_key,
                         nr_keys,
                         single_value,
                         nr_values):
                self.cursor = cursor
                self.single_key = single_key
                self.nr_keys = nr_keys
                self.single_value = single_value
                self.nr_values = nr_values

            def __iter__(self): return self

            def next(self):
                row = self.cursor.fetchone()
                if row != None:
                    if self.single_key:
                        key = row[0]
                    else:
                        key = tuple(row[0 : self.nr_keys])
                    if self.single_value:
                        value = row[self.nr_keys]
                    else:
                        value = tuple(row[self.nr_keys : self.nr_keys + self.nr_values])
                    return (key, value)
                else:
                    raise StopIteration

        cursor = self.connection.cursor()
        cursor.execute(self.items_query)
        return db_table_iteritems(cursor,
                                  self.single_key,
                                  len(self.key_columns),
                                  self.single_value,
                                  len(self.value_columns))

    
    # items -- return a list of all the items
    #
    # Be careful -- this function will extract every item from the table into
    # memory.
    
    def items(self):
        list = []
        for item in self.iteritems():
            list.append(item)
        return list


    # append -- add a row to the table with default key columns
    #
    # This assumes that the key fields will be filled in automatically, so
    # this is pretty much only useful when the key field is a "serial" or the
    # table is just a bag and the key field is the "oid".
    # See <http://www.python.org/doc/2.2/lib/typesseq-mutable.html>.

    def append(self, value):
        if self.single_value: value = (value,)
        self.check_value(value)
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.append_query, value)
        except:
            self.connection.rollback()
            raise
        self.connection.commit()


    # index -- find smallest key for a value
    #
    # Returns smallest key such that table[key] = value or raise ValueError
    # See <http://www.python.org/doc/2.2/lib/typesseq-mutable.html>.
    #
    # The "smallest" key is as chosen by SQL "ORDER BY" and not necessarily
    # the same as Python's idea of "smallest".

    def index(self, value):
        if self.single_value: value = (value,)
        self.check_value(value)
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.index_query, value)
        except:
            self.connection.rollback()
            raise
        row = cursor.fetchone()
        if row != None:
            if self.single_key:
                return row[0]
            else:
                return tuple(row)
        else:
            raise ValueError, value


    # count -- count rows with a key
    #
    # Return the number of keys for which table[key] = value
    # See <http://www.python.org/doc/2.2/lib/typesseq-mutable.html>.
    #
    # This will always be 0 or 1 if k was initialized as a true key field,
    # but might be larger otherwise.

    def count(self, value):
        if self.single_value: value = (value,)
        self.check_value(value)
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.count_query, value)
        except:
            self.connection.rollback()
            raise
        row = cursor.fetchone()
        return row[0]


    # min, max -- return the smallest, largest key in the table
    #
    # Note that "smallest" and "largest" are determined by SQL "ORDER BY" and
    # may not correspond with Python's idea of ordering.  If there are more
    # than one key column, the first is most significant in the ordering.
    #
    # @@@@ Too much common code, both here and elsewhere.  Tidy up!
    
    def min(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.min_query)
        except:
            self.conenction.rollback()
            raise
        row = cursor.fetchone()
        if self.single_key:
            return row[0]
        else:
            return tuple(row)

    def max(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.max_query)
        except:
            self.conenction.rollback()
            raise
        row = cursor.fetchone()
        if self.single_key:
            return row[0]
        else:
            return tuple(row)


    # clear -- delete all rows from the table
    #
    # Be careful!  Are you sure you want to do this?  Really?
    
    def clear(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(self.clear_query)
        except:
            self.conenction.rollback()
            raise
        

# A. REFERENCES
#
# [vanRossum 2002-03-29] "Python Reference Manual (release 2.2p1)"; Guido van
# Rossum, Fred L. Drake, Jr. (editor); PythonLabs; 2002-03-29;
# <http://www.python.org/doc/2.2p1/ref/ref.html>.
#
# [PEP 249] "Python Database API Specification v2.0"; Marc-Andre Lemburg
# <mal@lemburg.com>; Python Database SIG <db-sig at python.org>; 1999-04-07;
# <http://www.python.org/peps/pep-0249.html>.
#
# B. DOCUMENT HISTORY
#
# 2004-01-22  RB  Created in the train from London to Cambridge.
#
# 2004-01-23  RB  Documented.
#
# 2004-02-12  RB  Extended to allow a single key or value to be specified on
#                 initialization, in which case the keys and values are also
#                 single values, not tuples.  Added "append" and "index"
#                 methods with semantics a subset of those described in
#                 <http://www.python.org/doc/2.2/lib/typesseq-mutable.html>.
#
# 2004-02-13  RB  Implemented almost everything a container, sequence, and
#                 dictionary emulation should have according to the Python
#                 reference and library reference manuals.
#
#
# C. COPYRIGHT AND LICENCE
#
# Copyright 2004 Ravenbrook Limited <http://www.ravenbrook.com/>.
#
#
# $Id$
