-- tables.sql
--
-- $Id$

DROP TABLE messages CASCADE;
DROP TABLE message_texts CASCADE;
DROP TABLE message_headers CASCADE;
DROP TABLE message_recipients CASCADE;


-- messages -- basic table of messages
--
-- This is the table of messages that exist in the database and information
-- about them.
--
-- The columns are:
--
--   message_id     A globally unique identifier for the message.
--                  The Message-Id header is used if possible.
--
--   envelope_from  The mailbox envelope from field, if available.
--
--   date, time     The date and time from the "Date" header, if it existed
--                  and could be parsed, converted to UTC.

CREATE TABLE messages (
    message_id text PRIMARY KEY,    -- from Message-Id header
    envelope_from text,             -- mailbox envelope from
    "date" date,                    -- from Date header, UTC
    "time" time                     -- from Date header, UTC
);


-- message_texts -- the original text of messages
--
-- This table contains the original unprocessed text of the e-mail messages,
-- as it was imported into the database.  All other information in the
-- database is derived from this, and can be re-created from it if necessary.
--
-- @@@@ Should be using BLOBs?

CREATE TABLE message_texts (
    message_id text PRIMARY KEY REFERENCES messages ON DELETE CASCADE,
    message_text text NOT NULL
);


-- message_headers -- contents of message headers
--
-- This table contains the headers of each message, indexed by their position
-- in the message (0, 1, 2, ...).  The header name is converted to lower case
-- on import.  The header value is not processed further, and may contain
-- line breaks.

CREATE TABLE message_headers (
    message_id text REFERENCES messages ON DELETE CASCADE,
    header_index int NOT NULL,
    PRIMARY KEY (message_id, header_index),
    header_name text NOT NULL,
    header_value text NOT NULL
);


-- message_recipients -- parsed recipient fields
--
-- This table contains the recipients of each message, indexed in the order
-- that they appeared in the "to", "cc", and "bcc" headers, respectively.

CREATE TABLE message_recipients (
    message_id text REFERENCES messages ON DELETE CASCADE,
    recipient_index int NOT NULL,
    PRIMARY KEY (message_id, recipient_index),
    recipient_type text NOT NULL, -- 'to', 'cc', or 'bcc'
    recipient_name text,
    recipient_address text NOT NULL
);
