#! /usr/bin/env python
#
# $Id$
#

import mailbox
import rfc822
import time

print

fp = open("mbox", "r")
mb = mailbox.UnixMailbox(fp)
while 1:
	msg = mb.next()
	if msg == None:
		break
	date = msg.getdate_tz("Date")
	if date:
		print time.strftime("%Y-%m-%d %H:%M:%S", date[0:9])
		print date[9]
		seconds = time.mktime(date[0:9])
		seconds = seconds - date[9]
		print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))
		# If the local timezone changes between the call to mktime and the call to localtime then we'll get the wrong answer.  There's no timegm in Python 1.5.2!  RB 2000-10-07
