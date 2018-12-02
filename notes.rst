===========
GUMDB NOTES
===========


Duplicates
----------

1. Content duplicates are determined by message digests.  We use the
   Pyzor message hasher (used to detect spam) and also mix in the
   message-id headers.  These may exist in more than one source.
