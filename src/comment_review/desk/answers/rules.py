"""The rules an answer is held to, read off its row in the answers table.

    validate()   one answer against its row -- every broken rule, named

The answer itself -- its fields and its structural read -- is
`desk.proof.answer`, and `read_answer` applies this after that read
(`decision-log.md Process: #203`).
"""

from comment_review.desk.answers.table import ANSWERS
from comment_review.desk.proof.answer import Answer
from comment_review.desk.proof.mark import filled


def validate(where: str, answer: Answer) -> list[str]:
    """Every rule `answer`'s row states that the answer breaks.

    A rule asks only of a field the row takes; a field the row does not take is
    never refused (`decision-log.md Process: #204`).

    Args:
        where: how to name this answer in a message -- its address.
        answer: the entry as `Answer.deserialize` read it, a field of the wrong
            type already read as absent.

    Returns:
        One message per broken rule; empty for an answer that keeps its row.
        An answer its question does not take is one message, and nothing else
        is asked of it.
    """
    name = answer.name
    question = answer.question
    row = ANSWERS.get((question, name))
    if row is None:
        article = "an" if str(question)[:1] in "aeiou" else "a"
        return [f"{where}: {name!r} is not an answer to {article} {question}"]
    out = []
    if not filled(answer.address):
        out.append(f"{where}: {name} needs the `address`")
    if not filled(answer.reason):
        out.append(f"{where}: {name} needs a `reason`")
    if row.owes_change and not filled(answer.change):
        out.append(f"{where}: {name} needs a `change`")
    # Every key the row's own `effect` reads. A `query` whose `claim.shape`
    # is missing used to fall through to the deferring branch, which is
    # the difference between a place held for a person and one nobody is
    # waiting on -- so the absence is refused where the answer is read.
    out += [
        f"{where}: {name} needs `claim.{key}`"
        for key in row.claim_all
        if not filled(answer.claim.get(key))
    ]
    return out
