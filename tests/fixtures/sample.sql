-- fx.sql -- one small schema.

/* SQL has no docstring practice, so the row declares no `declares`
   list and no `a` series is minted for this file. */

CREATE TABLE reading (
    id      INTEGER PRIMARY KEY,
    folio   TEXT NOT NULL,  -- a trailing comment
    anchor  TEXT NOT NULL
);

CREATE INDEX reading_folio ON reading (folio);

INSERT INTO reading VALUES (1, 'http://example.com/not-a-comment', 'x');
