-- tables.sql
--
-- $Id$

DROP TABLE messages CASCADE;
DROP TABLE message_texts CASCADE;
DROP TABLE message_headers CASCADE;
DROP TABLE message_recipients CASCADE;

CREATE TABLE messages (
    message_id text PRIMARY KEY,
    envelope_from text,
    "date" date,
    "time" time
);

CREATE TABLE message_texts (
    message_id text PRIMARY KEY REFERENCES messages,
    message_text text
);

CREATE TABLE message_headers (
    message_id text REFERENCES messages,
    header_index int NOT NULL,
    PRIMARY KEY (message_id, header_index),
    header_name text NOT NULL,
    header_value text NOT NULL
);

CREATE TABLE message_recipients (
    message_id text REFERENCES messages,
    recipient_index int NOT NULL,
    PRIMARY KEY (message_id, recipient_index),
    recipient_type text NOT NULL, -- 'to', 'cc', or 'bcc'
    recipient_name text NOT NULL,
    recipient_address text NOT NULL
);
