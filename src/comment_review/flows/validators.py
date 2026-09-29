"""The rule checks every parse of a copy or a proof is handed, built once.

`desk.proof.validators.Validators` is the bundle; this is the one built from
the answers' and the rulings' tables, so a flow or a command reading a copy, a
proof, an answer or a ruling hands the same checks to every record it reads.
"""

from comment_review.desk.answers import rules as answer_rules
from comment_review.desk.dispositions import rules as disposition_rules
from comment_review.desk.proof.validators import Validators

VALIDATORS = Validators(
    answer=answer_rules.validate,
    disposition=disposition_rules.validate,
)
