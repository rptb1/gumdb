# tables.py -- interface to PostgreSQL tables
#
# $Id$
#
# 2004-02-18  RB  Created.

from pyPgSQL import PgSQL
db = PgSQL
from db_table_dict import db_table_dict

connection = db.connect('::mail')

messages = db_table_dict(connection,
                         "messages",
                         ("message_id", "text"),
                         [("envelope_from", "text"),
                          ("date", "date"),
                          ("time", "time")],
                         auto_commit = 0)

message_texts = db_table_dict(connection,
                              "message_texts",
                              ("message_id", "text"),
                              ("message_text", "text"),
                              auto_commit = 0)

message_headers = db_table_dict(connection,
                                "message_headers",
                                [("message_id", "text"),
                                 ("header_index", "int")],
                                [("header_name", "text"),
                                 ("header_value", "text")],
                                auto_commit = 0)

message_recipients = db_table_dict(connection,
                                   "message_recipients",
                                   [("message_id", "text"),
                                    ("recipient_index", "int")],
                                   [("recipient_type", "text"),
                                    ("recipient_name", "text"),
                                    ("recipient_address", "text")],
                                   auto_commit = 0)
