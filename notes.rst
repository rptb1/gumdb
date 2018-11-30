===========
GUMDB NOTES
===========


Database Integrity
------------------

SQLite doesn't have constraints by default (but see
<https://sqlite.org/foreignkeys.html>), so we work with faily loose
integrity.  This means that queries should not assume that, for
example, if a header exists for an id, then the message also exists.
We might clean those things up lazily.  So avoid::

  SELECT *
  FROM headers LEFT JOIN messages USING (id)
  WHERE ...

because this might yield a result with a header but no messsage.
Instead, use inner joins::

  SELECT *
  FROM headers JOIN messages USING (id)
  WHERE ...

as this will ignore headers without messages.  Cleaning up other
tables can be done like::

  SELECT * FROM dates WHERE id NOT IN (SELECT id FROM messages)


Duplicates
----------

1. Content duplicates are determined by message digests.  We use the
   Pyzor message hasher (used to detect spam) and also mix in the
   message-id headers.  These may exist in more than one source.

2. Source duplicates are a subset of the above where the same message
   is added twice from the same file (with the same modification
   time).  These can just be deleted.

   These can be found with::
     
     SELECT * FROM sources GROUP BY type, file, key, mtime HAVING count(*) > 1;
