#! /usr/bin/env python
#
# $Id$
#

import sys
from pyPgSQL import PgSQL
db = PgSQL
from db_table_dict import db_table_dict
import email
import time

error = "Error"

connection = db.connect('::mail')

messages = db_table_dict(connection,
                         "messages",
                         ("message_id", "text"),
                         [("envelope_from", "text"),
                          ("date", "date"),
                          ("time", "time")])

message_texts = db_table_dict(connection,
                              "message_texts",
                              ("message_id", "text"),
                              ("message_text", "text"))

message_headers = db_table_dict(connection,
                                "message_headers",
                                [("message_id", "text"),
                                 ("header_index", "int")],
                                [("header_name", "text"),
                                 ("header_value", "text")])

message_recipients = db_table_dict(connection,
                                   "message_recipients",
                                   [("message_id", "text"),
                                    ("recipient_index", "int")],
                                   [("recipient_type", "text"),
                                    ("recipient_name", "text"),
                                    ("recipient_address", "text")])

message_text = sys.stdin.read()

message = email.message_from_string(message_text)

# Need to decide what to do if any of these fields don't exist or can't
# be parsed.
message_id = message["message-id"]
envelope_from = message.get_unixfrom()
stamp = email.Utils.mktime_tz(email.Utils.parsedate_tz(message["date"]))
iso_date = time.strftime("%Y-%m-%d", time.gmtime(stamp))
iso_time = time.strftime("%H:%M:%S", time.gmtime(stamp))

if message_id in messages:
    raise error, "Duplicate message with id %s" % repr(message_id)

messages[message_id] = (envelope_from, iso_date, iso_time)
message_texts[message_id] = message_text

index = 0
for (name, value) in message.items():
    message_headers[(message_id, index)] = (name.lower(), value)
    index += 1

index = 0
for type in ['to', 'cc', 'bcc']:
    for (name, address) in email.Utils.getaddresses(message.get_all(type, [])):
        message_recipients[(message_id, index)] = (type, name, address)
        index += 1
