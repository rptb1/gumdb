#! /usr/bin/env python
#
# $Id$
#

import sys
from pyPgSQL import PgSQL
db = PgSQL
from db_table_dict import db_table_dict

connection = db.connect('::mail')

messages = db_table_dict(connection,
                         "messages",
                         ("message_id", "serial"),
                         ("message_text", "text"))

message_text = sys.stdin.read()

messages.append(message_text)
