#!/usr/bin/env python
# import.py -- import a message to the e-mail database

import sys
import tables
import email
import time
from warnings import warn

Error = 'Error'

# import_message -- attempt to import one mail message
def import_message():
    message_text = sys.stdin.read()
    
    message = email.message_from_string(message_text)

    # Note: For somed reason, message.__getitem__ never raises KeyError but
    # returns None instead, according to the Python 2.3 docs.  Tsk!
    message_id = message['message-id']
    if message_id == None:
        # If the message doens't have a message-id then make one up.
        message_id = email.Utils.make_msgid('gumdb')
        warn('Message has no Message-Id; using %s' % repr(message_id))

    envelope_from = message.get_unixfrom()

    # If the message has already been imported, check that it's in fact the
    # same, and raise an error if not.  Otherwise ignore it.
    if message_id in tables.messages:
        try:
            if message_text == tables.message_texts[message_id]:
                return
        except KeyError:
            pass
        raise Error, ('Different message in database with same Message-Id %s' %
                      repr(message_id))

    # Attempt to parse the date field and convert it to UTC
    iso_date = None
    iso_time = None
    date_field = message['date']
    if date_field == None:
        warn('Message has no Date field')
    else:
        tuple = email.Utils.parsedate_tz(message['date'])
        if tuple == None:
            warn('Unable to parse date field %s' % repr(date_field))
        else:
            stamp = email.Utils.mktime_tz(tuple)
            iso_date = time.strftime('%Y-%m-%d', time.gmtime(stamp))
            iso_time = time.strftime('%H:%M:%S', time.gmtime(stamp))
    
    tables.messages[message_id] = (envelope_from, iso_date, iso_time)
    tables.message_texts[message_id] = message_text

    # Extract all the headers and put them in the headers table    
    index = 0
    for (name, value) in message.items():
        tables.message_headers[(message_id, index)] = (name.lower(), value)
        index += 1

    # Extract all the recipients and put them in the recipients table
    index = 0
    for type in ['to', 'cc', 'bcc', 'from', 'sender']:
        for (name, address) in email.Utils.getaddresses(message.get_all(type, [])):
            # Use None if the recipient doesn't have a name, rather than the empty
            # string.  (Sadly, getaddresses doesn't distinguish between these cases.)
            if name == '': name = None
            tables.message_recipients[(message_id, index)] = (type, name, address)
            index += 1

# Main -- import one message and commit iff successful
def main():
    try:
        import_message()
    except:
        tables.connection.rollback()
        raise
    tables.connection.commit()


# Invocation boilerplate
#
# This is a standard sight in Python programs.  If this file is invoked
# as a Python program, run "main", otherwise just define the variables
# and functions.  This allows this file to be imported as a module as
# well as run as a program.

if __name__ == '__main__':
    main()


# A. REFERENCES
#
#
# B. DOCUMENT HISTORY
#
# 2004-02-18  RB  Created.
#
#
# $Id$
