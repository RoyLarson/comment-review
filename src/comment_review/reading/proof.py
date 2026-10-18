"""What a reader's record answers when a proof asks whether code survived.

Every reader returns a record of the file it read, and the record compares
itself with a second read of the same file. A proof asks that question of the
page's `read` and never of the language: `PythonRead` compares lexical source
structure, and `StrippedRead` compares the source with its comments removed.
"""

from collections.abc import Collection
from dataclasses import dataclass
from typing import Protocol, Self

from comment_review.reading.diagnostics import ReadDiagnostic

#: The diagnostic code a read reports when it cannot separate prose from code,
#: so sameness is neither shown nor refuted.
UNPROVABLE = "unprovable"

#: The diagnostic code a read reports when an approved docstring's anchor names
#: no single declaration on both sides.
UNIDENTIFIED_OWNER = "unidentified-documentation-owner"


@dataclass(frozen=True)
class PreservationResult:
    """A preservation decision with diagnostics only when source changed."""

    unchanged: bool
    diagnostics: tuple[ReadDiagnostic, ...]

    def __post_init__(self) -> None:
        """Require a Boolean decision and the corresponding diagnostic presence."""
        if not isinstance(self.unchanged, bool):
            raise ValueError("unchanged must be a bool")
        if not isinstance(self.diagnostics, tuple) or any(
            not isinstance(item, ReadDiagnostic) for item in self.diagnostics
        ):
            raise ValueError("diagnostics must be a tuple of ReadDiagnostic")
        if self.unchanged == bool(self.diagnostics):
            raise ValueError(
                "unchanged results have no diagnostics; changed results require them"
            )

    @property
    def unprovable(self) -> bool:
        """The comparison could not be made, as opposed to finding a change."""
        return any(d.code == UNPROVABLE for d in self.diagnostics)


class SourceRead(Protocol):
    """A reader's record of one file, able to compare itself with another read."""

    @property
    def proof(self) -> str:
        """The comparison's name, as a proof report prints it."""
        ...

    def preserved(
        self,
        after: Self,
        *,
        documented: Collection[tuple[int | None, int | None]] | None = None,
    ) -> PreservationResult:
        """Whether `after` holds this read's code unchanged.

        Args:
            after: a read of the same file, by the same reader.
            documented: the docstrings an approved alteration may add or remove,
                each as the anchor line of its declaration before and after, with
                None for the module. None allows every docstring to change.
        """
        ...
