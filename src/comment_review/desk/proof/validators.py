"""The rule checks a proof's parsers are handed, one per record kind.

A ruling is read by its own `deserialize` and held to the rules of its
table by a validator its parser is handed, so nothing in `desk/proof` imports
the tables. A mark and an answer are each read into their own type, which
checks itself, so no validator is handed for either. The checks travel as one
bundle; `flows.validators.VALIDATORS` is the one built from the tables.
"""

from dataclasses import dataclass

from comment_review.desk.proof.disposition import DispositionValidator


@dataclass(frozen=True)
class Validators:
    """The rule checks, each handed to the reader of its own record.

    Attributes:
        disposition: a chief's ruling against its row -- `read_disposition`'s.
    """

    disposition: DispositionValidator
