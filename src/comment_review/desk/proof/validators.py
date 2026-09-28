"""The rule checks a proof's parsers are handed, one per record kind.

`decision-log.md Process: #203` and `#204`: each record is read by its own
`deserialize` and held to the rules of its table by a validator its parser is
handed, so nothing in `desk/proof` imports the tables. The three travel as
one bundle; `flows.validators.VALIDATORS` is the one built from the tables.
"""

from dataclasses import dataclass

from comment_review.desk.proof.answer import AnswerValidator
from comment_review.desk.proof.disposition import DispositionValidator
from comment_review.desk.proof.mark import Validator


@dataclass(frozen=True)
class Validators:
    """The three rule checks, each handed to the reader of its own record.

    Attributes:
        mark: a mark against its instruction's row -- `read_mark`'s.
        answer: an answer against its question's row -- `read_answer`'s.
        disposition: a chief's ruling against its row -- `read_disposition`'s.
    """

    mark: Validator
    answer: AnswerValidator
    disposition: DispositionValidator
