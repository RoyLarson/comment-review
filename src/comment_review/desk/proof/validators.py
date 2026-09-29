"""The rule checks a proof's parsers are handed, one per record kind.

An answer and a ruling are read by their own `deserialize` and held to the
rules of their table by a validator their parser is handed, so nothing in
`desk/proof` imports the tables. A mark is read into its own type, which
checks itself, so no validator is handed for it. The checks travel as one
bundle; `flows.validators.VALIDATORS` is the one built from the tables.
"""

from dataclasses import dataclass

from comment_review.desk.proof.answer import AnswerValidator
from comment_review.desk.proof.disposition import DispositionValidator


@dataclass(frozen=True)
class Validators:
    """The rule checks, each handed to the reader of its own record.

    Attributes:
        answer: an answer against its question's row -- `read_answer`'s.
        disposition: a chief's ruling against its row -- `read_disposition`'s.
    """

    answer: AnswerValidator
    disposition: DispositionValidator
