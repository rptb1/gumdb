-- views.sql
--
-- $Id$

DROP VIEW message_subjects CASCADE;
DROP VIEW message_froms CASCADE;

CREATE VIEW message_subjects AS
    SELECT messages.message_id, header_value AS subject
    FROM messages, message_headers
    WHERE message_headers.message_id = messages.message_id AND
          message_headers.header_name = 'subject';

CREATE VIEW message_froms AS
    SELECT messages.message_id, header_value AS "from"
    FROM messages, message_headers
    WHERE message_headers.message_id = messages.message_id AND
          message_headers.header_name = 'from';

CREATE VIEW summary AS
    SELECT date, time, "from", subject
    FROM messages
         NATURAL LEFT JOIN message_subjects
         NATURAL LEFT JOIN message_froms;
