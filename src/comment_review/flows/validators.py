"""The rule checks every parse of a copy or a proof is handed, built once.

`desk.proof.validators.Validators` is the bundle; this is the one built from
the rulings' table, so a flow or a command reading a proof or a ruling hands
the same check to every ruling it reads.
"""

from comment_review.desk.dispositions import rules as disposition_rules
from comment_review.desk.proof.validators import Validators

VALIDATORS = Validators(
    disposition=disposition_rules.validate,
)
