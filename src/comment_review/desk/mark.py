"""Shim: `desk.mark` moved to `desk.marks`. Deleted when the old readers go."""

from comment_review.desk.marks.mark import *  # noqa: F401,F403
from comment_review.desk.marks.mark import (  # noqa: F401
    ROLE_FIELDS,
    Instruction,
    Mark,
    Shape,
    derived_change,
    filled,
    text_at,
    untouched,
)
from comment_review.desk.marks.table import INSTRUCTIONS, Row  # noqa: F401
